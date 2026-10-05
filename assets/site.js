(function () {
  var root = document.documentElement;
  var btn = document.getElementById('theme');
  function current() {
    return root.dataset.theme ||
      (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  function label() { if (btn) btn.textContent = current() === 'dark' ? 'Светлая' : 'Тёмная'; }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  label();
  if (btn) btn.addEventListener('click', function () {
    var t = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = t; save('theme', t); label();
  });
  function fs(delta) {
    var v = parseFloat(getComputedStyle(root).getPropertyValue('--fs')) || 19;
    v = Math.min(26, Math.max(15, v + delta));
    root.style.setProperty('--fs', v + 'px'); save('fs', v);
  }
  var up = document.getElementById('fs-up'), down = document.getElementById('fs-down');
  if (up) up.addEventListener('click', function () { fs(1); });
  if (down) down.addEventListener('click', function () { fs(-1); });
  // почта собирается на лету, чтобы её не подбирали автоматические сборщики адресов
  var m = document.querySelectorAll('[data-u][data-d]');
  for (var i = 0; i < m.length; i++) {
    var a = m[i].getAttribute('data-u') + '@' + m[i].getAttribute('data-d');
    m[i].innerHTML = '<a href="mailto:' + a + '">' + a + '</a>';
  }
})();
