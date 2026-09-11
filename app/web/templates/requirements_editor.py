"""
HTML Template — Personal Eligibility
Apple Human Interface Guidelines: Settings-app aesthetic.
Centered 720px column. Six grouped sections: Education, Age & Category,
Experience, Job Preferences, Application Fee, Matching.
No admin controls, no technical jargon, no comma-separated fields.
"""
from datetime import date as _date

REQUIREMENTS_EDITOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal Eligibility | Job Alerts</title>
  <meta name="description" content="Set your education, age, experience, and preferences so Job Alerts can match government job notifications to you.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700&display=swap" rel="stylesheet">
  <style>
    /* ─── TOKENS ────────────────────────────────────────────── */
    :root {
      --bg:            #F5F5F7;
      --surface:       #FFFFFF;
      --fill:          #F2F2F7;
      --fill-hover:    #E9E9EF;
      --divider:       rgba(0,0,0,0.10);
      --divider-hard:  #D1D1D6;
      --t1:            #1D1D1F;
      --t2:            #6E6E73;
      --t3:            #AEAEB2;
      --blue:          #0071E3;
      --blue-hover:    #0077ED;
      --blue-light:    rgba(0,113,227,.08);
      --green:         #34C759;
      --red:           #FF3B30;
      --orange:        #FF9F0A;
      --r-sm:          8px;
      --r-md:          12px;
      --r-lg:          16px;
      --r-xl:          20px;
      --r-pill:        9999px;
      --font:          "Inter", -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
      --shadow-card:   0 1px 0 rgba(0,0,0,.06), 0 2px 12px rgba(0,0,0,.04);
    }

    /* ─── RESET ─────────────────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }

    body {
      font-family: var(--font);
      background: var(--bg);
      color: var(--t1);
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }

    /* ─── NAV BAR ────────────────────────────────────────────── */
    .nav {
      position: sticky; top: 0; z-index: 200;
      height: 52px;
      display: flex; align-items: center;
      background: rgba(245,245,247,.88);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border-bottom: 1px solid var(--divider);
      padding: 0 24px;
    }
    .nav-inner {
      max-width: 900px; width: 100%; margin: 0 auto;
      display: flex; align-items: center; justify-content: space-between;
    }
    .nav-brand {
      font-size: 16px; font-weight: 600;
      color: var(--t1); text-decoration: none;
      letter-spacing: -0.01em;
    }
    /* shared nav-tab token — same as jobs & channels pages */
    .nav-tabs { display: flex; gap: 28px; }
    .nav-tab {
      font-size: 13px; font-weight: 500;
      color: var(--t2); text-decoration: none;
      transition: color .15s;
    }
    .nav-tab:hover { color: var(--t1); }
    .nav-tab.active { color: var(--t1); font-weight: 600; }

    /* ─── PAGE SHELL ─────────────────────────────────────────── */
    .page {
      max-width: 720px;
      margin: 0 auto;
      padding: 56px 20px 100px;
    }

    /* ─── HERO ───────────────────────────────────────────────── */
    .hero {
      text-align: center;
      margin-bottom: 44px;
    }
    .hero-title {
      font-size: 32px; font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--t1);
      margin-bottom: 10px;
    }
    .hero-sub {
      font-size: 15px; line-height: 1.55;
      color: var(--t2);
      max-width: 420px;
      margin: 0 auto;
    }

    /* ─── SECTION ────────────────────────────────────────────── */
    .section { margin-bottom: 32px; }
    .section-label {
      font-size: 11px; font-weight: 600;
      letter-spacing: .06em; text-transform: uppercase;
      color: var(--t2);
      padding: 0 16px;
      margin-bottom: 8px;
    }
    .card {
      background: var(--surface);
      border-radius: var(--r-xl);
      box-shadow: var(--shadow-card);
      overflow: hidden;
    }

    /* ─── ROW ────────────────────────────────────────────────── */
    .row {
      display: flex; align-items: center;
      padding: 14px 20px;
      min-height: 54px;
      border-bottom: 1px solid var(--divider);
      gap: 12px;
      transition: background .12s;
    }
    .row:last-child { border-bottom: none; }
    .row-label {
      flex: 1;
      font-size: 15px; font-weight: 400;
      color: var(--t1);
    }
    .row-value {
      font-size: 15px; color: var(--t2);
      display: flex; align-items: center; gap: 6px;
    }
    .row-chevron {
      font-size: 12px; color: var(--t3);
      flex-shrink: 0;
      margin-left: 2px;
    }

    /* native select styled as iOS picker row */
    .row-select {
      appearance: none; -webkit-appearance: none;
      border: none; outline: none;
      background: transparent;
      font-family: inherit;
      font-size: 15px; color: var(--t2);
      cursor: pointer;
      text-align: right;
      padding: 0;
      max-width: 260px;
    }

    .row-input-native {
      border: none; outline: none;
      background: transparent;
      font-family: inherit;
      font-size: 15px; color: var(--t2);
      text-align: right;
      width: 100%;
    }
    .row-input-native::placeholder { color: var(--t3); }

    /* percentage input */
    .pct-wrap {
      display: flex; align-items: center; gap: 4px;
    }
    .pct-input {
      width: 56px; text-align: right;
      border: none; outline: none; background: transparent;
      font-family: inherit; font-size: 15px; color: var(--t2);
    }
    .pct-label { font-size: 15px; color: var(--t2); }

    /* ─── TAG PILLS ──────────────────────────────────────────── */
    .tags-row {
      padding: 14px 20px;
      border-bottom: 1px solid var(--divider);
      display: flex; flex-direction: column; gap: 10px;
    }
    .tags-row:last-child { border-bottom: none; }
    .tags-row-label {
      font-size: 15px; color: var(--t1);
    }
    .tags-wrap {
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    }
    .tag {
      display: inline-flex; align-items: center; gap: 5px;
      background: var(--fill);
      border-radius: var(--r-pill);
      padding: 5px 12px;
      font-size: 13px; font-weight: 500; color: var(--t1);
      transition: background .15s;
    }
    .tag:hover { background: var(--fill-hover); }
    .tag-x {
      cursor: pointer;
      display: inline-flex; align-items: center; justify-content: center;
      width: 15px; height: 15px;
      border-radius: 50%;
      background: rgba(0,0,0,.12);
      color: var(--t2); font-size: 10px;
      transition: background .15s;
      flex-shrink: 0;
    }
    .tag-x:hover { background: rgba(255,59,48,.18); color: var(--red); }
    .tag-add {
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 13px; font-weight: 500;
      color: var(--blue);
      cursor: pointer;
      padding: 5px 4px;
      transition: opacity .15s;
    }
    .tag-add:hover { opacity: .75; }

    /* inline tag input */
    .tag-input-wrap { display: flex; align-items: center; gap: 8px; }
    .tag-input {
      flex: 1;
      border: 1.5px solid var(--blue);
      border-radius: var(--r-pill);
      padding: 5px 12px;
      font-family: inherit; font-size: 13px;
      outline: none; background: var(--surface);
      color: var(--t1);
    }
    .tag-input::placeholder { color: var(--t3); }
    .tag-input-confirm {
      font-size: 13px; font-weight: 600; color: var(--blue);
      background: none; border: none; cursor: pointer;
      padding: 4px;
    }
    .tag-input-cancel {
      font-size: 13px; color: var(--t3);
      background: none; border: none; cursor: pointer;
      padding: 4px;
    }

    /* ─── SEGMENTED CONTROL (Experience / Fee) ───────────────── */
    .segment-row {
      padding: 16px 20px;
      border-bottom: 1px solid var(--divider);
      display: flex; flex-direction: column; gap: 12px;
    }
    .segment-row:last-child { border-bottom: none; }
    .segment-label { font-size: 15px; color: var(--t1); }
    .segmented {
      display: grid;
      background: var(--fill);
      border-radius: var(--r-md);
      padding: 3px;
      gap: 3px;
    }
    .seg-btn {
      border: none; background: transparent;
      font-family: inherit; font-size: 13px; font-weight: 500;
      color: var(--t2); cursor: pointer;
      padding: 8px 4px; border-radius: 9px;
      transition: all .18s cubic-bezier(.4,0,.2,1);
      text-align: center;
    }
    .seg-btn.active {
      background: var(--surface);
      color: var(--t1); font-weight: 600;
      box-shadow: 0 1px 4px rgba(0,0,0,.10);
    }
    .seg-btn:hover:not(.active) { color: var(--t1); }

    /* fee selector — horizontal pills */
    .fee-options {
      display: flex; flex-wrap: wrap; gap: 8px;
    }
    .fee-btn {
      border: 1.5px solid var(--divider-hard);
      background: transparent;
      border-radius: var(--r-pill);
      padding: 6px 16px;
      font-family: inherit; font-size: 14px; font-weight: 500;
      color: var(--t2); cursor: pointer;
      transition: all .15s;
    }
    .fee-btn.active {
      border-color: var(--blue);
      background: var(--blue-light);
      color: var(--blue); font-weight: 600;
    }
    .fee-btn:hover:not(.active) {
      border-color: var(--t2);
      color: var(--t1);
    }
    .fee-hint {
      font-size: 12px; color: var(--t3); line-height: 1.4;
      padding: 0 20px 16px;
    }

    /* ─── MATCHING CARDS ─────────────────────────────────────── */
    .match-options {
      display: flex; flex-direction: column;
    }
    .match-row {
      display: flex; align-items: flex-start; gap: 14px;
      padding: 16px 20px;
      border-bottom: 1px solid var(--divider);
      cursor: pointer;
      transition: background .12s;
    }
    .match-row:last-child { border-bottom: none; }
    .match-row:hover { background: var(--fill); }
    .match-radio-wrap {
      padding-top: 3px;
      flex-shrink: 0;
    }
    .match-info { flex: 1; }
    .match-title {
      font-size: 15px; font-weight: 600; color: var(--t1);
      margin-bottom: 2px;
    }
    .match-desc { font-size: 13px; color: var(--t2); line-height: 1.45; }

    /* ─── RADIO / TOGGLE ─────────────────────────────────────── */
    /* hide native radio, show custom circle */
    input[type="radio"] { display: none; }
    .radio-dot {
      width: 20px; height: 20px;
      border-radius: 50%;
      border: 2px solid var(--divider-hard);
      display: flex; align-items: center; justify-content: center;
      transition: border-color .15s;
      flex-shrink: 0;
    }
    input[type="radio"]:checked + .radio-dot {
      border-color: var(--blue);
      background: var(--blue);
    }
    input[type="radio"]:checked + .radio-dot::after {
      content: "";
      width: 7px; height: 7px;
      border-radius: 50%;
      background: white;
    }

    /* iOS toggle switch */
    .toggle-label {
      position: relative;
      display: inline-block;
      width: 50px; height: 28px;
      flex-shrink: 0;
    }
    .toggle-label input { display: none; }
    .toggle-track {
      position: absolute; inset: 0;
      background: var(--divider-hard);
      border-radius: var(--r-pill);
      transition: background .22s;
    }
    .toggle-thumb {
      position: absolute;
      top: 2px; left: 2px;
      width: 24px; height: 24px;
      border-radius: 50%;
      background: white;
      box-shadow: 0 2px 6px rgba(0,0,0,.22);
      transition: transform .22s cubic-bezier(.4,0,.2,1);
    }
    .toggle-label input:checked ~ .toggle-track { background: var(--green); }
    .toggle-label input:checked ~ .toggle-thumb { transform: translateX(22px); }

    /* ─── SAVE BUTTON ────────────────────────────────────────── */
    .save-area {
      display: flex; flex-direction: column; align-items: center;
      gap: 12px;
      padding-top: 12px;
    }
    .save-btn {
      font-family: inherit;
      font-size: 15px; font-weight: 500;
      color: white; background: var(--blue);
      border: none; border-radius: var(--r-pill);
      padding: 11px 40px;
      cursor: pointer;
      transition: background .15s, transform .1s;
    }
    .save-btn:hover { background: var(--blue-hover); }
    .save-btn:active { transform: scale(.98); }
    .save-btn:disabled { opacity: .55; cursor: not-allowed; }
    .save-status {
      font-size: 13px; color: var(--t3);
      height: 18px; transition: opacity .3s;
    }
    .save-status.visible { color: var(--green); }

    /* ─── TOAST ──────────────────────────────────────────────── */
    .toast {
      position: fixed; bottom: 28px; left: 50%;
      transform: translateX(-50%) translateY(80px);
      background: rgba(29,29,31,.92);
      backdrop-filter: blur(16px);
      color: white; font-size: 13px; font-weight: 500;
      padding: 10px 20px; border-radius: var(--r-pill);
      box-shadow: 0 8px 24px rgba(0,0,0,.18);
      transition: transform .3s cubic-bezier(.16,1,.3,1);
      pointer-events: none; z-index: 900;
      white-space: nowrap;
    }
    .toast.show { transform: translateX(-50%) translateY(0); }

    /* ─── RESPONSIVE ─────────────────────────────────────────── */
    @media (max-width: 600px) {
      .page { padding: 36px 12px 80px; }
      .hero-title { font-size: 26px; }
      .nav-links { gap: 18px; }
    }
  </style>
</head>
<body>

<!-- ── UNIFIED NAV ──────────────────────────────────────────── -->
<header class="nav">
  <div class="nav-inner">
    <a href="/jobs" class="nav-brand">Job Alerts</a>
    <nav class="nav-tabs">
      <a href="/jobs"               class="nav-tab">Jobs</a>
      <a href="/plan-to-apply"      class="nav-tab">⭐ Plan to Apply</a>
      <a href="/applied"            class="nav-tab">✓ Applied</a>
      <a href="/admin/requirements" class="nav-tab active">Profile &amp; Rules</a>
      <a href="/admin/channels"     class="nav-tab">Channels</a>
    </nav>
  </div>
</header>

<!-- ── PAGE ──────────────────────────────────────────────────── -->
<div class="page">

  <!-- HERO -->
  <header class="hero">
    <h1 class="hero-title">Personal Eligibility</h1>
    <p class="hero-sub">Tell us about yourself. We'll use these details to determine which jobs you're eligible for.</p>
  </header>

  <!-- ── 1. EDUCATION ─────────────────────────────────────────── -->
  <section class="section" id="sec-education">
    <p class="section-label">Education</p>
    <div class="card">

      <!-- Highest education -->
      <label class="row" for="edu-level">
        <span class="row-label">Highest education</span>
        <div class="row-value">
          <select id="edu-level" class="row-select">
            <option value="any">Any</option>
            <option value="10th">10th Standard</option>
            <option value="12th">12th Standard</option>
            <option value="diploma">Diploma</option>
            <option value="bachelors" selected>Bachelor's Degree</option>
            <option value="masters">Master's Degree</option>
            <option value="doctorate">Doctorate / Ph.D.</option>
          </select>
          <span class="row-chevron">›</span>
        </div>
      </label>

      <!-- Degree tags -->
      <div class="tags-row" id="degree-section">
        <span class="tags-row-label">Degree</span>
        <div class="tags-wrap" id="degree-tags">
          <!-- populated by JS -->
          <span class="tag-add" onclick="openTagInput('degree-tags','degree-input-row')">
            + Add degree
          </span>
        </div>
        <div class="tag-input-wrap" id="degree-input-row" style="display:none">
          <input id="degree-input" class="tag-input" placeholder="e.g. B.Tech, MCA…"
                 onkeydown="inputKey(event,'degrees','degree-input','degree-input-row','degree-tags')">
          <button class="tag-input-confirm" onclick="confirmTag('degrees','degree-input','degree-input-row','degree-tags')">Done</button>
          <button class="tag-input-cancel"  onclick="cancelTagInput('degree-input','degree-input-row')">Cancel</button>
        </div>
        <!-- presets -->
        <div class="tags-wrap" id="degree-presets" style="gap:6px">
          <span style="font-size:11px;color:var(--t3);margin-right:4px;">Quick add:</span>
          <span class="tag-add" onclick="addTag('degrees','B.E.','degree-tags')">B.E.</span>
          <span class="tag-add" onclick="addTag('degrees','B.Tech','degree-tags')">B.Tech</span>
          <span class="tag-add" onclick="addTag('degrees','B.Sc','degree-tags')">B.Sc</span>
          <span class="tag-add" onclick="addTag('degrees','BCA','degree-tags')">BCA</span>
          <span class="tag-add" onclick="addTag('degrees','MCA','degree-tags')">MCA</span>
          <span class="tag-add" onclick="addTag('degrees','M.Tech','degree-tags')">M.Tech</span>
        </div>
      </div>

      <!-- Discipline tags -->
      <div class="tags-row" id="discipline-section">
        <span class="tags-row-label">Engineering / discipline</span>
        <div class="tags-wrap" id="branch-tags">
          <span class="tag-add" onclick="openTagInput('branch-tags','branch-input-row')">
            + Add discipline
          </span>
        </div>
        <div class="tag-input-wrap" id="branch-input-row" style="display:none">
          <input id="branch-input" class="tag-input" placeholder="e.g. Computer Science, ECE…"
                 onkeydown="inputKey(event,'branches','branch-input','branch-input-row','branch-tags')">
          <button class="tag-input-confirm" onclick="confirmTag('branches','branch-input','branch-input-row','branch-tags')">Done</button>
          <button class="tag-input-cancel"  onclick="cancelTagInput('branch-input','branch-input-row')">Cancel</button>
        </div>
        <div class="tags-wrap" style="gap:6px">
          <span style="font-size:11px;color:var(--t3);margin-right:4px;">Quick add:</span>
          <span class="tag-add" onclick="addTag('branches','Computer Science','branch-tags')">CS</span>
          <span class="tag-add" onclick="addTag('branches','Information Technology','branch-tags')">IT</span>
          <span class="tag-add" onclick="addTag('branches','CSE','branch-tags')">CSE</span>
          <span class="tag-add" onclick="addTag('branches','Electronics','branch-tags')">Electronics</span>
          <span class="tag-add" onclick="addTag('branches','ECE','branch-tags')">ECE</span>
          <span class="tag-add" onclick="addTag('branches','Any Branch','branch-tags')">Any Branch</span>
        </div>
      </div>

      <!-- Minimum percentage -->
      <label class="row" for="min-pct">
        <span class="row-label">Minimum percentage</span>
        <div class="row-value">
          <div class="pct-wrap">
            <input id="min-pct" class="pct-input" type="number" min="0" max="100" step="0.5" value="60">
            <span class="pct-label">%</span>
          </div>
        </div>
      </label>

    </div>
  </section>

  <!-- ── 2. AGE & CATEGORY ────────────────────────────────────── -->
  <section class="section" id="sec-age">
    <p class="section-label">Age &amp; Category</p>
    <div class="card">

      <!-- Date of birth -->
      <label class="row" for="dob">
        <span class="row-label">Date of birth</span>
        <div class="row-value">
          <input id="dob" class="row-input-native" type="date"
                 style="max-width:160px; color-scheme:light;" placeholder="DD / MM / YYYY">
          <span class="row-chevron">›</span>
        </div>
      </label>

      <!-- Reservation category -->
      <label class="row" for="cat-select">
        <span class="row-label">Reservation category</span>
        <div class="row-value">
          <select id="cat-select" class="row-select">
            <option value="General">General (UR)</option>
            <option value="OBC">OBC</option>
            <option value="SC">SC</option>
            <option value="ST">ST</option>
            <option value="EWS">EWS</option>
            <option value="PwD">PwD</option>
          </select>
          <span class="row-chevron">›</span>
        </div>
      </label>

      <!-- Age relaxation note -->
      <div class="row" style="cursor:default">
        <span class="row-label" style="color:var(--t2)">Age relaxation</span>
        <span class="row-value" style="font-size:13px;max-width:240px;text-align:right;line-height:1.4">
          Automatically applied from each official notification
        </span>
      </div>

    </div>
  </section>

  <!-- ── 3. EXPERIENCE ─────────────────────────────────────────── -->
  <section class="section" id="sec-experience">
    <p class="section-label">Experience</p>
    <div class="card">
      <div class="segment-row" style="border-bottom:none;">
        <span class="segment-label">Work experience</span>
        <div class="segmented" id="exp-segmented"
             style="grid-template-columns: repeat(4, 1fr);">
          <button class="seg-btn active" data-val="fresher"  onclick="setExp(this)">Fresher</button>
          <button class="seg-btn"        data-val="0-2"       onclick="setExp(this)">0–2 yrs</button>
          <button class="seg-btn"        data-val="2-5"       onclick="setExp(this)">2–5 yrs</button>
          <button class="seg-btn"        data-val="5+"        onclick="setExp(this)">5+ yrs</button>
        </div>
      </div>
    </div>
  </section>

  <!-- ── 4. JOB PREFERENCES ────────────────────────────────────── -->
  <section class="section" id="sec-prefs">
    <p class="section-label">Job Preferences</p>
    <div class="card">

      <!-- Job sectors / cadres -->
      <div class="tags-row">
        <span class="tags-row-label">Job sectors</span>
        <div class="tags-wrap" id="sector-tags">
          <span class="tag-add" onclick="openTagInput('sector-tags','sector-input-row')">+ Add</span>
        </div>
        <div class="tag-input-wrap" id="sector-input-row" style="display:none">
          <input id="sector-input" class="tag-input" placeholder="e.g. PSU, Banking…"
                 onkeydown="inputKey(event,'sectors','sector-input','sector-input-row','sector-tags')">
          <button class="tag-input-confirm" onclick="confirmTag('sectors','sector-input','sector-input-row','sector-tags')">Done</button>
          <button class="tag-input-cancel"  onclick="cancelTagInput('sector-input','sector-input-row')">Cancel</button>
        </div>
        <div class="tags-wrap" style="gap:6px">
          <span style="font-size:11px;color:var(--t3);margin-right:4px;">Quick add:</span>
          <span class="tag-add" onclick="addTag('sectors','SSC','sector-tags')">SSC</span>
          <span class="tag-add" onclick="addTag('sectors','PSU','sector-tags')">PSU</span>
          <span class="tag-add" onclick="addTag('sectors','Banking','sector-tags')">Banking</span>
          <span class="tag-add" onclick="addTag('sectors','Defense','sector-tags')">Defense</span>
          <span class="tag-add" onclick="addTag('sectors','Railway','sector-tags')">Railway</span>
        </div>
      </div>

      <!-- Preferred locations -->
      <div class="tags-row">
        <span class="tags-row-label">Preferred locations</span>
        <div class="tags-wrap" id="location-tags">
          <span class="tag-add" onclick="openTagInput('location-tags','location-input-row')">+ Add location</span>
        </div>
        <div class="tag-input-wrap" id="location-input-row" style="display:none">
          <input id="location-input" class="tag-input" placeholder="e.g. Telangana, Delhi…"
                 onkeydown="inputKey(event,'locations','location-input','location-input-row','location-tags')">
          <button class="tag-input-confirm" onclick="confirmTag('locations','location-input','location-input-row','location-tags')">Done</button>
          <button class="tag-input-cancel"  onclick="cancelTagInput('location-input','location-input-row')">Cancel</button>
        </div>
        <div class="tags-wrap" style="gap:6px">
          <span style="font-size:11px;color:var(--t3);margin-right:4px;">Quick add:</span>
          <span class="tag-add" onclick="addTag('locations','Telangana','location-tags')">Telangana</span>
          <span class="tag-add" onclick="addTag('locations','Andhra Pradesh','location-tags')">Andhra Pradesh</span>
          <span class="tag-add" onclick="addTag('locations','Karnataka','location-tags')">Karnataka</span>
          <span class="tag-add" onclick="addTag('locations','Delhi','location-tags')">Delhi</span>
          <span class="tag-add" onclick="addTag('locations','Maharashtra','location-tags')">Maharashtra</span>
        </div>
      </div>

      <!-- Include All India toggle -->
      <div class="row">
        <span class="row-label">Include All India opportunities</span>
        <label class="toggle-label" id="all-india-toggle-lbl">
          <input type="checkbox" id="all-india-toggle" checked>
          <div class="toggle-track"></div>
          <div class="toggle-thumb"></div>
        </label>
      </div>

      <!-- Excluded types -->
      <div class="tags-row" style="border-bottom:none;">
        <span class="tags-row-label">Don't show</span>
        <div class="tags-wrap" id="exclude-tags">
          <span class="tag-add" onclick="openTagInput('exclude-tags','exclude-input-row')">+ Add exclusion</span>
        </div>
        <div class="tag-input-wrap" id="exclude-input-row" style="display:none">
          <input id="exclude-input" class="tag-input" placeholder="e.g. Contract, Part-time…"
                 onkeydown="inputKey(event,'exclusions','exclude-input','exclude-input-row','exclude-tags')">
          <button class="tag-input-confirm" onclick="confirmTag('exclusions','exclude-input','exclude-input-row','exclude-tags')">Done</button>
          <button class="tag-input-cancel"  onclick="cancelTagInput('exclude-input','exclude-input-row')">Cancel</button>
        </div>
        <div class="tags-wrap" style="gap:6px">
          <span style="font-size:11px;color:var(--t3);margin-right:4px;">Common:</span>
          <span class="tag-add" onclick="addTag('exclusions','Contract','exclude-tags')">Contract</span>
          <span class="tag-add" onclick="addTag('exclusions','Internship','exclude-tags')">Internship</span>
          <span class="tag-add" onclick="addTag('exclusions','Part-time','exclude-tags')">Part-time</span>
        </div>
      </div>

    </div>
  </section>

  <!-- ── 5. APPLICATION FEE ─────────────────────────────────────── -->
  <section class="section" id="sec-fee">
    <p class="section-label">Application Fee</p>
    <div class="card">
      <div class="segment-row" style="border-bottom:none;">
        <span class="segment-label">Maximum application fee you're willing to pay</span>
        <div class="fee-options" id="fee-options">
          <button class="fee-btn" data-val="0"    onclick="setFee(this)">₹0</button>
          <button class="fee-btn" data-val="100"  onclick="setFee(this)">₹100</button>
          <button class="fee-btn active" data-val="250" onclick="setFee(this)">₹250</button>
          <button class="fee-btn" data-val="500"  onclick="setFee(this)">₹500</button>
          <button class="fee-btn" data-val="1000" onclick="setFee(this)">₹1,000</button>
          <button class="fee-btn" data-val=""     onclick="setFee(this)">Any</button>
        </div>
      </div>
      <p class="fee-hint">We'll consider category-based fee exemptions automatically.</p>
    </div>
  </section>

  <!-- ── 6. MATCHING ───────────────────────────────────────────── -->
  <section class="section" id="sec-matching">
    <p class="section-label">Matching</p>
    <div class="card">

      <p style="font-size:13px;color:var(--t2);padding:14px 20px 4px;border-bottom:1px solid var(--divider);">
        How strictly should we match jobs?
      </p>

      <div class="match-options" id="match-options">

        <label class="match-row" for="match-strict">
          <div class="match-radio-wrap">
            <input type="radio" id="match-strict" name="match" value="strict">
            <div class="radio-dot"></div>
          </div>
          <div class="match-info">
            <div class="match-title">Strict</div>
            <div class="match-desc">Only show jobs where your eligibility is clearly satisfied.</div>
          </div>
        </label>

        <label class="match-row" for="match-balanced">
          <div class="match-radio-wrap">
            <input type="radio" id="match-balanced" name="match" value="balanced" checked>
            <div class="radio-dot"></div>
          </div>
          <div class="match-info">
            <div class="match-title">Balanced</div>
            <div class="match-desc">Show eligible jobs and jobs requiring minor verification.</div>
          </div>
        </label>

        <label class="match-row" for="match-broad">
          <div class="match-radio-wrap">
            <input type="radio" id="match-broad" name="match" value="broad">
            <div class="radio-dot"></div>
          </div>
          <div class="match-info">
            <div class="match-title">Broad</div>
            <div class="match-desc">Show potentially suitable jobs even when some requirements need verification.</div>
          </div>
        </label>

      </div>

      <!-- Ambiguous toggle -->
      <div class="row" style="border-top:1px solid var(--divider);">
        <div style="flex:1">
          <div class="row-label">Show jobs with unclear eligibility</div>
          <div style="font-size:12px;color:var(--t3);margin-top:2px;max-width:440px;line-height:1.4;">
            Some notifications use unusual wording. We'll flag these instead of auto-rejecting them.
          </div>
        </div>
        <label class="toggle-label">
          <input type="checkbox" id="alert-uncertain" checked>
          <div class="toggle-track"></div>
          <div class="toggle-thumb"></div>
        </label>
      </div>

    </div>
  </section>

  <!-- ── SAVE ─────────────────────────────────────────────────── -->
  <div class="save-area">
    <button class="save-btn" id="save-btn" onclick="saveProfile()">Save Changes</button>
    <span class="save-status" id="save-status"></span>
  </div>

</div><!-- .page -->

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ─── STATE ───────────────────────────────────────────────────────
const S = {
  degrees:    [],
  branches:   [],
  sectors:    [],
  locations:  [],
  exclusions: [],
  expVal:     'fresher',   // fresher | 0-2 | 2-5 | 5+
  feeVal:     '250',       // '' = any, '0','100','250','500','1000'
  matchMode:  'balanced',
};

// ─── LOAD FROM API ───────────────────────────────────────────────
async function loadProfile() {
  try {
    const res = await fetch('/api/requirements');
    if (!res.ok) return;
    const d = await res.json();

    /* Education */
    if (d.education) {
      document.getElementById('edu-level').value = d.education.minimum_level || 'bachelors';
      document.getElementById('min-pct').value   = d.education.minimum_percentage ?? 60;
      S.degrees  = [...(d.education.accepted_degrees || [])];
      S.branches = [...(d.education.branches || [])];
    }

    /* Age & DOB */
    if (d.date_of_birth) document.getElementById('dob').value = d.date_of_birth;
    if (d.age) document.getElementById('cat-select').value = d.age.category || 'General';

    /* Experience → derive bucket */
    if (d.experience) {
      const fresher  = d.experience.fresher_allowed;
      const maxYears = d.experience.max_years_experience_required ?? 0;
      if (fresher && maxYears === 0) S.expVal = 'fresher';
      else if (maxYears <= 2)       S.expVal = '0-2';
      else if (maxYears <= 5)       S.expVal = '2-5';
      else                          S.expVal = '5+';
    }

    /* Job categories → sectors */
    const catMap = {
      central_government: 'Central Govt',
      state_government:   'State Govt',
      psu:                'PSU',
      banking:            'Banking',
      defense:            'Defense',
      autonomous_body:    'Autonomous',
    };
    if (d.job_categories) {
      S.sectors = d.job_categories.map(c => catMap[c] || c);
    }

    /* Locations */
    if (d.location?.allowed) {
      const locs = d.location.allowed.filter(l => l !== 'All India' && l !== 'India');
      S.locations = locs;
      document.getElementById('all-india-toggle').checked =
        d.location.allowed.some(l => l === 'All India' || l === 'India');
    }

    /* Exclusions */
    if (d.excluded_types) S.exclusions = [...d.excluded_types];

    /* Fee */
    if (d.max_application_fee != null) S.feeVal = String(d.max_application_fee);
    else if (d.max_application_fee === null) S.feeVal = '';

    /* Matching */
    if (d.matching_mode) S.matchMode = d.matching_mode;
    if (d.notification_preferences?.alert_on_uncertain != null) {
      document.getElementById('alert-uncertain').checked =
        !!d.notification_preferences.alert_on_uncertain;
    }

  } catch (e) {
    console.error('loadProfile error:', e);
  }

  renderAll();
}

// ─── RENDER ──────────────────────────────────────────────────────
function renderAll() {
  renderTags('degrees',   'degree-tags',   'degree-input-row');
  renderTags('branches',  'branch-tags',   'branch-input-row');
  renderTags('sectors',   'sector-tags',   'sector-input-row');
  renderTags('locations', 'location-tags', 'location-input-row');
  renderTags('exclusions','exclude-tags',  'exclude-input-row');
  syncExpButtons();
  syncFeeButtons();
  syncMatchRadios();
}

function renderTags(stateKey, containerId, inputRowId) {
  const wrap = document.getElementById(containerId);
  if (!wrap) return;

  // collect nodes that are NOT tags (add-button, input row placeholder)
  const toKeep = [...wrap.querySelectorAll('.tag-add, .tag-input-wrap')];

  // rebuild
  wrap.innerHTML = '';
  S[stateKey].forEach((val, idx) => {
    const pill = document.createElement('span');
    pill.className = 'tag';
    pill.innerHTML = `${esc(val)}<span class="tag-x" onclick="removeTag('${stateKey}','${containerId}','${inputRowId}',${idx})">×</span>`;
    wrap.appendChild(pill);
  });

  // restore add button
  const addBtn = document.createElement('span');
  addBtn.className = 'tag-add';
  const addLabels = {
    degrees:'+ Add degree', branches:'+ Add discipline',
    sectors:'+ Add', locations:'+ Add location', exclusions:'+ Add exclusion'
  };
  addBtn.textContent = addLabels[stateKey] || '+ Add';
  addBtn.setAttribute('onclick', `openTagInput('${containerId}','${inputRowId}')`);
  wrap.appendChild(addBtn);
}

// ─── TAG HELPERS ─────────────────────────────────────────────────
function addTag(stateKey, value, containerId) {
  const v = (value || '').trim();
  if (!v || S[stateKey].includes(v)) return;
  S[stateKey].push(v);
  // figure out inputRowId from containerId
  const map = {
    'degree-tags':'degree-input-row','branch-tags':'branch-input-row',
    'sector-tags':'sector-input-row','location-tags':'location-input-row',
    'exclude-tags':'exclude-input-row'
  };
  renderTags(stateKey, containerId, map[containerId] || '');
}

function removeTag(stateKey, containerId, inputRowId, idx) {
  S[stateKey].splice(idx, 1);
  renderTags(stateKey, containerId, inputRowId);
}

function openTagInput(containerId, inputRowId) {
  document.getElementById(inputRowId).style.display = 'flex';
  const inputMap = {
    'degree-input-row':'degree-input','branch-input-row':'branch-input',
    'sector-input-row':'sector-input','location-input-row':'location-input',
    'exclude-input-row':'exclude-input'
  };
  const inp = document.getElementById(inputMap[inputRowId]);
  if (inp) { inp.value = ''; inp.focus(); }
}

function cancelTagInput(inputId, inputRowId) {
  document.getElementById(inputId).value = '';
  document.getElementById(inputRowId).style.display = 'none';
}

function confirmTag(stateKey, inputId, inputRowId, containerId) {
  const v = document.getElementById(inputId).value.trim();
  if (v) addTag(stateKey, v, containerId);
  cancelTagInput(inputId, inputRowId);
}

function inputKey(e, stateKey, inputId, inputRowId, containerId) {
  if (e.key === 'Enter') { e.preventDefault(); confirmTag(stateKey, inputId, inputRowId, containerId); }
  if (e.key === 'Escape') cancelTagInput(inputId, inputRowId);
}

// ─── EXPERIENCE SEGMENTED ────────────────────────────────────────
function setExp(btn) {
  S.expVal = btn.dataset.val;
  syncExpButtons();
}
function syncExpButtons() {
  document.querySelectorAll('#exp-segmented .seg-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.val === S.expVal);
  });
}

// ─── FEE SELECTOR ────────────────────────────────────────────────
function setFee(btn) {
  S.feeVal = btn.dataset.val;
  syncFeeButtons();
}
function syncFeeButtons() {
  document.querySelectorAll('#fee-options .fee-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.val === S.feeVal);
  });
}

// ─── MATCHING ────────────────────────────────────────────────────
function syncMatchRadios() {
  const r = document.querySelector(`input[name="match"][value="${S.matchMode}"]`);
  if (r) r.checked = true;
}

// ─── SAVE ────────────────────────────────────────────────────────
async function saveProfile() {
  const btn = document.getElementById('save-btn');
  btn.disabled = true;
  btn.textContent = 'Saving…';

  /* ── derive experience fields from bucket ── */
  const expMap = {
    'fresher': { fresher_allowed: true,  max_years_experience_required: 0 },
    '0-2':     { fresher_allowed: true,  max_years_experience_required: 2 },
    '2-5':     { fresher_allowed: false, max_years_experience_required: 5 },
    '5+':      { fresher_allowed: false, max_years_experience_required: 10 },
  };
  const expFields = expMap[S.expVal] || expMap['fresher'];

  /* ── derive age.maximum from DOB ── */
  const dobVal = document.getElementById('dob').value;
  let ageMax = 30;
  if (dobVal) {
    const today = new Date();
    const dob   = new Date(dobVal);
    ageMax = today.getFullYear() - dob.getFullYear() -
             ((today.getMonth() < dob.getMonth() ||
               (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate())) ? 1 : 0);
    if (ageMax < 1 || ageMax > 80) ageMax = 30;
  }

  /* ── locations ── */
  const locs = [...S.locations];
  if (document.getElementById('all-india-toggle').checked) locs.unshift('All India');

  /* ── sectors → job_categories ── */
  const sectorCatMap = {
    'Central Govt':'central_government', 'State Govt':'state_government',
    'PSU':'psu', 'Banking':'banking', 'Defense':'defense',
    'Autonomous':'autonomous_body', 'SSC':'central_government',
    'Railway':'central_government',
  };
  const jobCategories = S.sectors.map(s => sectorCatMap[s] || s.toLowerCase().replace(/\s+/g,'_'));

  /* ── matching → alert_on_uncertain ── */
  const alertOnUncertain = document.getElementById('alert-uncertain').checked;
  const matchVal = document.querySelector('input[name="match"]:checked')?.value || 'balanced';

  const payload = {
    education: {
      minimum_level:       document.getElementById('edu-level').value,
      accepted_degrees:    S.degrees.length ? S.degrees : ['B.Tech'],
      branches:            S.branches.length ? S.branches : ['Any Branch'],
      minimum_percentage:  parseFloat(document.getElementById('min-pct').value) || 0,
    },
    age: {
      maximum:  ageMax,
      category: document.getElementById('cat-select').value,
      category_age_relaxations: { OBC: 3, SC: 5, ST: 5, PwD: 10, 'Ex-Serviceman': 5 },
    },
    experience: expFields,
    job_categories:   jobCategories.length ? jobCategories : ['central_government','state_government','psu'],
    location:         { allowed: locs, exclude_locations: [] },
    excluded_types:   S.exclusions,
    notification_preferences: {
      alert_on_uncertain:    alertOnUncertain,
      min_vacancies:         1,
      min_salary_inr_month:  0,
    },
    date_of_birth:       dobVal || null,
    max_application_fee: S.feeVal === '' ? null : parseInt(S.feeVal, 10),
    matching_mode:       matchVal,
  };

  try {
    const res = await fetch('/api/requirements', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      showStatus('Changes saved');
      showToast('✓ Changes saved');
    } else {
      showToast('Failed to save changes');
    }
  } catch {
    showToast('Network error — please retry');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Changes';
  }
}

// ─── UI HELPERS ──────────────────────────────────────────────────
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2800);
}
function showStatus(msg) {
  const el = document.getElementById('save-status');
  el.textContent = msg;
  el.classList.add('visible');
  setTimeout(() => { el.textContent = ''; el.classList.remove('visible'); }, 3000);
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' })[c]);
}

window.addEventListener('DOMContentLoaded', loadProfile);
</script>
</body>
</html>
"""
