"""
HTML Template for User Requirements Editor & Dashboard
Provides a premium, responsive Web UI to view and edit eligibility requirements:
- Minimum Education & Accepted Degrees
- Engineering & General Branches
- Age Limits & Category Relaxations
- Experience & Fresher Eligibility
- Job Categories & Excluded Types
- Real-time JSON schema validation and instant save to PostgreSQL.
"""

REQUIREMENTS_EDITOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>User Eligibility Profile & System Management</title>
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
      padding: 16px 32px;
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
      font-size: 14px;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      box-shadow: 0 0 15px var(--accent-blue-glow);
    }

    .brand-title {
      font-size: 18px;
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

    .header-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .btn {
      font-family: var(--font-sans);
      font-weight: 500;
      font-size: 14px;
      padding: 9px 18px;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .btn-primary {
      background: var(--accent-blue);
      color: #fff;
      box-shadow: 0 4px 14px var(--accent-blue-glow);
    }

    .btn-primary:hover {
      background: #2563EB;
      box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
      transform: translateY(-1px);
    }

    .btn-secondary {
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
      background: #24314C;
      border-color: rgba(255, 255, 255, 0.15);
    }

    .container {
      max-width: 1100px;
      width: 100%;
      margin: 32px auto;
      padding: 0 24px;
    }

    .hero-banner {
      background: linear-gradient(180deg, var(--bg-surface) 0%, rgba(19, 27, 42, 0.4) 100%);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 28px 32px;
      margin-bottom: 32px;
      position: relative;
      overflow: hidden;
    }

    .hero-banner::after {
      content: '';
      position: absolute;
      top: -50px;
      right: -50px;
      width: 250px;
      height: 250px;
      background: radial-gradient(circle, var(--accent-blue-glow) 0%, transparent 70%);
      pointer-events: none;
    }

    .hero-title {
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 8px;
      letter-spacing: -0.02em;
    }

    .hero-subtitle {
      color: var(--text-secondary);
      font-size: 14px;
      max-width: 700px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    @media (max-width: 800px) {
      .grid-2 {
        grid-template-columns: 1fr;
      }
    }

    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      transition: border-color 0.2s;
    }

    .card:hover {
      border-color: rgba(255, 255, 255, 0.14);
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 14px;
    }

    .card-title {
      font-size: 16px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .card-title-icon {
      font-size: 18px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
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
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      font-size: 14px;
      font-family: var(--font-sans);
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .form-control:focus {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px var(--accent-blue-glow);
    }

    .tags-input-container {
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      min-height: 48px;
    }

    .tag-item {
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .tag-remove {
      cursor: pointer;
      color: var(--text-muted);
      font-weight: bold;
    }

    .tag-remove:hover {
      color: var(--accent-rose);
    }

    .toggle-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
    }

    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 44px;
      height: 24px;
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
      transition: .3s;
      border-radius: 24px;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .3s;
      border-radius: 50%;
    }

    input:checked + .slider {
      background-color: var(--accent-blue);
    }

    input:checked + .slider:before {
      transform: translateX(20px);
    }

    .toast {
      position: fixed;
      bottom: 32px;
      right: 32px;
      background: #1E293B;
      color: #fff;
      padding: 14px 20px;
      border-radius: var(--radius-md);
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      border-left: 4px solid var(--accent-emerald);
      display: none;
      align-items: center;
      gap: 12px;
      z-index: 1000;
      font-size: 14px;
      animation: slideIn 0.3s ease;
    }

    @keyframes slideIn {
      from { transform: translateX(50px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span class="brand-badge">GOVT JOB AI</span>
      <span class="brand-title">Eligibility Profile & Rules Editor</span>
    </div>
    <div class="nav-links">
      <a href="/admin/requirements" class="nav-link active">🎓 Eligibility Rules</a>
      <a href="/admin/channels" class="nav-link">📢 Monitored Channels</a>
    </div>
    <div class="header-actions">
      <button class="btn btn-secondary" onclick="resetToDefaults()">Reset to Defaults</button>
      <button class="btn btn-primary" onclick="saveRequirements()">Save Requirements</button>
    </div>
  </header>

  <main class="container">
    <section class="hero-banner">
      <h1 class="hero-title">Your Personal Eligibility Profile</h1>
      <p class="hero-subtitle">
        The deterministic eligibility engine evaluates every extracted government circular against the rules configured below.
        Any requirement you fail will classify the notification as <code>NOT_ELIGIBLE</code>. Any ambiguous condition triggers a <code>UNCERTAIN</code> review alert.
      </p>
    </section>

    <div class="grid-2">
      <!-- CARD 1: EDUCATION & BRANCHES -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span class="card-title-icon">🎓</span>
            <span>Education & Degrees</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Minimum Education Level</label>
          <select id="minimum_level" class="form-control">
            <option value="any">Any Education</option>
            <option value="10th">10th Standard / Matriculation</option>
            <option value="12th">12th Standard / Intermediate</option>
            <option value="diploma">Diploma / Polytechnic</option>
            <option value="bachelors" selected>Bachelor's Degree / Graduation</option>
            <option value="masters">Master's Degree / Post-Graduation</option>
            <option value="doctorate">Doctorate / Ph.D.</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Accepted Degrees (comma-separated)</label>
          <input type="text" id="accepted_degrees" class="form-control" value="B.E., B.Tech, B.Sc, BCA, MCA, M.Tech, Graduation">
        </div>

        <div class="form-group">
          <label class="form-label">Accepted Branches / Disciplines (comma-separated)</label>
          <input type="text" id="branches" class="form-control" value="Computer Science, Information Technology, CSE, IT, Electronics, ECE, Any Branch">
        </div>

        <div class="form-group">
          <label class="form-label">Minimum Aggregate Percentage Required</label>
          <input type="number" id="minimum_percentage" class="form-control" value="60" min="0" max="100">
        </div>
      </div>

      <!-- CARD 2: AGE & RESERVATION -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span class="card-title-icon">🎂</span>
            <span>Age & Reservation Category</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Your Maximum Base Age Limit</label>
          <input type="number" id="age_maximum" class="form-control" value="30" min="18" max="65">
        </div>

        <div class="form-group">
          <label class="form-label">Reservation Category</label>
          <select id="category" class="form-control">
            <option value="General" selected>General / Unreserved (UR)</option>
            <option value="OBC">Other Backward Class (OBC)</option>
            <option value="SC">Scheduled Caste (SC)</option>
            <option value="ST">Scheduled Tribe (ST)</option>
            <option value="EWS">Economically Weaker Section (EWS)</option>
            <option value="PwD">Person with Benchmark Disability (PwD)</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Category Age Relaxations (Years)</label>
          <input type="text" id="age_relaxations" class="form-control" value="OBC: 3, SC: 5, ST: 5, PwD: 10, Ex-Serviceman: 5">
        </div>
      </div>

      <!-- CARD 3: EXPERIENCE & FRESHER STATUS -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span class="card-title-icon">💼</span>
            <span>Experience & Employment</span>
          </div>
        </div>

        <div class="toggle-row">
          <div>
            <div class="form-label" style="color:var(--text-primary);">Accept Fresher Positions</div>
            <div style="font-size:12px; color:var(--text-muted);">Match jobs requiring 0 years experience</div>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" id="fresher_allowed" checked>
            <span class="slider"></span>
          </label>
        </div>

        <div class="form-group">
          <label class="form-label">Maximum Years of Experience You Possess</label>
          <input type="number" id="max_years_experience" class="form-control" value="2" min="0" max="30">
        </div>

        <div class="form-group">
          <label class="form-label">Excluded Job / Post Types (comma-separated)</label>
          <input type="text" id="excluded_types" class="form-control" value="internship, unpaid_volunteer, ad_hoc_short_term">
        </div>
      </div>

      <!-- CARD 4: PREFERENCES & LOCATIONS -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <span class="card-title-icon">📍</span>
            <span>Locations & Alerts</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Allowed Locations (comma-separated)</label>
          <input type="text" id="allowed_locations" class="form-control" value="All India, India, Delhi, Telangana, Andhra Pradesh, Karnataka, Maharashtra">
        </div>

        <div class="form-group">
          <label class="form-label">Preferred Job Categories (comma-separated)</label>
          <input type="text" id="job_categories" class="form-control" value="central_government, state_government, psu, banking, defense, autonomous_body">
        </div>

        <div class="toggle-row">
          <div>
            <div class="form-label" style="color:var(--text-primary);">Alert on Uncertain Notifications</div>
            <div style="font-size:12px; color:var(--text-muted);">Receive 🟡 UNCERTAIN alerts when circular excerpt is ambiguous</div>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" id="alert_on_uncertain" checked>
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </div>
  </main>

  <div id="toast" class="toast">
    <span>✅ User requirements saved and synced to database!</span>
  </div>

  <script>
    async function loadRequirements() {
      try {
        const res = await fetch('/api/requirements');
        if (!res.ok) return;
        const data = await res.json();
        
        if (data.education) {
          document.getElementById('minimum_level').value = data.education.minimum_level || 'bachelors';
          document.getElementById('accepted_degrees').value = (data.education.accepted_degrees || []).join(', ');
          document.getElementById('branches').value = (data.education.branches || []).join(', ');
          document.getElementById('minimum_percentage').value = data.education.minimum_percentage || 60;
        }
        if (data.age) {
          document.getElementById('age_maximum').value = data.age.maximum || 30;
          document.getElementById('category').value = data.age.category || 'General';
          if (data.age.category_age_relaxations) {
            const rels = Object.entries(data.age.category_age_relaxations).map(([k, v]) => `${k}: ${v}`).join(', ');
            document.getElementById('age_relaxations').value = rels;
          }
        }
        if (data.experience) {
          document.getElementById('fresher_allowed').checked = !!data.experience.fresher_allowed;
          document.getElementById('max_years_experience').value = data.experience.max_years_experience_required ?? 2;
        }
        if (data.excluded_types) {
          document.getElementById('excluded_types').value = data.excluded_types.join(', ');
        }
        if (data.location && data.location.allowed) {
          document.getElementById('allowed_locations').value = data.location.allowed.join(', ');
        }
        if (data.job_categories) {
          document.getElementById('job_categories').value = data.job_categories.join(', ');
        }
        if (data.notification_preferences) {
          document.getElementById('alert_on_uncertain').checked = !!data.notification_preferences.alert_on_uncertain;
        }
      } catch (e) {
        console.error('Failed to load profile:', e);
      }
    }

    async function saveRequirements() {
      const splitList = (id) => document.getElementById(id).value.split(',').map(s => s.trim()).filter(Boolean);

      // Parse relaxations dict
      const relsStr = document.getElementById('age_relaxations').value;
      const relaxations = {};
      relsStr.split(',').forEach(item => {
        const parts = item.split(':');
        if (parts.length === 2) {
          relaxations[parts[0].trim()] = parseInt(parts[1].trim(), 10) || 0;
        }
      });

      const payload = {
        education: {
          minimum_level: document.getElementById('minimum_level').value,
          accepted_degrees: splitList('accepted_degrees'),
          branches: splitList('branches'),
          minimum_percentage: parseFloat(document.getElementById('minimum_percentage').value) || 0.0
        },
        age: {
          maximum: parseInt(document.getElementById('age_maximum').value, 10) || 30,
          category: document.getElementById('category').value,
          category_age_relaxations: relaxations
        },
        experience: {
          fresher_allowed: document.getElementById('fresher_allowed').checked,
          max_years_experience_required: parseInt(document.getElementById('max_years_experience').value, 10) || 0
        },
        excluded_types: splitList('excluded_types'),
        location: {
          allowed: splitList('allowed_locations'),
          exclude_locations: []
        },
        job_categories: splitList('job_categories'),
        notification_preferences: {
          alert_on_uncertain: document.getElementById('alert_on_uncertain').checked,
          min_vacancies: 1,
          min_salary_inr_month: 0
        }
      };

      try {
        const res = await fetch('/api/requirements', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('✅ Requirements saved successfully to database!');
        } else {
          const err = await res.json();
          alert('Error saving requirements: ' + JSON.stringify(err));
        }
      } catch (e) {
        alert('Network error saving requirements: ' + e.message);
      }
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.querySelector('span').innerText = msg;
      toast.style.display = 'flex';
      setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }

    async function resetToDefaults() {
      if (confirm('Reset eligibility rules to system defaults?')) {
        location.reload();
      }
    }

    window.addEventListener('DOMContentLoaded', loadRequirements);
  </script>
</body>
</html>
"""
