"""
HTML Template for Channel Management Dashboard & Live Intelligence Queue
Provides an interactive Web UI to:
- View all monitored public and private Telegram channels
- Add new channels with validation
- Trigger immediate multi-channel message fetch / sync
- Toggle channels enabled/disabled in real time
- Inspect live message ingestion queue and AI extraction results
"""

CHANNELS_MANAGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Telegram Channels & Intelligence Queue | Govt Job AI</title>
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
      --accent-purple: #8B5CF6;
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
      padding-bottom: 50px;
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
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 24px;
      width: 100%;
    }

    .hero-banner {
      background: linear-gradient(180deg, rgba(59, 130, 246, 0.08) 0%, rgba(19, 27, 42, 0.4) 100%);
      border: 1px solid rgba(59, 130, 246, 0.2);
      border-radius: var(--radius-lg);
      padding: 24px 28px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }

    .hero-title {
      font-size: 20px;
      font-weight: 700;
      margin-bottom: 6px;
      color: #fff;
    }

    .hero-subtitle {
      font-size: 13px;
      color: var(--text-secondary);
      max-width: 750px;
      line-height: 1.5;
    }

    .btn-group {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn {
      padding: 9px 16px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .btn-primary {
      background: var(--accent-blue);
      color: #fff;
      box-shadow: 0 4px 12px var(--accent-blue-glow);
    }

    .btn-primary:hover {
      background: #2563EB;
    }

    .btn-emerald {
      background: var(--accent-emerald);
      color: #fff;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }

    .btn-emerald:hover {
      background: #059669;
    }

    .btn-secondary {
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.08);
    }

    .btn-danger {
      background: rgba(244, 63, 94, 0.15);
      color: #FDA4AF;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }

    .btn-danger:hover {
      background: rgba(244, 63, 94, 0.3);
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }

    @media (max-width: 900px) {
      .stats-grid {
        grid-template-columns: repeat(2, 1fr);
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
      margin-bottom: 28px;
    }

    .card-header {
      padding: 16px 22px;
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
      padding: 14px 20px;
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
      letter-spacing: 0.04em;
    }

    .badge-public {
      background: rgba(59, 130, 246, 0.15);
      color: #93C5FD;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .badge-private {
      background: rgba(245, 158, 11, 0.15);
      color: #FCD34D;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-processed, .badge-eligible {
      background: rgba(16, 185, 129, 0.15);
      color: #6EE7B7;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-uncertain {
      background: rgba(245, 158, 11, 0.15);
      color: #FCD34D;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-extracting, .badge-pending {
      background: rgba(59, 130, 246, 0.15);
      color: #93C5FD;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .badge-non_job {
      background: rgba(107, 114, 128, 0.2);
      color: #9CA3AF;
      border: 1px solid rgba(107, 114, 128, 0.3);
    }

    .badge-failed, .badge-ai_review_required, .badge-not_eligible {
      background: rgba(244, 63, 94, 0.15);
      color: #FDA4AF;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }

    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 36px;
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
      background-color: var(--bg-surface-elevated);
      border: 1px solid var(--border-color);
      transition: .3s;
      border-radius: 20px;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 14px;
      width: 14px;
      left: 2px;
      bottom: 2px;
      background-color: var(--text-muted);
      transition: .3s;
      border-radius: 50%;
    }

    input:checked + .slider {
      background-color: var(--accent-emerald);
      border-color: var(--accent-emerald);
    }

    input:checked + .slider:before {
      transform: translateX(16px);
      background-color: white;
    }

    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .modal-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 24px;
      width: 100%;
      max-width: 480px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }

    .form-group {
      margin-bottom: 16px;
    }

    .form-label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .form-control {
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 9px 12px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-family: var(--font-sans);
      width: 100%;
      outline: none;
    }

    .form-control:focus {
      border-color: var(--border-focus);
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 20px;
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
      <span class="brand-title">Channel Management & Live Queue</span>
    </div>
    <div class="nav-links">
      <a href="/admin/requirements" class="nav-link">🎓 Eligibility Rules</a>
      <a href="/admin/channels" class="nav-link active">📢 Channels & Live Queue</a>
    </div>
  </header>

  <main class="container">
    <section class="hero-banner">
      <div>
        <h1 class="hero-title">Monitored Telegram Channels & Live Queue</h1>
        <p class="hero-subtitle">
          The system streams notifications automatically via Web Preview and MTProto.
          Click <strong>Fetch Latest Messages Now</strong> to immediately pull new messages from all enabled channels into the AI intelligence pipeline.
        </p>
      </div>
      <div class="btn-group">
        <button id="btn-fetch-now" class="btn btn-emerald" onclick="fetchRecentMessages()">⚡ Fetch Latest Messages Now</button>
        <button class="btn btn-primary" onclick="openAddModal()">+ Add Channel</button>
      </div>
    </section>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📡</div>
        <div>
          <div class="stat-val" id="stat-total">0</div>
          <div class="stat-label">Monitored Channels</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📨</div>
        <div>
          <div class="stat-val" id="stat-messages" style="color:#60A5FA;">0</div>
          <div class="stat-label">Messages Ingested</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💼</div>
        <div>
          <div class="stat-val" id="stat-jobs" style="color:#34D399;">0</div>
          <div class="stat-label">Jobs Extracted</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div>
          <div class="stat-val" id="stat-eligible" style="color:#FBBF24;">0</div>
          <div class="stat-label">Eligible Matches</div>
        </div>
      </div>
    </div>

    <!-- Monitored Channels Card -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>📡 Configured Monitored Channels</span>
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

    <!-- Live Ingested Messages Queue -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>📨 Recent Ingested Messages Queue</span>
        </div>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="loadMessagesQueue()">🔄 Refresh Queue</button>
      </div>
      <div style="overflow-x: auto;">
        <table class="channel-table">
          <thead>
            <tr>
              <th>Processing Status</th>
              <th>Channel</th>
              <th>Message ID</th>
              <th>Message Excerpt</th>
              <th>Received At</th>
            </tr>
          </thead>
          <tbody id="messages-table-body">
            <tr>
              <td colspan="5" style="text-align:center; color:var(--text-muted); padding:24px;">No messages received yet. Click "Fetch Latest Messages Now" above.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Discovered Jobs Card -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>💼 Discovered Recruitment Notifications</span>
        </div>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="loadJobsList()">🔄 Refresh Jobs</button>
      </div>
      <div style="overflow-x: auto;">
        <table class="channel-table">
          <thead>
            <tr>
              <th>Eligibility</th>
              <th>Organization</th>
              <th>Post Name</th>
              <th>Advt Number</th>
              <th>AI Provider</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody id="jobs-table-body">
            <tr>
              <td colspan="6" style="text-align:center; color:var(--text-muted); padding:24px;">No jobs processed yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- Add Channel Modal -->
  <div id="modal-add" class="modal-overlay">
    <div class="modal-card">
      <h3 style="font-size:16px; font-weight:600; margin-bottom:16px;">Add Monitored Channel</h3>
      
      <div class="form-group">
        <label class="form-label">Channel Display Name</label>
        <input type="text" id="add-name" class="form-control" placeholder="e.g. Govt Jobs Alert">
      </div>

      <div class="form-group">
        <label class="form-label">Telegram Address or ID</label>
        <input type="text" id="add-address" class="form-control" placeholder="e.g. @govtjobsalert">
        <span style="font-size:11px; color:var(--text-muted);">Use @username for public channels, or numeric ID for private groups.</span>
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
        <input type="text" id="add-desc" class="form-control" placeholder="e.g. Central & State Government Recruitment">
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" onclick="closeAddModal()">Cancel</button>
        <button class="btn btn-primary" onclick="submitAddChannel()">Add Channel</button>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">
    <span>✅ Done!</span>
  </div>

  <script>
    let channelsData = [];

    async function loadAllData() {
      await Promise.all([
        loadChannels(),
        loadMessagesQueue(),
        loadJobsList()
      ]);
    }

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
      document.getElementById('stat-total').innerText = total;

      if (channelsData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:30px;">No channels configured. Click "+ Add Channel" to start.</td></tr>';
        return;
      }

      channelsData.forEach(ch => {
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
    }

    async function loadMessagesQueue() {
      try {
        const res = await fetch('/api/messages?limit=25');
        if (!res.ok) return;
        const msgs = await res.json();
        document.getElementById('stat-messages').innerText = msgs.length;

        const tbody = document.getElementById('messages-table-body');
        if (msgs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:24px;">No messages received yet. Click "Fetch Latest Messages Now" above.</td></tr>';
          return;
        }

        tbody.innerHTML = '';
        msgs.forEach(m => {
          const tr = document.createElement('tr');
          const statusClass = (m.processing_status || '').toLowerCase();
          tr.innerHTML = `
            <td><span class="badge badge-${statusClass}">${escapeHtml(m.processing_status)}</span></td>
            <td><code style="color:#93C5FD;">${escapeHtml(m.channel_identifier || 'unknown')}</code></td>
            <td><code>${escapeHtml(m.telegram_message_id)}</code></td>
            <td style="color:var(--text-secondary); max-width:350px;">${escapeHtml(m.message_text || '-')}</td>
            <td style="color:var(--text-muted); font-size:11px;">${m.received_at ? new Date(m.received_at).toLocaleTimeString() : '-'}</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error('Error loading messages queue:', e);
      }
    }

    async function loadJobsList() {
      try {
        const res = await fetch('/api/jobs?limit=25');
        if (!res.ok) return;
        const jobs = await res.json();
        document.getElementById('stat-jobs').innerText = jobs.length;

        let eligibleCount = jobs.filter(j => j.eligibility_status === 'ELIGIBLE').length;
        document.getElementById('stat-eligible').innerText = eligibleCount;

        const tbody = document.getElementById('jobs-table-body');
        if (jobs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:24px;">No jobs processed yet.</td></tr>';
          return;
        }

        tbody.innerHTML = '';
        jobs.forEach(j => {
          const tr = document.createElement('tr');
          const statusClass = (j.eligibility_status || '').toLowerCase();
          tr.innerHTML = `
            <td><span class="badge badge-${statusClass}">${escapeHtml(j.eligibility_status)}</span></td>
            <td style="font-weight:600; color:#fff;">${escapeHtml(j.organization || 'Unknown')}</td>
            <td>${escapeHtml(j.post_name || '-')}</td>
            <td><code>${escapeHtml(j.notification_number || '-')}</code></td>
            <td><span class="badge" style="background:rgba(255,255,255,0.06);">${escapeHtml(j.ai_provider_used || 'ai')}</span></td>
            <td>${(j.confidence * 100).toFixed(0)}%</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error('Error loading jobs list:', e);
      }
    }

    async function fetchRecentMessages() {
      const btn = document.getElementById('btn-fetch-now');
      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '⏳ Scanning & Ingesting Channels...';

      try {
        const res = await fetch('/api/channels/fetch-recent', { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          const r = data.result || {};
          showToast(`Synced ${r.channels_synced || 0} channels (${r.total_new_ingested || 0} new messages ingested)`);
          await loadAllData();
        } else {
          alert('Error during channel sync: ' + (data.detail || JSON.stringify(data)));
        }
      } catch (e) {
        alert('Failed to trigger message fetch: ' + e.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
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
      setTimeout(() => { toast.style.display = 'none'; }, 4000);
    }

    function escapeHtml(text) {
      if (!text) return '';
      return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    window.addEventListener('DOMContentLoaded', () => {
      loadAllData();
      setInterval(loadAllData, 12000); // Auto-refresh every 12s
    });
  </script>
</body>
</html>
"""
