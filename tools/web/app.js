(function () {
  'use strict';

  var TOKEN_KEY = 'mega_dashboard_token';
  var strip = document.querySelector('.status-strip');
  var form = document.getElementById('token-form');
  var input = document.getElementById('token-input');

  function getToken() {
    try { return sessionStorage.getItem(TOKEN_KEY) || ''; } catch (e) { return ''; }
  }

  function setToken(value) {
    try { sessionStorage.setItem(TOKEN_KEY, value); } catch (e) { /* ignora */ }
  }

  function makeBadge(text, cls) {
    var el = document.createElement('span');
    el.className = 'badge ' + cls;
    var dot = document.createElement('span');
    dot.className = 'dot';
    el.appendChild(dot);
    el.appendChild(document.createTextNode(' ' + text));
    return el;
  }

  function render(items) {
    if (!strip) return;
    while (strip.firstChild) strip.removeChild(strip.firstChild);
    items.forEach(function (item) { strip.appendChild(makeBadge(item.text, item.cls)); });
  }

  function refresh() {
    var token = getToken();
    if (!token) {
      render([{ text: 'Status: informe o token', cls: 'neutral' }]);
      return;
    }

    fetch('/api/health', { headers: { Authorization: 'Bearer ' + token }, cache: 'no-store' })
      .then(function (res) {
        if (res.status === 401) {
          render([{ text: 'Status: token invalido', cls: 'neutral' }]);
          return null;
        }
        if (!res.ok) throw new Error('http ' + res.status);
        return res.json();
      })
      .then(function (data) {
        if (!data) return;
        var mcp = data.mcp || {};
        render([
          { text: 'Dashboard: ' + String(data.status), cls: 'online' },
          { text: 'HexStrike: ' + String(mcp.hexstrike || 'unknown'), cls: 'neutral' },
          { text: 'CyberStrike: ' + String(mcp.cyberstrike || 'unknown'), cls: 'neutral' },
          { text: 'Modelo: ' + String(data.model || 'unknown'), cls: 'neutral' }
        ]);
      })
      .catch(function () {
        render([{ text: 'Status: offline', cls: 'neutral' }]);
      });
  }

  if (form && input) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var value = input.value.trim();
      if (value) setToken(value);
      input.value = '';
      refresh();
    });
  }

  refresh();
})();
