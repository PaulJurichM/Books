#!/usr/bin/env python3
"""Собирает сайт из папки content/ в папку docs/ (её публикует GitHub Pages).

Новый рассказ: положить .md в папку сборника (номер в имени файла задаёт порядок)
и запустить  python3 build.py
"""
import html, os, re, shutil

SRC, OUT = "content", "docs"
AUTHOR = "Павел Юрич"
SITE = "Павел Юрич. Проза"


def read(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    m = re.match(r"---\n(.*?)\n---\n?(.*)", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body.strip()


def inline(text):
    """Экранирует текст; *так* помечается курсив."""
    return re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", html.escape(text))


def render(body):
    out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip("\n")
        if not block.strip():
            continue
        if block.startswith("## "):
            out.append(f"<h2>{html.escape(block[3:].strip())}</h2>")
        elif block.startswith(">"):
            # цитата: эпиграф, письмо, документ; пустая строка «>» делит абзацы
            text = "\n".join(re.sub(r"^>\s?", "", x) for x in block.split("\n"))
            paras = ["<p>" + "<br>\n".join(inline(x.strip()) for x in p.split("\n")) + "</p>"
                     for p in re.split(r"\n\s*\n", text) if p.strip()]
            out.append("<blockquote>" + "\n".join(paras) + "</blockquote>")
        elif "\n" in block:
            lines = "<br>\n".join(inline(x.strip()) for x in block.split("\n"))
            out.append(f'<p class="verse">{lines}</p>')
        else:
            out.append(f"<p>{inline(block.strip())}</p>")
    return "\n".join(out)


def minutes(body):
    return max(1, round(len(body.split()) / 180))


def page(title, content, root, crumbs=""):
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script>(function(){{try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t;var f=localStorage.getItem('fs');if(f)document.documentElement.style.setProperty('--fs',f+'px');}}catch(e){{}}}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{root}index.html">{AUTHOR}</a>
  <nav>
    <a href="{root}index.html">Сборники</a>
    <a href="{root}ekranizaciya.html">Экранизация</a>
    <button class="ctl" id="fs-down" type="button" aria-label="Уменьшить шрифт">A−</button>
    <button class="ctl" id="fs-up" type="button" aria-label="Увеличить шрифт">A+</button>
    <button class="ctl" id="theme" type="button" aria-label="Переключить тему">Тёмная</button>
  </nav>
</header>
<main>
{crumbs}
{content}
</main>
<footer>
  <p>© {AUTHOR}, 2026. Читать можно свободно. <a href="{root}ekranizaciya.html">Экранизация и права</a></p>
</footer>
<script src="{root}assets/site.js"></script>
</body>
</html>
"""


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    shutil.copytree("assets", f"{OUT}/assets")
    open(f"{OUT}/.nojekyll", "w").close()
    if os.path.exists("CNAME"):
        shutil.copy("CNAME", f"{OUT}/CNAME")

    cols = []
    for d in sorted(os.listdir(SRC)):
        p = os.path.join(SRC, d)
        if not os.path.isdir(p):
            continue
        cmeta, cbody = read(os.path.join(p, "_collection.md"))
        slug = re.sub(r"^\d+-", "", d)
        works = []
        for f in sorted(os.listdir(p)):
            if f.startswith("_") or not f.endswith(".md"):
                continue
            meta, body = read(os.path.join(p, f))
            wslug = re.sub(r"^\d+-", "", f[:-3])
            pic = next((f"images/{wslug}{e}" for e in (".jpg", ".png", ".webp")
                        if os.path.exists(os.path.join(p, "images", wslug + e))), "")
            works.append({"slug": wslug, "title": meta.get("title", f),
                          "body": body, "min": minutes(body), "pic": pic})
        img = os.path.join(p, "images")
        if os.path.isdir(img):
            shutil.copytree(img, f"{OUT}/{slug}/images")
        cols.append({"slug": slug, "title": cmeta.get("title", d), "about": cbody, "works": works})

    # главная
    parts = ['<section class="hero"><h1>Проза</h1>'
             '<p>Пять сборников детективной прозы. Читать можно бесплатно и без регистрации, '
             'с телефона или с большого экрана, при свете и в темноте.</p></section>']
    for c in cols:
        lis = "\n".join(
            f'<li><a href="{c["slug"]}/{w["slug"]}.html">{html.escape(w["title"])}</a>'
            f'<span class="min">{w["min"]} мин</span></li>' for w in c["works"])
        parts.append(
            f'<details class="col"><summary><span class="ct">{html.escape(c["title"])}</span>'
            f'<span class="cn">{len(c["works"])}</span></summary>'
            f'<ol>{lis}</ol>'
            f'<p class="more"><a href="{c["slug"]}/index.html">Открыть сборник отдельной страницей</a></p></details>')
    open(f"{OUT}/index.html", "w", encoding="utf-8").write(page(SITE, "\n".join(parts), ""))

    # сборники и рассказы
    for c in cols:
        os.makedirs(f"{OUT}/{c['slug']}", exist_ok=True)
        lis = "\n".join(
            f'<li><a href="{w["slug"]}.html">{html.escape(w["title"])}</a>'
            f'<span class="min">{w["min"]} мин</span></li>' for w in c["works"])
        about = render(c["about"]) if c["about"] else ""
        body = f'<h1>{html.escape(c["title"])}</h1>{about}<ol class="toc">{lis}</ol>'
        crumbs = '<p class="crumbs"><a href="../index.html">Все сборники</a></p>'
        open(f"{OUT}/{c['slug']}/index.html", "w", encoding="utf-8").write(
            page(f'{c["title"]} — {AUTHOR}', body, "../", crumbs))
        for i, w in enumerate(c["works"]):
            prev = c["works"][i - 1] if i else None
            nxt = c["works"][i + 1] if i + 1 < len(c["works"]) else None
            nav = '<nav class="pn">'
            nav += (f'<a class="prev" href="{prev["slug"]}.html"><small>Назад</small>{html.escape(prev["title"])}</a>'
                    if prev else '<span></span>')
            nav += (f'<a class="next" href="{nxt["slug"]}.html"><small>Дальше</small>{html.escape(nxt["title"])}</a>'
                    if nxt else f'<a class="next" href="index.html"><small>Конец сборника</small>К оглавлению</a>')
            nav += "</nav>"
            crumbs = (f'<p class="crumbs"><a href="../index.html">Все сборники</a> · '
                      f'<a href="index.html">{html.escape(c["title"])}</a></p>')
            body = (f'<article><h1>{html.escape(w["title"])}</h1>'
                    f'<p class="meta">{AUTHOR} · около {w["min"]} мин чтения</p>'
                    + (f'<figure><img src="{w["pic"]}" alt="Иллюстрация к рассказу «{html.escape(w["title"])}»" loading="lazy"></figure>'
                       if w["pic"] else "")
                    + f'{render(w["body"])}</article>{nav}')
            open(f"{OUT}/{c['slug']}/{w['slug']}.html", "w", encoding="utf-8").write(
                page(f'{w["title"]} — {AUTHOR}', body, "../", crumbs))

    # отдельные страницы
    for f in sorted(os.listdir("pages")):
        meta, body = read(os.path.join("pages", f))
        open(f"{OUT}/{f[:-3]}.html", "w", encoding="utf-8").write(
            page(f'{meta.get("title", "")} — {AUTHOR}',
                 f'<article class="plain"><h1>{html.escape(meta.get("title", ""))}</h1>{body}</article>', ""))

    n = sum(len(c["works"]) for c in cols)
    print(f"Готово: сборников {len(cols)}, произведений {n} → {OUT}/")


if __name__ == "__main__":
    main()
