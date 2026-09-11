"""
HTML Template for Apple-Inspired Monitored Channels & Message Stream
Clean, calm, minimalist interface with Apple Human Interface Guidelines:
Light background (#F5F5F7), grouped white settings cards, iOS-style toggles,
refined typography, channel controls, and live ingestion queue audit.
"""

CHANNELS_MANAGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Channels & Ingestion | Job Alerts</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-page: #F5F5F7;
      --bg-surface: #FFFFFF;
      --bg-surface-secondary: #F2F2F7;
      --bg-surface-tertiary: #E5E5EA;
      --text-primary: #1D1D1F;
      --text-secondary: #6E6E73;
      --text-tertiary: #86868B;
      --border-subtle: rgba(0, 0, 0, 0.08);
      --border-divider: #E5E5EA;
      --accent-blue: #0071E3;
      --accent-blue-hover: #0077ED;
      --accent-blue-subtle: rgba(0, 113, 227, 0.08);
      --status-green: #34C759;
      --status-green-bg: #E8F5E9;
      --status-amber: #FF9500;
      --status-amber-bg: #FFF4E5;
      --status-red: #FF3B30;
      --status-red-bg: #FEECEB;
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-full: 9999px;
      --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", system-ui, sans-serif;
      --font-mono: "JetBrains Mono", SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-page);
      color: var(--text-primary);
      font-family: var(--font-sans);
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* GLOBAL APPLE HEADER */
    header {
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid var(--border-subtle);
      position: sticky;
      top: 0;
      z-index: 100;
      height: 54px;
      display: flex;
      align-items: center;
      padding: 0 24px;
    }

    .header-inner {
      max-width: 1080px;
      width: 100%;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .brand-logo {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      text-decoration: none;
      letter-spacing: -0.015em;
    }

    .nav-tabs {
      display: flex;
      align-items: center;
      gap: 24px;
    }

    .nav-tab {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      text-decoration: none;
      transition: color 0.15s ease;
    }

    .nav-tab:hover {
      color: var(--text-primary);
    }

    .nav-tab.active {
      color: var(--text-primary);
      font-weight: 600;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .btn-secondary-apple {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
      background: var(--bg-surface-secondary);
      border: none;
      cursor: pointer;
      padding: 6px 14px;
      border-radius: var(--radius-full);
      transition: background 0.15s;
    }

    .btn-secondary-apple:hover {
      background: var(--bg-surface-tertiary);
    }

    .btn-primary-apple {
      font-size: 13px;
      font-weight: 500;
      color: #FFFFFF;
      background: var(--accent-blue);
      border: none;
      cursor: pointer;
      padding: 6px 16px;
      border-radius: var(--radius-full);
      transition: background 0.15s;
    }

    .btn-primary-apple:hover {
      background: var(--accent-blue-hover);
    }

    /* MAIN CONTAINER */
    main {
      max-width: 1080px;
      width: 100%;
      margin: 0 auto;
      padding: 40px 24px 80px 24px;
      flex: 1;
    }

    .page-hero {
      margin-bottom: 28px;
    }

    .page-title {
      font-size: 32px;
      font-weight: 700;
      letter-spacing: -0.025em;
      color: var(--text-primary);
      margin-bottom: 6px;
    }

    .page-subtitle {
      font-size: 15px;
      color: var(--text-secondary);
      max-width: 640px;
      line-height: 1.5;
    }

    .summary-inline-bar {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      font-size: 13px;
      color: var(--text-secondary);
      background: rgba(0, 0, 0, 0.03);
      padding: 6px 16px;
      border-radius: var(--radius-full);
      margin-top: 14px;
    }

    .summary-dot {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: var(--text-tertiary);
    }

    /* GROUPED CARDS */
    .stack-sections {
      display: flex;
      flex-direction: column;
      gap: 32px;
      margin-top: 24px;
    }

    .section-block {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .section-header-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 4px;
    }

    .section-heading-text {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
    }

    .btn-refresh-clean {
      font-size: 12px;
      color: var(--accent-blue);
      background: transparent;
      border: none;
      cursor: pointer;
      font-weight: 500;
    }

    .clean-table-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }

    /* CLEAN TABLES */
    .apple-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .apple-table th {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 12px 18px;
      background: var(--bg-surface-secondary);
      border-bottom: 1px solid var(--border-divider);
    }

    .apple-table td {
      padding: 14px 18px;
      font-size: 13.5px;
      color: var(--text-primary);
      border-bottom: 1px solid var(--border-divider);
      vertical-align: middle;
    }

    .apple-table tr:last-child td {
      border-bottom: none;
    }

    .apple-table tr:hover td {
      background: rgba(0, 0, 0, 0.015);
    }

    .code-badge {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-secondary);
      background: var(--bg-surface-secondary);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
    }

    .type-pill {
      font-size: 11px;
      font-weight: 500;
      padding: 2px 8px;
      border-radius: var(--radius-full);
      background: var(--bg-surface-secondary);
      color: var(--text-secondary);
      text-transform: capitalize;
    }

    .status-dot-sm {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 6px;
    }

    .dot-green { background: var(--status-green); }
    .dot-amber { background: var(--status-amber); }
    .dot-gray { background: var(--text-tertiary); }

    .btn-delete-clean {
      font-size: 12px;
      color: var(--status-red);
      background: transparent;
      border: none;
      cursor: pointer;
      font-weight: 500;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
      transition: background 0.15s;
    }

    .btn-delete-clean:hover {
      background: var(--status-red-bg);
    }

    /* IOS SWITCH */
    .ios-switch {
      position: relative;
      display: inline-block;
      width: 40px;
      height: 24px;
      flex-shrink: 0;
    }

    .ios-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .switch-slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: #E5E5EA;
      transition: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      border-radius: var(--radius-full);
    }

    .switch-slider:before {
      position: absolute;
      content: "";
      height: 20px;
      width: 20px;
      left: 2px;
      bottom: 2px;
      background-color: white;
      transition: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }

    input:checked + .switch-slider {
      background-color: var(--status-green);
    }

    input:checked + .switch-slider:before {
      transform: translateX(16px);
    }

    /* MODAL (APPLE SHEET STYLE) */
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.25);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      transition: opacity 0.2s ease;
      padding: 20px;
    }

    .modal-backdrop.open {
      display: flex;
      opacity: 1;
    }

    .modal-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 24px 28px;
      width: 100%;
      max-width: 460px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .modal-title {
      font-size: 18px;
      font-weight: 600;
      letter-spacing: -0.015em;
      color: var(--text-primary);
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-label {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .apple-input {
      width: 100%;
      background: var(--bg-surface-secondary);
      border: 1px solid transparent;
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      font-size: 14px;
      color: var(--text-primary);
      font-family: var(--font-sans);
      outline: none;
      transition: all 0.15s;
    }

    .apple-input:focus {
      background: #FFFFFF;
      border-color: var(--accent-blue);
      box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15);
    }

    .apple-select {
      background: var(--bg-surface-secondary);
      border: 1px solid transparent;
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      font-size: 14px;
      color: var(--text-primary);
      font-family: var(--font-sans);
      outline: none;
      cursor: pointer;
      width: 100%;
    }

    .modal-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 10px;
    }

    /* TOAST PILL */
    .toast-pill {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: rgba(29, 29, 31, 0.9);
      backdrop-filter: blur(10px);
      color: #FFFFFF;
      font-size: 13px;
      padding: 8px 18px;
      border-radius: var(--radius-full);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
      pointer-events: none;
      opacity: 0;
      transition: all 0.2s ease;
      z-index: 2000;
    }

    .toast-pill.show {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>
  <!-- UNIFIED NAV -->
  <header>
    <div class="header-inner">
      <a href="/jobs" class="brand-logo">Job Alerts</a>
      <nav class="nav-tabs">
        <a href="/jobs" class="nav-tab">Jobs</a>
        <a href="/plan-to-apply" class="nav-tab">⭐ Plan to Apply</a>
        <a href="/applied" class="nav-tab">✓ Applied</a>
        <a href="/admin/requirements" class="nav-tab">Profile &amp; Rules</a>
        <a href="/admin/channels" class="nav-tab active">Channels</a>
      </nav>
      <div class="header-actions">
        <button class="btn-secondary-apple" id="btn-scan" onclick="fetchRecentMessages()">⚡ Scan Channels</button>
        <button class="btn-primary-apple" onclick="openAddModal()">+ Add Channel</button>
      </div>
    </div>
  </header>

  <main>
    <div class="page-hero">
      <h1 class="page-title">Monitored Sources & Live Stream</h1>
      <p class="page-subtitle">
        Automated Telegram web preview and MTProto ingestion monitoring official state and central recruitment channels.
      </p>
      <div class="summary-inline-bar">
        <span id="stat-total">8</span> monitored sources
        <span class="summary-dot"></span>
        <span id="stat-messages">0</span> messages indexed
        <span class="summary-dot"></span>
        <span id="stat-jobs">0</span> circulars extracted
      </div>
    </div>

    <div class="stack-sections">
      <!-- MONITORED CHANNELS -->
      <div class="section-block">
        <div class="section-header-bar">
          <div class="section-heading-text">Configured Telegram Channels</div>
          <button class="btn-refresh-clean" onclick="loadChannels()">Refresh</button>
        </div>
        <div class="clean-table-card">
          <div style="overflow-x: auto;">
            <table class="apple-table">
              <thead>
                <tr>
                  <th style="width: 60px;">Active</th>
                  <th>Channel Name</th>
                  <th>Telegram Identifier</th>
                  <th>Type</th>
                  <th>Description</th>
                  <th style="text-align: right;">Action</th>
                </tr>
              </thead>
              <tbody id="channels-table-body">
                <tr>
                  <td colspan="6" style="text-align:center; color:var(--text-tertiary); padding:28px;">Loading channels...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- INGESTED MESSAGES -->
      <div class="section-block">
        <div class="section-header-bar">
          <div class="section-heading-text">Live Ingested Messages Queue</div>
          <button class="btn-refresh-clean" onclick="loadMessagesQueue()">Refresh</button>
        </div>
        <div class="clean-table-card">
          <div style="overflow-x: auto;">
            <table class="apple-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Channel</th>
                  <th>Message ID</th>
                  <th>Excerpt</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody id="messages-table-body">
                <tr>
                  <td colspan="5" style="text-align:center; color:var(--text-tertiary); padding:28px;">No messages received yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- EXTRACTED JOBS -->
      <div class="section-block">
        <div class="section-header-bar">
          <div class="section-heading-text">Discovered Recruitment Circulars</div>
          <button class="btn-refresh-clean" onclick="loadJobsList()">Refresh</button>
        </div>
        <div class="clean-table-card">
          <div style="overflow-x: auto;">
            <table class="apple-table">
              <thead>
                <tr>
                  <th>Eligibility</th>
                  <th>Organization</th>
                  <th>Post Name</th>
                  <th>Advertisement</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody id="jobs-table-body">
                <tr>
                  <td colspan="5" style="text-align:center; color:var(--text-tertiary); padding:28px;">No jobs processed yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- ADD CHANNEL MODAL -->
  <div id="modal-add" class="modal-backdrop" onclick="handleModalBackdrop(event)">
    <div class="modal-card">
      <h3 class="modal-title">Add Monitored Channel</h3>
      
      <div class="form-group">
        <label class="form-label">Channel Display Name</label>
        <input type="text" id="add-name" class="apple-input" placeholder="e.g. UPSC Official Updates">
      </div>

      <div class="form-group">
        <label class="form-label">Telegram Address or ID</label>
        <input type="text" id="add-address" class="apple-input" placeholder="e.g. @upscnotifications">
      </div>

      <div class="form-group">
        <label class="form-label">Channel Type</label>
        <select id="add-type" class="apple-select">
          <option value="public" selected>Public Channel</option>
          <option value="private">Private Channel / Group</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Description (Optional)</label>
        <input type="text" id="add-desc" class="apple-input" placeholder="e.g. Civil and Engineering Services">
      </div>

      <div class="modal-actions">
        <button class="btn-secondary-apple" onclick="closeAddModal()">Cancel</button>
        <button class="btn-primary-apple" onclick="submitAddChannel()">Add Channel</button>
      </div>
    </div>
  </div>

  <div class="toast-pill" id="toastPill">Operation completed</div>

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
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-tertiary); padding:28px;">No channels configured. Click "+ Add Channel" to start.</td></tr>';
        return;
      }

      channelsData.forEach(ch => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>
            <label class="ios-switch">
              <input type="checkbox" ${ch.enabled ? 'checked' : ''} onchange="toggleChannel('${ch.id}', this.checked)">
              <span class="switch-slider"></span>
            </label>
          </td>
          <td style="font-weight: 500; color: var(--text-primary);">${escapeHtml(ch.name)}</td>
          <td><span class="code-badge">${escapeHtml(ch.telegram_channel_id)}</span></td>
          <td><span class="type-pill">${ch.type}</span></td>
          <td style="color: var(--text-secondary); max-width: 260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(ch.description || '—')}</td>
          <td style="text-align: right;">
            <button class="btn-delete-clean" onclick="deleteChannel('${ch.id}')">Delete</button>
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
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-tertiary); padding:24px;">No messages received yet.</td></tr>';
          return;
        }

        tbody.innerHTML = '';
        msgs.forEach(m => {
          const tr = document.createElement('tr');
          const isProcessed = m.processing_status === 'PROCESSED';
          const dotClass = isProcessed ? 'dot-green' : (m.processing_status === 'FAILED' ? 'dot-amber' : 'dot-gray');
          tr.innerHTML = `
            <td><span class="status-dot-sm ${dotClass}"></span>${escapeHtml(m.processing_status || 'Ingested')}</td>
            <td style="font-weight: 500;">${escapeHtml(m.channel_identifier || 'external')}</td>
            <td><span class="code-badge">${escapeHtml(m.telegram_message_id)}</span></td>
            <td style="color: var(--text-secondary); max-width: 320px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(m.message_text || '—')}</td>
            <td style="color: var(--text-tertiary); font-size: 12px;">${m.received_at ? new Date(m.received_at).toLocaleTimeString() : '—'}</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error('Error fetching messages queue:', e);
      }
    }

    async function loadJobsList() {
      try {
        const res = await fetch('/api/jobs?limit=25');
        if (!res.ok) return;
        const jobs = await res.json();
        document.getElementById('stat-jobs').innerText = jobs.length;

        const tbody = document.getElementById('jobs-table-body');
        if (jobs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-tertiary); padding:24px;">No jobs processed yet.</td></tr>';
          return;
        }

        tbody.innerHTML = '';
        jobs.forEach(j => {
          const tr = document.createElement('tr');
          const isEligible = j.eligibility_status === 'ELIGIBLE';
          const dotClass = isEligible ? 'dot-green' : (j.eligibility_status === 'UNCERTAIN' ? 'dot-amber' : 'dot-gray');
          tr.innerHTML = `
            <td><span class="status-dot-sm ${dotClass}"></span>${escapeHtml(j.eligibility_status)}</td>
            <td style="font-weight: 500;">${escapeHtml(j.organization || 'Govt')}</td>
            <td style="max-width: 260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(j.post_name || '—')}</td>
            <td><span class="code-badge">${escapeHtml(j.notification_number || '—')}</span></td>
            <td style="color: var(--text-tertiary); font-size: 12px;">${Math.round((j.confidence || 0.9) * 100)}%</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error('Error fetching jobs list:', e);
      }
    }

    async function toggleChannel(channelId, enabled) {
      try {
        const res = await fetch(`/api/channels/${channelId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: enabled })
        });
        if (res.ok) {
          showToast(enabled ? 'Channel enabled' : 'Channel paused');
        } else {
          showToast('Failed to update channel');
          loadChannels();
        }
      } catch (e) {
        showToast('Network error updating channel');
        loadChannels();
      }
    }

    async function deleteChannel(channelId) {
      if (!confirm('Are you sure you want to remove this channel from monitoring?')) return;

      try {
        const res = await fetch(`/api/channels/${channelId}`, { method: 'DELETE' });
        if (res.ok) {
          showToast('Channel removed');
          loadChannels();
        } else {
          showToast('Failed to delete channel');
        }
      } catch (e) {
        showToast('Network error deleting channel');
      }
    }

    function openAddModal() {
      const modal = document.getElementById('modal-add');
      modal.style.display = 'flex';
      setTimeout(() => modal.classList.add('open'), 10);
      document.getElementById('add-name').focus();
    }

    function closeAddModal() {
      const modal = document.getElementById('modal-add');
      modal.classList.remove('open');
      setTimeout(() => modal.style.display = 'none', 200);
    }

    function handleModalBackdrop(e) {
      if (e.target.id === 'modal-add') {
        closeAddModal();
      }
    }

    async function submitAddChannel() {
      const name = document.getElementById('add-name').value.trim();
      const address = document.getElementById('add-address').value.trim();
      const type = document.getElementById('add-type').value;
      const desc = document.getElementById('add-desc').value.trim();

      if (!name || !address) {
        alert('Please enter both Channel Name and Telegram Identifier (@username or ID).');
        return;
      }

      try {
        const res = await fetch('/api/channels', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name,
            telegram_channel_id: address,
            type: type,
            description: desc,
            enabled: true
          })
        });

        if (res.ok) {
          closeAddModal();
          document.getElementById('add-name').value = '';
          document.getElementById('add-address').value = '';
          document.getElementById('add-desc').value = '';
          showToast('Channel added successfully');
          loadChannels();
        } else {
          const err = await res.json();
          alert('Error adding channel: ' + (err.detail || JSON.stringify(err)));
        }
      } catch (e) {
        alert('Network error adding channel: ' + e.message);
      }
    }

    async function fetchRecentMessages() {
      const btn = document.getElementById('btn-scan');
      btn.disabled = true;
      btn.innerText = 'Scanning...';
      showToast('Scanning monitored channels...');

      try {
        const res = await fetch('/api/channels/fetch-recent?limit=15', { method: 'POST' });
        if (res.ok) {
          showToast('Scan complete');
          await loadAllData();
        } else {
          showToast('Scan failed');
        }
      } catch (e) {
        showToast('Network error during scan');
      } finally {
        btn.disabled = false;
        btn.innerText = '⚡ Scan Channels';
      }
    }

    function showToast(msg) {
      const toast = document.getElementById('toastPill');
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => { toast.classList.remove('show'); }, 2500);
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    window.addEventListener('DOMContentLoaded', loadAllData);
  </script>
</body>
</html>
"""
