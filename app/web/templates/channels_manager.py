"""
HTML Template for Channel Management Dashboard
Provides an interactive Web UI to:
- View all monitored public and private Telegram channels
- Add new channels with validation
- Toggle channels enabled/disabled in real time
- Delete channels
"""

CHANNELS_MANAGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Telegram Channels Manager | Govt Job AI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #0B0F17;
      --bg-surface: #131B2A;
      --bg-surface-elevated: #1A2438;
      --border-color: rgba(255, 255, 255, 0.08);
      --border-focus: #3B82F6;
      --text-primary: #F3F4F6;
      --text-secondary: #9CA3AF;
      --text-muted: #6B7280;
      --accent-blue: #3B82F6;
      --accent-blue-glow: rgba(59, 130, 246, 0.25);
      --accent-emerald: #10B981;
      --accent-amber: #F59E0B;
      --accent-rose: #F43F5E;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-base);
      color: var(--text-primary);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
      padding-bottom: 40px;
    }

    header {
      background-color: rgba(19, 27, 42, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-badge {
      background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
      color: #fff;
      font-weight: 700;
      font-size: 13px;
      padding: 5px 10px;
      border-radius: var(--radius-sm);
      box-shadow: 0 0 15px var(--accent-blue-glow);
    }

    .brand-title {
      font-size: 17px;
      font-weight: 600;
      letter-spacing: -0.02em;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-base);
      padding: 4px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
    }

    .nav-link {
      padding: 6px 14px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 500;
      text-decoration: none;
      color: var(--text-secondary);
      transition: all 0.2s;
    }

    .nav-link:hover {
      color: var(--text-primary);
    }

    .nav-link.active {
      background: var(--bg-surface-elevated);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.1);
    }

    .container {
      max-width: 1100px;
      width: 100%;
      margin: 28px auto;
      padding: 0 24px;
    }

    .hero-banner {
      background: linear-gradient(180deg, var(--bg-surface) 0%, rgba(19, 27, 42, 0.4) 100%);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 24px 30px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
    }

    .hero-title {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 6px;
      letter-spacing: -0.02em;
    }

    .hero-subtitle {
      color: var(--text-secondary);
      font-size: 13px;
      max-width: 620px;
    }

    .btn {
      font-family: var(--font-sans);
      font-weight: 500;
      font-size: 13px;
      padding: 8px 16px;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }

    .btn-primary {
      background: var(--accent-blue);
      color: #fff;
      box-shadow: 0 4px 14px var(--accent-blue-glow);
    }

    .btn-primary:hover {
      background: #2563EB;
      transform: translateY(-1px);
    }

    .btn-danger {
      background: rgba(244, 63, 94, 0.15);
      color: var(--accent-rose);
      border: 1px solid rgba(244, 63, 94, 0.3);
    }

    .btn-danger:hover {
      background: var(--accent-rose);
      color: #fff;
    }

    .btn-secondary {
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }

    @media (max-width: 700px) {
      .stats-grid {
        grid-template-columns: 1fr;
      }
    }

    .stat-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .stat-icon {
      width: 42px;
      height: 42px;
      border-radius: var(--radius-sm);
      background: var(--bg-surface-elevated);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }

    .stat-val {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .stat-label {
      font-size: 12px;
      color: var(--text-muted);
    }

    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      overflow: hidden;
      margin-bottom: 24px;
    }

    .card-header {
      padding: 18px 22px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .card-title {
      font-size: 15px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .channel-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .channel-table th {
      background: rgba(11, 15, 23, 0.5);
      padding: 12px 20px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border-color);
    }

    .channel-table td {
      padding: 16px 20px;
      font-size: 13px;
      border-bottom: 1px solid var(--border-color);
      vertical-align: middle;
    }

    .channel-table tr:last-child td {
      border-bottom: none;
    }

    .channel-table tr:hover {
      background: rgba(255, 255, 255, 0.02);
    }

    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      font-family: var(--font-mono);
    }

    .badge-public {
      background: rgba(59, 130, 246, 0.15);
      color: #60A5FA;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .badge-private {
      background: rgba(245, 158, 11, 0.15);
      color: #FBBF24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 38px;
      height: 20px;
    }

    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: #374151;
      transition: .2s;
      border-radius: 20px;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 14px;
      width: 14px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .2s;
      border-radius: 50%;
    }

    input:checked + .slider {
      background-color: var(--accent-emerald);
    }

    input:checked + .slider:before {
      transform: translateX(18px);
    }

    /* Modal Form */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 200;
      padding: 20px;
    }

    .modal-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      max-width: 500px;
      width: 100%;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-label {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .form-control {
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 9px 12px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-family: var(--font-sans);
      outline: none;
    }

    .form-control:focus {
      border-color: var(--border-focus);
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 10px;
    }

    .toast {
      position: fixed;
      bottom: 28px;
      right: 28px;
      background: #1E293B;
      color: #fff;
      padding: 12px 18px;
      border-radius: var(--radius-md);
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      border-left: 4px solid var(--accent-emerald);
      display: none;
      align-items: center;
      gap: 10px;
      z-index: 1000;
      font-size: 13px;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span class="brand-badge">GOVT JOB AI</span>
      <span class="brand-title">Channel Management</span>
    </div>
    <div class="nav-links">
      <a href="/admin/requirements" class="nav-link">🎓 Eligibility Rules</a>
      <a href="/admin/channels" class="nav-link active">📢 Monitored Channels</a>
    </div>
  </header>

  <main class="container">
    <section class="hero-banner">
      <div>
        <h1 class="hero-title">Monitored Telegram Channels</h1>
        <p class="hero-subtitle">
          Add public channels via <code>@username</code> or private channels/groups using their numeric channel ID (e.g. <code>-1001234567890</code>).
          The MTProto listener streams updates from enabled channels automatically.
        </p>
      </div>
      <button class="btn btn-primary" onclick="openAddModal()">+ Add New Channel</button>
    </section>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📡</div>
        <div>
          <div class="stat-val" id="stat-total">0</div>
          <div class="stat-label">Total Channels</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🌐</div>
        <div>
          <div class="stat-val" id="stat-public" style="color:#60A5FA;">0</div>
          <div class="stat-label">Active Public Channels</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔒</div>
        <div>
          <div class="stat-val" id="stat-private" style="color:#FBBF24;">0</div>
          <div class="stat-label">Active Private Groups</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>Configured Channels List</span>
        </div>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="loadChannels()">🔄 Refresh</button>
      </div>
      <div style="overflow-x: auto;">
        <table class="channel-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Channel Name</th>
              <th>Telegram Address / ID</th>
              <th>Type</th>
              <th>Description</th>
              <th style="text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody id="channels-table-body">
            <tr>
              <td colspan="6" style="text-align:center; color:var(--text-muted); padding:30px;">Loading channels...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>

  <!-- Add Channel Modal -->
  <div id="modal-add" class="modal-overlay">
    <div class="modal-card">
      <h3 style="font-size:16px; font-weight:600;">Add Monitored Channel</h3>
      
      <div class="form-group">
        <label class="form-label">Channel Display Name</label>
        <input type="text" id="add-name" class="form-control" placeholder="e.g. UPSC Official Alerts">
      </div>

      <div class="form-group">
        <label class="form-label">Telegram Address or ID</label>
        <input type="text" id="add-address" class="form-control" placeholder="e.g. @upsc_alerts or -1001234567890">
        <span style="font-size:11px; color:var(--text-muted);">For private channels, use the numeric ID starting with -100</span>
      </div>

      <div class="form-group">
        <label class="form-label">Channel Type</label>
        <select id="add-type" class="form-control">
          <option value="public" selected>Public Channel</option>
          <option value="private">Private Channel / Group</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Description (Optional)</label>
        <input type="text" id="add-desc" class="form-control" placeholder="e.g. Daily central govt vacancy notifications">
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" onclick="closeAddModal()">Cancel</button>
        <button class="btn btn-primary" onclick="submitAddChannel()">Add Channel</button>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">
    <span>✅ Channel updated successfully!</span>
  </div>

  <script>
    let channelsData = [];

    async function loadChannels() {
      try {
        const res = await fetch('/api/channels');
        if (!res.ok) return;
        channelsData = await res.json();
        renderChannels();
      } catch (e) {
        console.error('Error fetching channels:', e);
      }
    }

    function renderChannels() {
      const tbody = document.getElementById('channels-table-body');
      tbody.innerHTML = '';

      let total = channelsData.length;
      let pubActive = 0;
      let privActive = 0;

      if (channelsData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:30px;">No channels configured. Click "+ Add New Channel" to begin monitoring.</td></tr>';
      }

      channelsData.forEach(ch => {
        if (ch.enabled) {
          if (ch.type === 'public') pubActive++;
          else privActive++;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>
            <label class="toggle-switch">
              <input type="checkbox" ${ch.enabled ? 'checked' : ''} onchange="toggleChannel('${ch.id}', this.checked)">
              <span class="slider"></span>
            </label>
          </td>
          <td style="font-weight:600; color:#fff;">${escapeHtml(ch.name)}</td>
          <td><code style="font-family:var(--font-mono); color:#93C5FD; background:rgba(59,130,246,0.1); padding:2px 6px; border-radius:4px;">${escapeHtml(ch.telegram_channel_id)}</code></td>
          <td><span class="badge badge-${ch.type}">${ch.type}</span></td>
          <td style="color:var(--text-secondary); max-width:250px;">${escapeHtml(ch.description || '-')}</td>
          <td style="text-align: right;">
            <button class="btn btn-danger" style="padding:4px 8px; font-size:11px;" onclick="deleteChannel('${ch.id}')">Delete</button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('stat-total').innerText = total;
      document.getElementById('stat-public').innerText = pubActive;
      document.getElementById('stat-private').innerText = privActive;
    }

    async function toggleChannel(channelId, isEnabled) {
      try {
        const res = await fetch(`/api/channels/${encodeURIComponent(channelId)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: isEnabled })
        });
        if (res.ok) {
          showToast(isEnabled ? 'Channel enabled for monitoring' : 'Channel disabled');
          loadChannels();
        } else {
          alert('Failed to update channel status.');
        }
      } catch (e) {
        alert('Network error: ' + e.message);
      }
    }

    async function deleteChannel(channelId) {
      if (!confirm('Are you sure you want to delete this channel from monitoring?')) return;
      try {
        const res = await fetch(`/api/channels/${encodeURIComponent(channelId)}`, {
          method: 'DELETE'
        });
        if (res.ok) {
          showToast('Channel removed successfully');
          loadChannels();
        } else {
          alert('Failed to delete channel.');
        }
      } catch (e) {
        alert('Network error: ' + e.message);
      }
    }

    function openAddModal() {
      document.getElementById('add-name').value = '';
      document.getElementById('add-address').value = '';
      document.getElementById('add-desc').value = '';
      document.getElementById('modal-add').style.display = 'flex';
    }

    function closeAddModal() {
      document.getElementById('modal-add').style.display = 'none';
    }

    async function submitAddChannel() {
      const name = document.getElementById('add-name').value.trim();
      const address = document.getElementById('add-address').value.trim();
      const type = document.getElementById('add-type').value;
      const desc = document.getElementById('add-desc').value.trim();

      if (!name || !address) {
        alert('Please fill in both the Channel Name and Telegram Address.');
        return;
      }

      const payload = {
        name: name,
        telegram_channel_id: address,
        type: type,
        enabled: true,
        description: desc
      };

      try {
        const res = await fetch('/api/channels', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          closeAddModal();
          showToast('Channel added and active!');
          loadChannels();
        } else {
          const err = await res.json();
          alert('Error: ' + (err.detail || JSON.stringify(err)));
        }
      } catch (e) {
        alert('Network error adding channel: ' + e.message);
      }
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.querySelector('span').innerText = '✅ ' + msg;
      toast.style.display = 'flex';
      setTimeout(() => { toast.style.display = 'none'; }, 3000);
    }

    function escapeHtml(text) {
      if (!text) return '';
      return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    window.addEventListener('DOMContentLoaded', loadChannels);
  </script>
</body>
</html>
"""
