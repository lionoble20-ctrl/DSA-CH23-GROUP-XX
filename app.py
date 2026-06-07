# =============================================================================
#  app.py  —  Flask Web Interface for the URL Shortening Service
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Run with: python app.py
#  Then open: http://localhost:5000
# =============================================================================

import sys
sys.path.insert(0, './src')

from flask import Flask, request, redirect, jsonify, render_template_string
from url_store      import URLStore
from redirect_graph import RedirectGraph
from sorter         import sort_urls_by_clicks, merge_sort, binary_search_threshold
import contextlib, io

app = Flask(__name__)
store = URLStore()
graph = RedirectGraph()

# Pre-load sample data silently
with contextlib.redirect_stdout(io.StringIO()):
    c1 = store.shorten("https://www.google.com")
    c2 = store.shorten("https://www.youtube.com")
    c3 = store.shorten("https://www.github.com")
    c4 = store.shorten("https://www.wikipedia.org")
    c5 = store.shorten("https://www.stackoverflow.com")
    for _ in range(7): store.redirect(c1)
    for _ in range(4): store.redirect(c2)
    for _ in range(11): store.redirect(c3)
    for _ in range(2): store.redirect(c4)
    graph.add_redirect(c1, c2)
    graph.add_redirect(c2, c3)

# =============================================================================
#  HTML Template — full single-page app
# =============================================================================

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>short.ly — DSA Group Project</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:       #0a0a0f;
    --surface:  #12121a;
    --card:     #1a1a26;
    --border:   #2a2a3e;
    --accent:   #6c63ff;
    --accent2:  #ff6584;
    --green:    #43e97b;
    --text:     #e8e8f0;
    --muted:    #8888aa;
    --mono:     'Space Mono', monospace;
    --sans:     'Syne', sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    background-image:
      radial-gradient(ellipse at 20% 20%, rgba(108,99,255,0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 80%, rgba(255,101,132,0.06) 0%, transparent 50%);
  }

  /* ── Header ── */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 48px;
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(10px);
    position: sticky; top: 0; z-index: 100;
    background: rgba(10,10,15,0.85);
  }
  .logo {
    font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .logo span { font-family: var(--mono); font-size: 13px; color: var(--muted); -webkit-text-fill-color: var(--muted); margin-left: 12px; font-weight: 400; }
  .badge { font-family: var(--mono); font-size: 11px; background: rgba(108,99,255,0.15); color: var(--accent); border: 1px solid rgba(108,99,255,0.3); padding: 4px 10px; border-radius: 20px; }

  /* ── Layout ── */
  .container { max-width: 1100px; margin: 0 auto; padding: 40px 48px; }

  /* ── Stats bar ── */
  .stats-bar {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px;
  }
  .stat-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 24px; transition: border-color 0.2s;
  }
  .stat-card:hover { border-color: var(--accent); }
  .stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; font-family: var(--mono); }
  .stat-value { font-size: 28px; font-weight: 800; }
  .stat-value.purple { color: var(--accent); }
  .stat-value.pink   { color: var(--accent2); }
  .stat-value.green  { color: var(--green); }
  .stat-value.white  { color: var(--text); }

  /* ── Shorten form ── */
  .shorten-box {
    background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    padding: 32px; margin-bottom: 32px; position: relative; overflow: hidden;
  }
  .shorten-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }
  .section-title {
    font-size: 13px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 2px; color: var(--muted); margin-bottom: 20px; font-family: var(--mono);
  }
  .input-row { display: flex; gap: 12px; }
  .url-input {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 18px; color: var(--text);
    font-family: var(--mono); font-size: 14px; outline: none; transition: border-color 0.2s;
  }
  .url-input::placeholder { color: var(--muted); }
  .url-input:focus { border-color: var(--accent); }
  .btn {
    padding: 14px 28px; border-radius: 10px; border: none; cursor: pointer;
    font-family: var(--sans); font-weight: 600; font-size: 14px; transition: all 0.2s;
    letter-spacing: 0.3px;
  }
  .btn-primary {
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    color: white;
  }
  .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(108,99,255,0.35); }
  .btn-danger { background: rgba(255,101,132,0.15); color: var(--accent2); border: 1px solid rgba(255,101,132,0.3); }
  .btn-danger:hover { background: rgba(255,101,132,0.25); }
  .btn-ghost { background: rgba(255,255,255,0.05); color: var(--muted); border: 1px solid var(--border); }
  .btn-ghost:hover { background: rgba(255,255,255,0.1); color: var(--text); }

  /* ── Result pill ── */
  .result-pill {
    display: none; margin-top: 16px; background: rgba(67,233,123,0.08);
    border: 1px solid rgba(67,233,123,0.25); border-radius: 10px;
    padding: 14px 18px; font-family: var(--mono); font-size: 14px;
    color: var(--green); animation: slideIn 0.3s ease;
  }
  .result-pill.error { background: rgba(255,101,132,0.08); border-color: rgba(255,101,132,0.25); color: var(--accent2); }
  @keyframes slideIn { from { opacity:0; transform:translateY(-8px); } to { opacity:1; transform:translateY(0); } }

  /* ── Two column layout ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }

  /* ── Tables ── */
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    padding: 28px; height: fit-content;
  }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th {
    text-align: left; font-family: var(--mono); font-size: 10px;
    text-transform: uppercase; letter-spacing: 1.5px; color: var(--muted);
    padding: 10px 12px; border-bottom: 1px solid var(--border);
  }
  td { padding: 12px 12px; font-size: 13px; border-bottom: 1px solid rgba(42,42,62,0.5); }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(108,99,255,0.04); }
  .code-pill {
    font-family: var(--mono); font-size: 12px; background: rgba(108,99,255,0.12);
    color: var(--accent); padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(108,99,255,0.2);
  }
  .url-cell { color: var(--muted); font-size: 12px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .click-badge {
    font-family: var(--mono); font-size: 11px; font-weight: 700;
    padding: 2px 8px; border-radius: 12px;
  }
  .click-high { background: rgba(67,233,123,0.12); color: var(--green); }
  .click-mid  { background: rgba(108,99,255,0.12); color: var(--accent); }
  .click-low  { background: rgba(136,136,170,0.1); color: var(--muted); }

  /* ── Top-K bar chart ── */
  .bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .bar-label { font-family: var(--mono); font-size: 11px; color: var(--accent); width: 60px; flex-shrink: 0; }
  .bar-track { flex: 1; height: 8px; background: var(--surface); border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--accent), var(--accent2)); transition: width 0.8s ease; }
  .bar-count { font-family: var(--mono); font-size: 11px; color: var(--muted); width: 30px; text-align: right; flex-shrink: 0; }

  /* ── Bottom section ── */
  .full-card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 28px; margin-bottom: 24px; }

  /* ── Actions ── */
  .action-row { display: flex; gap: 8px; }

  /* ── Tabs ── */
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; }
  .tab { padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; border: 1px solid transparent; transition: all 0.2s; color: var(--muted); }
  .tab.active { background: rgba(108,99,255,0.15); color: var(--accent); border-color: rgba(108,99,255,0.3); }
  .tab:hover:not(.active) { color: var(--text); }

  /* ── Rank badge ── */
  .rank { font-family: var(--mono); font-size: 11px; color: var(--muted); width: 24px; }
  .rank-1 { color: #ffd700; }
  .rank-2 { color: #c0c0c0; }
  .rank-3 { color: #cd7f32; }

  /* ── Footer ── */
  footer { text-align: center; padding: 32px; color: var(--muted); font-size: 12px; font-family: var(--mono); border-top: 1px solid var(--border); margin-top: 20px; }

  /* ── Loader ── */
  .loading { display: none; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.2); border-top-color: white; border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; vertical-align: middle; margin-left: 8px; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>

<header>
  <div>
    <span class="logo">short.ly <span>URL Shortener</span></span>
  </div>
  <div class="badge">DSA-CH23-GROUP-XX</div>
</header>

<div class="container">

  <!-- Stats Bar -->
  <div class="stats-bar" id="statsBar">
    <div class="stat-card"><div class="stat-label">URLs Stored</div><div class="stat-value purple" id="s-stored">0</div></div>
    <div class="stat-card"><div class="stat-label">Total Shortened</div><div class="stat-value pink" id="s-shortened">0</div></div>
    <div class="stat-card"><div class="stat-label">Total Redirects</div><div class="stat-value green" id="s-redirects">0</div></div>
    <div class="stat-card"><div class="stat-label">Undo Stack</div><div class="stat-value white" id="s-undo">0</div></div>
  </div>

  <!-- Shorten Form -->
  <div class="shorten-box">
    <div class="section-title">⚡ Shorten a URL</div>
    <div class="input-row">
      <input class="url-input" id="urlInput" type="text" placeholder="https://your-very-long-url-goes-here.com/path/to/page" />
      <button class="btn btn-primary" onclick="shortenURL()">Shorten →</button>
      <button class="btn btn-ghost" onclick="undoLast()">↩ Undo</button>
    </div>
    <div class="result-pill" id="resultPill"></div>
  </div>

  <!-- Two Column -->
  <div class="grid-2">

    <!-- All URLs table -->
    <div class="card">
      <div class="section-title">🔗 Stored Links</div>
      <table>
        <thead><tr><th>Code</th><th>URL</th><th>Clicks</th><th></th></tr></thead>
        <tbody id="urlTable"></tbody>
      </table>
    </div>

    <!-- Top-K Analytics -->
    <div class="card">
      <div class="section-title">📊 Top Clicked Links</div>
      <div id="topKChart"></div>
    </div>

  </div>

  <!-- Redirect test -->
  <div class="full-card">
    <div class="section-title">🔄 Test a Redirect</div>
    <div class="input-row">
      <input class="url-input" id="redirectInput" placeholder="Enter short code (e.g. 8ffdef)" style="max-width:280px"/>
      <button class="btn btn-primary" onclick="testRedirect()">Redirect →</button>
    </div>
    <div class="result-pill" id="redirectResult"></div>
  </div>

</div>

<footer>DSA Group Project — Theme B: URL Shortening Service (Bitly-lite) &nbsp;|&nbsp; Hash Table · Stack · Queue · Heap · Graph · Merge Sort</footer>

<script>
  // ── API calls ──────────────────────────────────────────────

  async function shortenURL() {
    const url = document.getElementById('urlInput').value.trim();
    if (!url) return;
    const res  = await fetch('/api/shorten', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url}) });
    const data = await res.json();
    const pill = document.getElementById('resultPill');
    pill.style.display = 'block';
    if (data.error) {
      pill.className = 'result-pill error';
      pill.textContent = '✗ ' + data.error;
    } else {
      pill.className = 'result-pill';
      pill.textContent = '✓ Shortened! → short.ly/' + data.code + '   (copy the code to use in Redirect test)';
      document.getElementById('urlInput').value = '';
    }
    refreshAll();
  }

  async function undoLast() {
    await fetch('/api/undo', { method:'POST' });
    const pill = document.getElementById('resultPill');
    pill.style.display = 'block';
    pill.className = 'result-pill';
    pill.textContent = '↩ Last action undone';
    refreshAll();
  }

  async function deleteURL(code) {
    await fetch('/api/delete/' + code, { method:'DELETE' });
    refreshAll();
  }

  async function testRedirect() {
    const code = document.getElementById('redirectInput').value.trim();
    if (!code) return;
    const res  = await fetch('/api/redirect/' + code);
    const data = await res.json();
    const pill = document.getElementById('redirectResult');
    pill.style.display = 'block';
    if (data.error) {
      pill.className = 'result-pill error';
      pill.textContent = '✗ ' + data.error;
    } else {
      pill.className = 'result-pill';
      pill.textContent = '✓ Redirects to: ' + data.url + '  [clicks: ' + data.clicks + ']';
    }
    refreshAll();
  }

  async function refreshAll() {
    // Stats
    const stats = await (await fetch('/api/stats')).json();
    document.getElementById('s-stored').textContent    = stats.stored;
    document.getElementById('s-shortened').textContent = stats.shortened;
    document.getElementById('s-redirects').textContent = stats.redirects;
    document.getElementById('s-undo').textContent      = stats.undo_depth;

    // URL Table
    const urls = await (await fetch('/api/urls')).json();
    const tbody = document.getElementById('urlTable');
    tbody.innerHTML = '';
    urls.forEach(u => {
      const clicks = u.clicks;
      const cls = clicks >= 5 ? 'click-high' : clicks >= 2 ? 'click-mid' : 'click-low';
      tbody.innerHTML += `
        <tr>
          <td><span class="code-pill">${u.code}</span></td>
          <td><span class="url-cell" title="${u.url}">${u.url}</span></td>
          <td><span class="click-badge ${cls}">${clicks}</span></td>
          <td><button class="btn btn-danger" style="padding:4px 10px;font-size:11px" onclick="deleteURL('${u.code}')">✕</button></td>
        </tr>`;
    });

    // Top-K chart
    const topk = await (await fetch('/api/topk/5')).json();
    const max   = topk.length > 0 ? topk[0].clicks : 1;
    const chart = document.getElementById('topKChart');
    chart.innerHTML = '';
    const medals = ['rank-1','rank-2','rank-3','',''];
    topk.forEach((item, i) => {
      const pct = max > 0 ? (item.clicks / max * 100) : 0;
      chart.innerHTML += `
        <div class="bar-row">
          <div class="bar-label ${medals[i]||''}">${item.code}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
          <div class="bar-count">${item.clicks}</div>
        </div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:14px;padding-left:72px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${item.url}</div>`;
    });
    if (topk.length === 0) chart.innerHTML = '<div style="color:var(--muted);font-size:13px;margin-top:16px">No clicks recorded yet</div>';
  }

  // ── Init ──────────────────────────────────────────────────
  refreshAll();
  setInterval(refreshAll, 5000);

  // Allow Enter key in inputs
  document.getElementById('urlInput').addEventListener('keydown', e => { if(e.key==='Enter') shortenURL(); });
  document.getElementById('redirectInput').addEventListener('keydown', e => { if(e.key==='Enter') testRedirect(); });
</script>
</body>
</html>
"""

# =============================================================================
#  API Routes
# =============================================================================

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.get_json()
    url  = data.get('url', '').strip()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = store.shorten(url)
        return jsonify({'code': code})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/redirect/<code>')
def api_redirect(code):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            url = store.redirect(code)
        return jsonify({'url': url, 'clicks': store.click_counts.get(code, 0)})
    except KeyError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/delete/<code>', methods=['DELETE'])
def api_delete(code):
    with contextlib.redirect_stdout(io.StringIO()):
        result = store.delete(code)
    return jsonify({'success': result})


@app.route('/api/undo', methods=['POST'])
def api_undo():
    with contextlib.redirect_stdout(io.StringIO()):
        result = store.undo()
    return jsonify({'success': result})


@app.route('/api/urls')
def api_urls():
    data = []
    for code, url in store.short_to_long.items():
        data.append({'code': code, 'url': url, 'clicks': store.click_counts.get(code, 0)})
    data.sort(key=lambda x: x['clicks'], reverse=True)
    return jsonify(data)


@app.route('/api/topk/<int:k>')
def api_topk(k):
    with contextlib.redirect_stdout(io.StringIO()):
        results = store.top_k(k)
    out = []
    for clicks, code in results:
        out.append({'code': code, 'clicks': clicks, 'url': store.short_to_long.get(code, '')})
    return jsonify(out)


@app.route('/api/stats')
def api_stats():
    return jsonify({
        'stored':    len(store.short_to_long),
        'shortened': store.total_shortened,
        'redirects': store.total_redirects,
        'undo_depth': len(store.history_stack)
    })


# =============================================================================
#  Run
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*55)
    print("  short.ly — URL Shortener Web Interface")
    print("  DSA Group Project — Theme B: Bitly-lite")
    print("="*55)
    print("\n  Open your browser and go to:")
    print("  http://localhost:5000\n")
    app.run(debug=True, port=5000)