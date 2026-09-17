"""
HTML Template — Complete Personal Job Eligibility & Preference Profile
Apple Human Interface Guidelines: Structured Settings aesthetic with 4 distinct tiers:
- Tier A: Hard Eligibility (Personal facts, Reservation, 10th Form, 12th Form, B.Tech Form, Branch Matrix, Experience, Licences, Physical & Medical)
- Tier B: Personal Preferences (Sectors, Organizations, Roles, Work Nature, Job Security, Locations, Salary)
- Tier C: Practical Constraints (Application Fee, Exam Travel, Bonds, Selection Process, Hard Exclusions)
- Tier D: Application Readiness (Document Readiness Checklist, EWS/Caste validity, Licences, NOC)
Includes smart conditional form disclosure, dedicated separate forms for 10th, 12th, and B.Tech with dual percentage/CGPA inputs, live summary card, and instant re-evaluation.
"""

REQUIREMENTS_EDITOR_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal Profile &amp; Preferences | Job Alerts</title>
  <meta name="description" content="Set your comprehensive qualifications, job preferences, constraints, and document readiness to accurately classify government job notifications.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:            #F5F5F7;
      --surface:       #FFFFFF;
      --fill:          #F2F2F7;
      --fill-hover:    #E9E9EF;
      --divider:       rgba(0,0,0,0.08);
      --divider-hard:  #D1D1D6;
      --t1:            #1D1D1F;
      --t2:            #6E6E73;
      --t3:            #AEAEB2;
      --blue:          #0071E3;
      --blue-hover:    #0077ED;
      --blue-light:    rgba(0,113,227,.08);
      --green:         #34C759;
      --green-bg:      #E8F5E9;
      --red:           #FF3B30;
      --red-bg:        #FEECEB;
      --orange:        #FF9F0A;
      --orange-bg:     #FFF4E5;
      --purple:        #5856D6;
      --purple-bg:     #F2F1FD;
      --r-sm:          8px;
      --r-md:          12px;
      --r-lg:          16px;
      --r-xl:          20px;
      --r-pill:        9999px;
      --font:          "Inter", -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
      --font-mono:     "JetBrains Mono", Menlo, monospace;
      --shadow-card:   0 1px 0 rgba(0,0,0,.06), 0 2px 12px rgba(0,0,0,.04);
      --shadow-modal:  0 8px 32px rgba(0,0,0,.14);
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: var(--font);
      background: var(--bg);
      color: var(--t1);
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* NAV */
    .nav {
      position: sticky; top: 0; z-index: 200;
      background: rgba(245,245,247,.88);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border-bottom: 1px solid var(--divider);
    }
    .nav-inner {
      max-width: 980px; width: 100%; margin: 0 auto;
      height: 52px; display: flex; align-items: center; justify-content: space-between;
      padding: 0 24px;
    }
    .nav-brand {
      font-size: 16px; font-weight: 600; color: var(--t1); text-decoration: none;
      letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px;
    }
    .nav-brand span.badge-beta {
      font-size: 11px; background: var(--blue-light); color: var(--blue);
      padding: 2px 8px; border-radius: var(--r-pill); font-weight: 600;
    }
    .nav-tabs { display: flex; gap: 20px; }
    .nav-tab {
      font-size: 13px; font-weight: 500; color: var(--t2); text-decoration: none;
      transition: color .15s;
    }
    .nav-tab:hover { color: var(--t1); }
    .nav-tab.active { color: var(--blue); font-weight: 600; }

    /* SUB-NAV QUICK JUMP */
    .subnav {
      max-width: 980px; width: 100%; margin: 0 auto;
      display: flex; gap: 8px; padding: 10px 24px; overflow-x: auto;
      border-top: 1px solid rgba(0,0,0,.04);
    }
    .subnav-link {
      font-size: 12px; font-weight: 500; text-decoration: none;
      padding: 5px 12px; border-radius: var(--r-pill); white-space: nowrap;
      background: var(--surface); color: var(--t2); border: 1px solid var(--divider);
      transition: all .15s;
    }
    .subnav-link:hover { color: var(--t1); border-color: var(--divider-hard); }
    .subnav-link.active-hard { background: var(--red-bg); color: var(--red); border-color: transparent; }
    .subnav-link.active-pref { background: var(--blue-light); color: var(--blue); border-color: transparent; }
    .subnav-link.active-cons { background: var(--orange-bg); color: var(--orange); border-color: transparent; }
    .subnav-link.active-ready { background: var(--purple-bg); color: var(--purple); border-color: transparent; }

    /* PAGE */
    .page {
      max-width: 880px;
      width: 100%;
      margin: 0 auto;
      padding: 36px 20px 140px;
    }

    .hero { text-align: center; margin-bottom: 36px; }
    .hero-title {
      font-size: 32px; font-weight: 700; letter-spacing: -0.025em;
      color: var(--t1); margin-bottom: 8px;
    }
    .hero-sub {
      font-size: 15px; color: var(--t2); line-height: 1.5; max-width: 660px; margin: 0 auto;
    }
    .hero-layers {
      display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-top: 18px;
    }
    .layer-pill {
      font-size: 11.5px; font-weight: 600; padding: 4px 12px; border-radius: var(--r-pill);
      display: inline-flex; align-items: center; gap: 6px;
    }
    .layer-pill-hard { background: var(--red-bg); color: var(--red); }
    .layer-pill-pref { background: var(--blue-light); color: var(--blue); }
    .layer-pill-cons { background: var(--orange-bg); color: var(--orange); }
    .layer-pill-ready { background: var(--purple-bg); color: var(--purple); }

    /* SECTIONS */
    .section { margin-bottom: 32px; }
    .section-label {
      font-size: 12px; font-weight: 700; text-transform: uppercase;
      letter-spacing: .06em; margin-bottom: 8px; padding-left: 4px;
      display: flex; align-items: center; justify-content: space-between;
    }
    .section-badge {
      font-size: 11px; font-weight: 600; padding: 3px 9px;
      border-radius: var(--r-pill); text-transform: none; letter-spacing: 0;
    }
    .badge-hard { background: var(--red-bg); color: var(--red); }
    .badge-pref { background: var(--blue-light); color: var(--blue); }
    .badge-cons { background: var(--orange-bg); color: var(--orange); }
    .badge-ready { background: var(--purple-bg); color: var(--purple); }

    /* CARDS */
    .card {
      background: var(--surface);
      border-radius: var(--r-lg);
      box-shadow: var(--shadow-card);
      overflow: hidden;
      border: 1px solid rgba(0,0,0,.04);
    }
    .card-divider { border-top: 1px solid var(--divider); }
    .card-inner-pad { padding: 18px 20px; }

    /* ROWS */
    .row {
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 20px; min-height: 54px;
      border-bottom: 1px solid var(--divider);
      gap: 16px;
    }
    .row:last-child { border-bottom: none; }
    .row-label { font-size: 14px; font-weight: 500; color: var(--t1); }
    .row-subtext { font-size: 12px; color: var(--t2); margin-top: 2px; }
    .row-value { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

    /* INPUTS & SELECTS */
    .row-input-text, .row-select {
      font-family: var(--font); font-size: 13.5px;
      background: var(--fill); border: 1px solid transparent;
      border-radius: var(--r-sm); padding: 7px 12px; color: var(--t1);
      outline: none; transition: all .15s;
    }
    .row-input-text:focus, .row-select:focus {
      background: #FFFFFF; border-color: var(--blue);
      box-shadow: 0 0 0 3px rgba(0,113,227,.12);
    }
    .row-select {
      cursor: pointer; -webkit-appearance: none; appearance: none;
      padding-right: 28px;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236E6E73' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 10px center;
    }

    /* DUAL SCORE INPUT BOX */
    .score-dual-wrap {
      display: flex; align-items: center; gap: 8px; background: var(--fill);
      padding: 6px 10px; border-radius: var(--r-md);
    }
    .score-unit {
      display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: var(--t2);
    }
    .score-input {
      width: 76px; font-family: var(--font); font-size: 13.5px; font-weight: 600;
      background: #FFF; border: 1px solid var(--divider-hard); border-radius: var(--r-sm);
      padding: 6px 8px; text-align: center; color: var(--t1); outline: none;
      transition: all .15s ease;
    }
    .score-input:focus { border-color: var(--blue); box-shadow: 0 0 0 2px rgba(0,113,227,.15); }
    .score-input:disabled, .score-input.disabled-score {
      background: rgba(0,0,0,.06); border-color: rgba(0,0,0,.1); color: var(--t3);
      cursor: not-allowed; opacity: 0.55; box-shadow: none;
    }
    .score-clear-btn {
      font-size: 11px; font-weight: 600; color: var(--red); background: rgba(255,59,48,.1);
      border: 1px solid rgba(255,59,48,.2); border-radius: var(--r-sm); padding: 4px 8px;
      cursor: pointer; transition: all .15s ease; display: none;
    }
    .score-clear-btn:hover { background: rgba(255,59,48,.18); }
    .score-or-divider { font-size: 11px; font-weight: 700; color: var(--t3); text-transform: uppercase; }

    /* TOGGLE */
    .toggle {
      position: relative; display: inline-block; width: 44px; height: 26px;
      flex-shrink: 0; cursor: pointer;
    }
    .toggle input { opacity: 0; width: 0; height: 0; }
    .toggle-track {
      position: absolute; inset: 0; background: var(--fill-hover);
      border-radius: var(--r-pill); transition: background .2s;
    }
    .toggle-track::after {
      content: ""; position: absolute; left: 3px; top: 3px;
      width: 20px; height: 20px; background: #FFF;
      border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,.2);
      transition: transform .2s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .toggle input:checked + .toggle-track { background: var(--green); }
    .toggle input:checked + .toggle-track::after { transform: translateX(18px); }

    /* SEGMENTED CONTROL */
    .seg-row {
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 20px; border-bottom: 1px solid var(--divider);
      gap: 16px; flex-wrap: wrap;
    }
    .seg-control {
      display: inline-flex; background: var(--fill); padding: 3px;
      border-radius: var(--r-md); gap: 2px;
    }
    .seg-btn {
      font-family: var(--font); font-size: 12px; font-weight: 500;
      padding: 5px 12px; border: none; border-radius: var(--r-sm);
      background: transparent; color: var(--t2); cursor: pointer;
      transition: all .15s; white-space: nowrap;
    }
    .seg-btn:hover { color: var(--t1); }
    .seg-btn.active {
      background: #FFFFFF; color: var(--t1); font-weight: 600;
      box-shadow: 0 1px 3px rgba(0,0,0,.1);
    }

    /* TAGS */
    .tags-row { padding: 14px 20px; border-bottom: 1px solid var(--divider); }
    .tags-row-label { font-size: 14px; font-weight: 500; color: var(--t1); margin-bottom: 8px; }
    .tags-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
    .tag {
      font-size: 12px; font-weight: 500; padding: 4px 10px;
      border-radius: var(--r-pill); background: var(--fill); color: var(--t1);
      display: inline-flex; align-items: center; gap: 6px;
      border: 1px solid rgba(0,0,0,.04);
    }
    .tag-x {
      font-size: 14px; line-height: 1; color: var(--t3); cursor: pointer;
      border-radius: 50%; padding: 0 2px;
    }
    .tag-x:hover { color: var(--red); }
    .tag-add {
      font-size: 12px; font-weight: 500; padding: 4px 10px;
      border-radius: var(--r-pill); background: var(--blue-light); color: var(--blue);
      cursor: pointer; border: 1px dashed rgba(0,113,227,.3); transition: all .15s;
    }
    .tag-add:hover { background: rgba(0,113,227,.15); }

    /* CONDITIONAL EXPANDABLE BOX */
    .conditional-panel {
      background: rgba(0,0,0,.015);
      border-left: 3px solid var(--blue);
      padding: 14px 20px;
      display: none;
    }
    .conditional-panel.show { display: block; }
    .cond-title { font-size: 12.5px; font-weight: 600; color: var(--t1); margin-bottom: 8px; }

    /* CHECKBOX GRID FOR 10+2 SUBJECTS */
    .subject-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 10px; padding: 14px 20px;
    }
    .subject-item {
      display: flex; align-items: center; gap: 10px;
      background: var(--fill); padding: 10px 14px; border-radius: var(--r-md);
      cursor: pointer; transition: all .15s; user-select: none;
    }
    .subject-item:hover { background: var(--fill-hover); }
    .subject-item input[type="checkbox"] { width: 16px; height: 16px; accent-color: var(--blue); }
    .subject-item span { font-size: 13px; font-weight: 500; color: var(--t1); }

    /* BRANCH STRICTNESS MATRIX */
    .branch-matrix-row {
      display: flex; align-items: center; justify-content: space-between;
      padding: 10px 20px; border-bottom: 1px solid var(--divider);
      gap: 12px;
    }
    .branch-matrix-row:last-child { border-bottom: none; }
    .branch-title { font-size: 13.5px; font-weight: 500; color: var(--t1); }
    .matrix-toggles { display: flex; gap: 4px; background: var(--fill); padding: 3px; border-radius: var(--r-sm); }
    .matrix-opt {
      font-size: 11px; font-weight: 600; padding: 4px 9px; border-radius: 6px;
      border: none; background: transparent; color: var(--t2); cursor: pointer;
      transition: all .15s;
    }
    .matrix-opt.active-accept { background: var(--green); color: #FFF; }
    .matrix-opt.active-possibly { background: var(--orange); color: #FFF; }
    .matrix-opt.active-reject { background: var(--red); color: #FFF; }

    /* REPEATER FOR EXPERIENCE */
    .repeater-wrap { padding: 14px 20px; }
    .repeater-card {
      background: var(--fill); border-radius: var(--r-md);
      padding: 12px 16px; margin-bottom: 10px; position: relative;
      border: 1px solid rgba(0,0,0,.03);
    }
    .repeater-card-header {
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;
    }
    .repeater-tag {
      font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: var(--r-pill);
      background: var(--blue-light); color: var(--blue);
    }
    .repeater-card-body {
      font-size: 13px; color: var(--t1); display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 6px;
    }
    .repeater-card-sub { font-size: 12px; color: var(--t2); }
    .btn-repeater-del {
      background: transparent; border: none; color: var(--red);
      font-size: 12px; font-weight: 500; cursor: pointer; padding: 2px 6px;
    }
    .btn-repeater-del:hover { text-decoration: underline; }
    .btn-add-repeater {
      font-family: var(--font); font-size: 12.5px; font-weight: 600;
      color: var(--blue); background: var(--blue-light); border: 1px dashed rgba(0,113,227,.4);
      padding: 9px 16px; border-radius: var(--r-md); cursor: pointer;
      display: inline-flex; align-items: center; gap: 6px; transition: all .15s;
    }
    .btn-add-repeater:hover { background: rgba(0,113,227,.14); }

    /* DOCUMENT READINESS GRID */
    .doc-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 12px; padding: 16px 20px;
    }
    .doc-card {
      background: var(--fill); border-radius: var(--r-md); padding: 14px 16px;
      display: flex; flex-direction: column; justify-content: space-between;
      border: 1px solid rgba(0,0,0,.03);
    }
    .doc-name { font-size: 13px; font-weight: 600; color: var(--t1); margin-bottom: 4px; }
    .doc-note { font-size: 11.5px; color: var(--t2); margin-bottom: 10px; }
    .doc-select {
      font-size: 12px; font-weight: 600; padding: 6px 10px; border-radius: var(--r-sm);
      border: 1px solid var(--divider-hard); background: #FFF; outline: none; cursor: pointer;
    }
    .doc-select.status-AVAILABLE { color: #1E7E34; border-color: #34C759; background: var(--green-bg); }
    .doc-select.status-RENEWAL_REQUIRED { color: #B25E02; border-color: #FF9F0A; background: var(--orange-bg); }
    .doc-select.status-EXPIRED { color: #C82333; border-color: #FF3B30; background: var(--red-bg); }
    .doc-select.status-NOT_AVAILABLE { color: #6E6E73; border-color: var(--divider-hard); background: #E5E5EA; }
    .doc-select.status-NOT_APPLICABLE { color: #8E8E93; border-color: transparent; background: transparent; }

    /* LIVE SUMMARY CARD (SECTION 15) */
    .summary-card {
      background: #FFFFFF; border: 1px solid rgba(0,113,227,.2);
      box-shadow: 0 4px 24px rgba(0,113,227,.06);
      border-radius: var(--r-lg); padding: 22px; margin-top: 14px;
    }
    .summary-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px; margin-top: 14px;
    }
    .summary-col { background: var(--fill); padding: 14px; border-radius: var(--r-md); }
    .summary-col-title {
      font-size: 11px; font-weight: 700; text-transform: uppercase;
      letter-spacing: .05em; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
    }
    .summary-item { font-size: 12.5px; margin-bottom: 5px; color: var(--t1); line-height: 1.4; }
    .summary-item b { font-weight: 600; color: var(--t2); font-size: 11px; text-transform: uppercase; display: block; }

    /* STICKY ACTION BAR */
    .sticky-bar {
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 200;
      background: rgba(255,255,255,.94);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border-top: 1px solid var(--divider-hard);
      box-shadow: 0 -4px 16px rgba(0,0,0,.04);
      padding: 14px 24px;
    }
    .sticky-bar-inner {
      max-width: 880px; margin: 0 auto;
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
    }
    .status-note { font-size: 13px; color: var(--t2); display: flex; align-items: center; gap: 6px; }
    .status-dot-saved { width: 8px; height: 8px; border-radius: 50%; background: var(--green); }
    .btn-group { display: flex; gap: 10px; }
    .btn-save, .btn-reeval {
      font-family: var(--font); font-size: 13.5px; font-weight: 600;
      padding: 9px 18px; border-radius: var(--r-md); cursor: pointer;
      border: none; transition: all .15s;
    }
    .btn-save { background: var(--fill-hover); color: var(--t1); }
    .btn-save:hover { background: #E2E2E8; }
    .btn-reeval {
      background: var(--blue); color: #FFF;
      box-shadow: 0 2px 8px rgba(0,113,227,.25);
    }
    .btn-reeval:hover { background: var(--blue-hover); }
    .btn-save:disabled, .btn-reeval:disabled { opacity: .5; cursor: not-allowed; }

    /* TOAST */
    .toast {
      position: fixed; top: 68px; right: 24px; z-index: 300;
      background: #1D1D1F; color: #FFF; padding: 12px 20px;
      border-radius: var(--r-md); font-size: 13.5px; font-weight: 500;
      box-shadow: 0 4px 16px rgba(0,0,0,.2); opacity: 0; pointer-events: none;
      transform: translateY(-8px); transition: all .25s ease;
    }
    .toast.show { opacity: 1; pointer-events: auto; transform: translateY(0); }

    /* MODAL FOR ADDING EXPERIENCE */
    .modal-backdrop {
      position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 500;
      backdrop-filter: blur(4px); display: none; align-items: center; justify-content: center;
      padding: 16px;
    }
    .modal-backdrop.show { display: flex; }
    .modal-box {
      background: #FFF; max-width: 520px; width: 100%; border-radius: var(--r-lg);
      box-shadow: var(--shadow-modal); overflow: hidden; animation: popIn .2s ease-out;
    }
    @keyframes popIn { from { opacity: 0; transform: scale(.95); } to { opacity: 1; transform: scale(1); } }
    .modal-header {
      padding: 16px 20px; border-bottom: 1px solid var(--divider);
      display: flex; align-items: center; justify-content: space-between;
    }
    .modal-title { font-size: 16px; font-weight: 600; color: var(--t1); }
    .modal-close { background: none; border: none; font-size: 18px; color: var(--t3); cursor: pointer; }
    .modal-body { padding: 18px 20px; max-height: 70vh; overflow-y: auto; }
    .modal-field { margin-bottom: 14px; }
    .modal-field label { display: block; font-size: 12.5px; font-weight: 600; color: var(--t1); margin-bottom: 4px; }
    .modal-field input, .modal-field select { width: 100%; }
    .modal-footer {
      padding: 14px 20px; border-top: 1px solid var(--divider);
      display: flex; justify-content: flex-end; gap: 8px; background: var(--fill);
    }
  </style>
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <div class="nav-inner">
    <a href="/dashboard" class="nav-brand">
      Job Alerts
      <span class="badge-beta">Profile &amp; Preferences</span>
    </a>
    <div class="nav-tabs">
      <a href="/dashboard" class="nav-tab">Circulars Feed</a>
      <a href="/admin/requirements" class="nav-tab active">Candidate Profile</a>
    </div>
  </div>
  <!-- Quick Jump Subnav -->
  <div class="subnav">
    <a href="#sec-personal" class="subnav-link active-hard">A. Personal Facts</a>
    <a href="#sec-category" class="subnav-link active-hard">A. Category &amp; Reservation</a>
    <a href="#sec-10th" class="subnav-link active-hard">A. 10th Standard</a>
    <a href="#sec-12th" class="subnav-link active-hard">A. 12th Standard &amp; Subjects</a>
    <a href="#sec-btech" class="subnav-link active-hard">A. B.Tech Graduation</a>
    <a href="#sec-branch-matrix" class="subnav-link active-hard">A. Branch Equivalence</a>
    <a href="#sec-experience" class="subnav-link active-hard">A. Experience</a>
    <a href="#sec-licences" class="subnav-link active-hard">A. Licences</a>
    <a href="#sec-physical" class="subnav-link active-hard">A. Physical &amp; Medical</a>
    <a href="#sec-preferences" class="subnav-link active-pref">B. Job Preferences</a>
    <a href="#sec-constraints" class="subnav-link active-cons">C. Constraints</a>
    <a href="#sec-readiness" class="subnav-link active-ready">D. Document Readiness</a>
    <a href="#sec-summary" class="subnav-link">Live Summary &amp; Save</a>
  </div>
</nav>

<div class="page">
  <!-- HERO -->
  <div class="hero">
    <h1 class="hero-title">Personal Eligibility &amp; Preferences</h1>
    <p class="hero-sub">
      Captures every fact, preference, constraint, and application readiness condition required by government recruitment notifications.
    </p>
    <div class="hero-layers">
      <span class="layer-pill layer-pill-hard">Tier A · Hard Eligibility</span>
      <span class="layer-pill layer-pill-pref">Tier B · Personal Preferences</span>
      <span class="layer-pill layer-pill-cons">Tier C · Practical Constraints</span>
      <span class="layer-pill layer-pill-ready">Tier D · Application Readiness</span>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- TIER A: HARD ELIGIBILITY -->
  <!-- ================================================================= -->

  <!-- SECTION 1: PERSONAL & IDENTITY FACTS -->
  <section class="section" id="sec-personal">
    <div class="section-label">
      <span>Section 1 · Personal &amp; Identity Facts</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">Full Legal Name</div>
          <div class="row-subtext">Must match matriculation/degree records</div>
        </div>
        <input type="text" id="full-name" class="row-input-text" style="width: 220px;" placeholder="e.g. Bhargav V" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Date of Birth</div>
          <div class="row-subtext" id="dob-calc-label">Calculates exact age on notification cutoff dates</div>
        </div>
        <input type="date" id="dob" class="row-input-text" onchange="updateDobAgeDisplay()" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Gender</div>
          <div class="row-subtext">Used strictly for post-specific gender criteria (e.g. Women only, NDA)</div>
        </div>
        <select id="gender" class="row-select">
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Transgender">Transgender</option>
          <option value="Prefer not to say">Prefer not to say</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Nationality</div>
          <div class="row-subtext">Eligibility rule: Citizen of India / Subject of Nepal/Bhutan</div>
        </div>
        <select id="nationality" class="row-select">
          <option value="Indian" selected>Citizen of India</option>
          <option value="Nepal">Subject of Nepal</option>
          <option value="Bhutan">Subject of Bhutan</option>
          <option value="Tibetan Refugee">Tibetan Refugee (Pre-1962)</option>
          <option value="Other">Other</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">State of Domicile</div>
          <div class="row-subtext">State where candidate possesses official domicile / nativity quota</div>
        </div>
        <select id="domicile-state" class="row-select">
          <option value="">Select Domicile State...</option>
          <option value="Andhra Pradesh">Andhra Pradesh</option>
          <option value="Arunachal Pradesh">Arunachal Pradesh</option>
          <option value="Assam">Assam</option>
          <option value="Bihar">Bihar</option>
          <option value="Chhattisgarh">Chhattisgarh</option>
          <option value="Delhi">Delhi (NCT)</option>
          <option value="Goa">Goa</option>
          <option value="Gujarat">Gujarat</option>
          <option value="Haryana">Haryana</option>
          <option value="Himachal Pradesh">Himachal Pradesh</option>
          <option value="Jammu & Kashmir">Jammu &amp; Kashmir</option>
          <option value="Jharkhand">Jharkhand</option>
          <option value="Karnataka">Karnataka</option>
          <option value="Kerala">Kerala</option>
          <option value="Madhya Pradesh">Madhya Pradesh</option>
          <option value="Maharashtra">Maharashtra</option>
          <option value="Odisha">Odisha</option>
          <option value="Punjab">Punjab</option>
          <option value="Rajasthan">Rajasthan</option>
          <option value="Tamil Nadu">Tamil Nadu</option>
          <option value="Telangana">Telangana</option>
          <option value="Uttar Pradesh">Uttar Pradesh</option>
          <option value="Uttarakhand">Uttarakhand</option>
          <option value="West Bengal">West Bengal</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Permanent Residence State</div>
          <div class="row-subtext">Permanent address state (if distinct from domicile)</div>
        </div>
        <input type="text" id="permanent-state" class="row-input-text" style="width: 200px;" placeholder="e.g. Andhra Pradesh" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Current Residing City &amp; State</div>
          <div class="row-subtext">For local exam center and travel calculation</div>
        </div>
        <div class="row-value">
          <input type="text" id="current-city" class="row-input-text" style="width: 110px;" placeholder="City" />
          <input type="text" id="current-state" class="row-input-text" style="width: 110px;" placeholder="State" />
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Local District / Zone</div>
          <div class="row-subtext">For state PSC local-area non-local reservation quotas</div>
        </div>
        <input type="text" id="local-area" class="row-input-text" style="width: 200px;" placeholder="e.g. Visakhapatnam, Zone-I" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Willing to Relocate Anywhere in India</div>
          <div class="row-subtext">Accept posts with all-India service liability</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="all-india-toggle" checked />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="tags-row">
        <div class="tags-row-label">Preferred States / Posting Circles</div>
        <div class="row-subtext" style="margin-bottom: 6px;">Used when jobs offer circle or regional selections</div>
        <div class="tags-wrap" id="reloc-states-wrap"></div>
      </div>
    </div>
  </section>

  <!-- SECTION 2: CATEGORY & RESERVATION (SMART CONDITIONAL) -->
  <section class="section" id="sec-category">
    <div class="section-label">
      <span>Section 2 · Category &amp; Reservation Details</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">Constitutional Category</div>
          <div class="row-subtext">Determines reservation quota, cutoff relaxation &amp; fee waivers</div>
        </div>
        <select id="cat-select" class="row-select" onchange="handleCategoryChange()">
          <option value="General">General / Unreserved (UR)</option>
          <option value="EWS">Economically Weaker Sections (EWS)</option>
          <option value="OBC">Other Backward Classes (OBC-NCL)</option>
          <option value="SC">Scheduled Caste (SC)</option>
          <option value="ST">Scheduled Tribe (ST)</option>
        </select>
      </div>

      <!-- EWS Conditional Panel -->
      <div class="conditional-panel" id="panel-ews">
        <div class="cond-title">EWS Reservation Requirements</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 8px;">
          <div>
            <label style="font-size: 12px; color: var(--t2);">Income &amp; Asset Cert Available?</label>
            <select id="ews-cert-avail" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="yes">Yes · Possessed</option>
              <option value="renewal_required">Renewal Required for Current FY</option>
              <option value="no">No · Not Available</option>
            </select>
          </div>
          <div>
            <label style="font-size: 12px; color: var(--t2);">Valid for Central Government?</label>
            <select id="ews-central-valid" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="yes">Yes · Central Format</option>
              <option value="state_only">State Govt Format Only</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
        </div>
      </div>

      <!-- OBC Conditional Panel -->
      <div class="conditional-panel" id="panel-obc">
        <div class="cond-title">OBC-NCL Reservation Requirements</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 8px;">
          <div>
            <label style="font-size: 12px; color: var(--t2);">Central OBC-NCL Certificate?</label>
            <select id="obc-central-cert" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="yes">Yes · In Central Govt Format</option>
              <option value="state_only">State List Only</option>
              <option value="creamy_layer">Creamy Layer (Not eligible for NCL)</option>
            </select>
          </div>
          <div>
            <label style="font-size: 12px; color: var(--t2);">Certificate Validity</label>
            <select id="obc-cert-valid" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="valid">Issued within last 3 years</option>
              <option value="expired">Older than 3 years (Needs renewal)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- SC / ST Panel -->
      <div class="conditional-panel" id="panel-scst">
        <div class="cond-title">Caste Certificate Verification</div>
        <div>
          <label style="font-size: 12px; color: var(--t2);">Permanent Caste Certificate Available?</label>
          <select id="scst-cert-avail" class="row-select" style="width: 100%; margin-top: 4px;">
            <option value="yes">Yes · Digital / Competent Authority Issued</option>
            <option value="applied">Applied / Awaiting Issuance</option>
            <option value="no">Not Possessed</option>
          </select>
        </div>
      </div>

      <!-- PwBD Toggle & Panel -->
      <div class="row">
        <div>
          <div class="row-label">Persons with Benchmark Disabilities (PwBD)</div>
          <div class="row-subtext">Benchmark physical or sensory disability (≥40%)</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="pwbd-toggle" onchange="togglePwbdPanel()" />
          <span class="toggle-track"></span>
        </label>
      </div>
      <div class="conditional-panel" id="panel-pwbd">
        <div class="cond-title">Disability Category &amp; UDID Details</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 8px;">
          <div>
            <label style="font-size: 12px; color: var(--t2);">Disability Sub-Category</label>
            <select id="pwbd-category" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="OH">Orthopedically Handicapped (OH / Locomotor)</option>
              <option value="HH">Hearing Handicapped (HH)</option>
              <option value="VH">Visually Handicapped (VH / Blind / Low Vision)</option>
              <option value="Multiple">Multiple Disabilities / Autism / SLD</option>
            </select>
          </div>
          <div>
            <label style="font-size: 12px; color: var(--t2);">Percentage of Disability</label>
            <input type="number" id="pwbd-percentage" class="row-input-text" style="width: 100%; margin-top: 4px;" placeholder="e.g. 40" min="40" max="100" />
          </div>
          <div>
            <label style="font-size: 12px; color: var(--t2);">UDID Card Status</label>
            <select id="pwbd-udid" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="available">UDID Card Available</option>
              <option value="enrolled">Enrolled / Medical Board Cert</option>
              <option value="no">Not Available</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Ex-Serviceman Toggle & Panel -->
      <div class="row">
        <div>
          <div class="row-label">Ex-Serviceman (ESM) Status</div>
          <div class="row-subtext">Armed forces service quota &amp; age relaxations</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="esm-toggle" onchange="toggleEsmPanel()" />
          <span class="toggle-track"></span>
        </label>
      </div>
      <div class="conditional-panel" id="panel-esm">
        <div class="cond-title">Defense Service Information</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 8px;">
          <div>
            <label style="font-size: 12px; color: var(--t2);">Defense Branch</label>
            <select id="esm-branch" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="Army">Indian Army</option>
              <option value="Navy">Indian Navy</option>
              <option value="AirForce">Indian Air Force</option>
              <option value="CoastGuard">Indian Coast Guard</option>
            </select>
          </div>
          <div>
            <label style="font-size: 12px; color: var(--t2);">Length of Service (Years)</label>
            <input type="number" id="esm-years" class="row-input-text" style="width: 100%; margin-top: 4px;" placeholder="e.g. 15" min="1" max="40" />
          </div>
          <div>
            <label style="font-size: 12px; color: var(--t2);">Discharge Status</label>
            <select id="esm-status" class="row-select" style="width: 100%; margin-top: 4px;">
              <option value="discharged">Discharged with Pension</option>
              <option value="retiring_soon">Retiring within 1 Year (NOC)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Notification-Driven Relaxation -->
      <div class="row">
        <div>
          <div class="row-label">Category Age &amp; Fee Relaxation</div>
          <div class="row-subtext">Evaluates against each notification's official relaxation rules (no hardcoded assumptions)</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="age-relax-toggle" checked />
          <span class="toggle-track"></span>
        </label>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- DEDICATED QUALIFICATION FORMS (10TH, 12TH, B.TECH) -->
  <!-- ================================================================= -->

  <!-- SECTION 3: 10TH STANDARD (MATRICULATION) -->
  <section class="section" id="sec-10th">
    <div class="section-label">
      <span>Section 3 · 10th Standard (Matriculation)</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">Board / Institution</div>
          <div class="row-subtext">e.g. CBSE, ICSE, State Board of Secondary Education</div>
        </div>
        <input type="text" id="tenth-board" class="row-input-text" style="width: 240px;" placeholder="e.g. State Board / CBSE" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Passing Year</div>
          <div class="row-subtext">Year matriculation certificate was awarded</div>
        </div>
        <input type="number" id="tenth-year" class="row-input-text" style="width: 100px;" placeholder="2016" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Score (Percentage OR CGPA)</div>
          <div class="row-subtext">Enter either Percentage OR CGPA (whichever is on your marksheet)</div>
        </div>
        <div class="score-dual-wrap">
          <div class="score-unit">
            <span>%</span>
            <input type="number" step="0.1" id="tenth-pct" class="score-input" placeholder="85.0" oninput="handleScoreInput('tenth', 'pct')" />
          </div>
          <span class="score-or-divider">OR</span>
          <div class="score-unit">
            <span>CGPA</span>
            <input type="number" step="0.01" id="tenth-cgpa" class="score-input" placeholder="8.9" oninput="handleScoreInput('tenth', 'cgpa')" />
          </div>
          <button type="button" class="score-clear-btn" id="tenth-score-clear" onclick="clearScorePair('tenth')">Clear</button>
        </div>
      </div>
    </div>
  </section>

  <!-- SECTION 4: 12TH STANDARD & SUBJECTS -->
  <section class="section" id="sec-12th">
    <div class="section-label">
      <span>Section 4 · 12th Standard (Intermediate) &amp; Subjects</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">Board / Junior College</div>
          <div class="row-subtext">e.g. State Board of Intermediate Education, CBSE</div>
        </div>
        <input type="text" id="twelfth-board" class="row-input-text" style="width: 240px;" placeholder="e.g. Intermediate Board / CBSE" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Passing Year</div>
          <div class="row-subtext">Year of 10+2 completion</div>
        </div>
        <input type="number" id="twelfth-year" class="row-input-text" style="width: 100px;" placeholder="2018" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">12th Stream</div>
          <div class="row-subtext">Required by posts specifying 10+2 stream eligibility</div>
        </div>
        <select id="twelfth-stream" class="row-select">
          <option value="Science-PCM" selected>Science (PCM - Physics, Chemistry, Maths)</option>
          <option value="Science-PCB">Science (PCB - Physics, Chemistry, Biology)</option>
          <option value="Science-PCMB">Science (PCMB - Four Sciences)</option>
          <option value="Commerce">Commerce</option>
          <option value="Arts">Arts / Humanities</option>
          <option value="Vocational">Vocational</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Score (Percentage OR CGPA)</div>
          <div class="row-subtext">Enter either Percentage OR CGPA (enter any one)</div>
        </div>
        <div class="score-dual-wrap">
          <div class="score-unit">
            <span>%</span>
            <input type="number" step="0.1" id="twelfth-pct" class="score-input" placeholder="78.0" oninput="handleScoreInput('twelfth', 'pct')" />
          </div>
          <span class="score-or-divider">OR</span>
          <div class="score-unit">
            <span>CGPA</span>
            <input type="number" step="0.01" id="twelfth-cgpa" class="score-input" placeholder="8.2" oninput="handleScoreInput('twelfth', 'cgpa')" />
          </div>
          <button type="button" class="score-clear-btn" id="twelfth-score-clear" onclick="clearScorePair('twelfth')">Clear</button>
        </div>
      </div>

      <div style="padding: 14px 20px 4px;">
        <div class="row-label">Subject Specific Verification</div>
        <div class="row-subtext">Check all subjects studied. The engine verifies rules like: <i>"Must have studied Mathematics at 10+2 level"</i></div>
      </div>

      <div class="subject-grid">
        <label class="subject-item">
          <input type="checkbox" id="subj-maths" checked onchange="markDirty(); renderSummary();" />
          <span>Mathematics in 10+2</span>
        </label>
        <label class="subject-item">
          <input type="checkbox" id="subj-physics" checked onchange="markDirty(); renderSummary();" />
          <span>Physics in 10+2</span>
        </label>
        <label class="subject-item">
          <input type="checkbox" id="subj-chemistry" checked onchange="markDirty(); renderSummary();" />
          <span>Chemistry in 10+2</span>
        </label>
        <label class="subject-item">
          <input type="checkbox" id="subj-cs" checked onchange="markDirty(); renderSummary();" />
          <span>Computer Science in 10+2</span>
        </label>
        <label class="subject-item">
          <input type="checkbox" id="subj-biology" onchange="markDirty(); renderSummary();" />
          <span>Biology in 10+2</span>
        </label>
        <label class="subject-item">
          <input type="checkbox" id="subj-english" checked onchange="markDirty(); renderSummary();" />
          <span>English in 10th / 12th</span>
        </label>
      </div>

      <div class="tags-row">
        <div class="tags-row-label">Other Specialized 10+2 Subjects (e.g. Statistics, Economics)</div>
        <div class="tags-wrap" id="subj-other-tags"></div>
      </div>
    </div>
  </section>

  <!-- SECTION 5: GRADUATION (B.TECH DEGREE) -->
  <section class="section" id="sec-btech">
    <div class="section-label">
      <span>Section 5 · Graduation (B.Tech Degree)</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">Degree</div>
          <div class="row-subtext">Bachelor of Technology / Engineering</div>
        </div>
        <div style="font-weight: 600; color: var(--blue); background: var(--blue-light); padding: 5px 14px; border-radius: var(--r-pill); font-size: 13px;">
          B.Tech (Bachelor of Technology)
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Engineering Discipline / Branch</div>
          <div class="row-subtext">Primary graduation specialisation</div>
        </div>
        <input type="text" id="btech-branch" class="row-input-text" style="width: 250px;" value="Computer Science and Engineering" />
      </div>

      <div class="tags-row">
        <div class="tags-row-label">Accepted Equivalent Branches &amp; Synonyms</div>
        <div class="row-subtext" style="margin-bottom: 6px;">Circular requirements matching these terms will be recognized as your branch</div>
        <div class="tags-wrap" id="branch-tags"></div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">University / Institute</div>
          <div class="row-subtext">Name of university or degree awarding institution</div>
        </div>
        <input type="text" id="btech-univ" class="row-input-text" style="width: 250px;" placeholder="e.g. State Technical University / JNTU" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Graduation Year</div>
          <div class="row-subtext">Year of graduation or expected pass out</div>
        </div>
        <input type="number" id="btech-year" class="row-input-text" style="width: 100px;" placeholder="2022" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Score (Percentage OR CGPA)</div>
          <div class="row-subtext">Enter either Percentage OR CGPA (whichever is on your transcript)</div>
        </div>
        <div class="score-dual-wrap">
          <div class="score-unit">
            <span>%</span>
            <input type="number" step="0.1" id="btech-pct" class="score-input" placeholder="70.0" oninput="handleScoreInput('btech', 'pct')" />
          </div>
          <span class="score-or-divider">OR</span>
          <div class="score-unit">
            <span>CGPA</span>
            <input type="number" step="0.01" id="btech-cgpa" class="score-input" placeholder="7.4" oninput="handleScoreInput('btech', 'cgpa')" />
          </div>
          <button type="button" class="score-clear-btn" id="btech-score-clear" onclick="clearScorePair('btech')">Clear</button>
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Study Mode &amp; Completion Status</div>
          <div class="row-subtext">Recognized regular graduation</div>
        </div>
        <div class="row-value">
          <select id="btech-mode" class="row-select" style="margin-right: 6px;">
            <option value="full_time" selected>Full Time (Regular)</option>
            <option value="part_time">Part Time</option>
            <option value="distance">Distance / Lateral</option>
          </select>
          <select id="btech-status" class="row-select">
            <option value="completed" selected>Completed</option>
            <option value="pursuing">Pursuing</option>
            <option value="final_year">Final Year / Awaiting Results</option>
          </select>
        </div>
      </div>
    </div>
  </section>

  <!-- SECTION 6: BRANCH STRICTNESS MATRIX -->
  <section class="section" id="sec-branch-matrix">
    <div class="section-label">
      <span>Section 6 · Engineering Discipline Strictness Matrix</span>
      <span class="section-badge badge-hard">Configurable Rules</span>
    </div>
    <div class="card" id="branch-matrix-card">
      <div style="padding: 12px 20px; font-size: 12.5px; color: var(--t2); border-bottom: 1px solid var(--divider);">
        Define how the classifier matches branch requirements declared in notifications.<br>
        <b>ACCEPT</b> = Matches as eligible · <b>POSSIBLY</b> = Triggers manual review if equivalent · <b>EXCLUDE</b> = Rejects branch as ineligible.
      </div>
      <div id="branch-matrix-container">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </section>

  <!-- SECTION 7: ADDITIONAL QUALIFICATIONS -->
  <section class="section">
    <div class="section-label">
      <span>Section 7 · Additional Certifications &amp; Trade Diplomas</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="tags-row">
        <div class="tags-row-label">Computer &amp; Technical Certifications</div>
        <div class="row-subtext" style="margin-bottom: 6px;">e.g. NIELIT CCC, O-Level, Typing 35 WPM English, Stenography 80 WPM, NCC 'C' Certificate</div>
        <div class="tags-wrap" id="cert-tags"></div>
      </div>
    </div>
  </section>

  <!-- SECTION 8: EXPERIENCE & EMPLOYMENT -->
  <section class="section" id="sec-experience">
    <div class="section-label">
      <span>Section 8 · Experience &amp; Employment Records</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="seg-row">
        <div>
          <div class="row-label">Current Experience Tier</div>
          <div class="row-subtext">Determines whether experienced-only circulars match</div>
        </div>
        <div class="seg-control" id="exp-seg">
          <button class="seg-btn active" data-val="fresher" onclick="setExpBucket('fresher')">Fresher (0 yr)</button>
          <button class="seg-btn" data-val="0-2" onclick="setExpBucket('0-2')">Up to 2 yrs</button>
          <button class="seg-btn" data-val="2-5" onclick="setExpBucket('2-5')">2 – 5 yrs</button>
          <button class="seg-btn" data-val="5+" onclick="setExpBucket('5+')">5+ yrs</button>
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Fresher-Friendly Opportunities</div>
          <div class="row-subtext">Accept circulars declaring 0 experience required or freshers eligible</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="fresher-toggle" checked />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="card-divider"></div>

      <!-- Employment Repeater -->
      <div class="repeater-wrap">
        <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">Detailed Employment Records</div>
        <div style="font-size: 12px; color: var(--t2); margin-bottom: 12px;">
          Government circulars differentiate between Qualifying Experience vs Internships / Apprenticeships.
        </div>
        <div id="experience-records-container">
          <!-- Dynamically populated -->
        </div>
        <button type="button" class="btn-add-repeater" onclick="openAddExpModal()">
          + Add Employment Record
        </button>
      </div>
    </div>
  </section>

  <!-- SECTION 9: LICENCES & REGISTRATIONS -->
  <section class="section" id="sec-licences">
    <div class="section-label">
      <span>Section 9 · Licences &amp; Professional Registrations</span>
      <span class="section-badge badge-hard">Hard Eligibility</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">Light Motor Vehicle (LMV) Driving Licence</div>
          <div class="row-subtext">Mandatory for posts like Sub-Inspector, Field Investigator, Transport Inspector</div>
        </div>
        <select id="lic-lmv" class="row-select">
          <option value="none">Not Possessed</option>
          <option value="valid" selected>Valid LMV Licence</option>
          <option value="expired">Expired (Renewal Needed)</option>
          <option value="learning">Learner's Licence Only</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Heavy Motor Vehicle (HMV) Commercial Licence</div>
          <div class="row-subtext">For driver, heavy equipment, fire operator posts</div>
        </div>
        <select id="lic-hmv" class="row-select">
          <option value="none" selected>Not Possessed</option>
          <option value="valid">Valid HMV Commercial Licence</option>
          <option value="expired">Expired</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Professional Council Registration</div>
          <div class="row-subtext">Bar Council, Nursing Council, Medical Council, Pharmacy Council</div>
        </div>
        <select id="lic-council" class="row-select">
          <option value="none" selected>None / Not Applicable</option>
          <option value="Bar_Council">Bar Council of India</option>
          <option value="Nursing_Council">State Nursing Council</option>
          <option value="Medical_Council">State / National Medical Commission</option>
          <option value="Pharmacy_Council">Pharmacy Council of India</option>
          <option value="Other">Other Statutory Council</option>
        </select>
      </div>
    </div>
  </section>

  <!-- SECTION 10: PHYSICAL & MEDICAL STANDARDS -->
  <section class="section" id="sec-physical">
    <div class="section-label">
      <span>Section 10 · Physical &amp; Medical Standards</span>
      <span class="section-badge badge-hard">Hard Facts vs Constraints</span>
    </div>
    <div class="card">
      <div style="padding: 12px 20px; font-size: 12.5px; color: var(--t2); border-bottom: 1px solid var(--divider);">
        Physical measurements (Height/Chest) are legal requirements. Physical efficiency tests (PET running) are candidate constraints.
      </div>

      <div class="row">
        <div>
          <div class="row-label">Candidate Height</div>
          <div class="row-subtext">Checked against notifications with minimum height limits (e.g. 165 cm, 170 cm)</div>
        </div>
        <div class="row-value">
          <input type="number" id="phys-height" class="row-input-text" style="width: 80px;" placeholder="172" />
          <span style="font-size: 13px; color: var(--t2);">cm</span>
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Chest Measurement (Male candidates)</div>
          <div class="row-subtext">Unexpanded and minimum expanded chest</div>
        </div>
        <div class="row-value">
          <input type="number" id="phys-chest-norm" class="row-input-text" style="width: 70px;" placeholder="80" />
          <span style="font-size: 13px; color: var(--t2);">cm /</span>
          <input type="number" id="phys-chest-exp" class="row-input-text" style="width: 70px;" placeholder="85" />
          <span style="font-size: 13px; color: var(--t2);">cm</span>
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Color Blindness</div>
          <div class="row-subtext">Technical circulars (Railways Loco/Tech, Defence, Electrical) prohibit color blindness</div>
        </div>
        <select id="med-color-blind" class="row-select">
          <option value="no" selected>No · Normal Color Vision</option>
          <option value="yes">Yes · Defective Color Vision</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Visual Acuity / Eyesight Standard</div>
          <div class="row-subtext">e.g. 6/6, 6/9 with or without corrective glasses</div>
        </div>
        <input type="text" id="med-eyesight" class="row-input-text" style="width: 140px;" placeholder="e.g. 6/6 with glasses" />
      </div>

      <div class="row">
        <div>
          <div class="row-label">Willing for Physical Efficiency Tests (PET)</div>
          <div class="row-subtext">Running 1600m / sprint, high jump, long jump tests</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="physical-tests-toggle" />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Accept Uniformed / Police / CAPF Jobs</div>
          <div class="row-subtext">Police SI/Constable, Paramilitary, Forest Ranger, Excise Inspector</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="police-standards-toggle" />
          <span class="toggle-track"></span>
        </label>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- TIER B: PERSONAL PREFERENCES -->
  <!-- ================================================================= -->

  <!-- SECTION 11: SECTOR & ORGANIZATION PREFERENCES -->
  <section class="section" id="sec-preferences">
    <div class="section-label">
      <span>Section 11 · Organization &amp; Sector Preferences</span>
      <span class="section-badge badge-pref">Personal Preferences</span>
    </div>
    <div class="card">
      <div class="tags-row">
        <div>
          <div class="tags-row-label">Target Government Sectors</div>
          <div class="row-subtext">Sectors to match opportunities from</div>
        </div>
        <div class="tags-wrap" id="sector-tags"></div>
      </div>

      <div class="tags-row">
        <div>
          <div class="tags-row-label">Priority Target Organizations (⭐ Want to Apply)</div>
          <div class="row-subtext">Jobs from these organizations automatically earn 'WANT TO APPLY' priority</div>
        </div>
        <div class="tags-wrap" id="pref-org-tags"></div>
      </div>

      <div class="tags-row">
        <div>
          <div class="tags-row-label">Strictly Avoided Organizations (✕ Not Interested)</div>
          <div class="row-subtext">Jobs from these organizations are flagged as 'NOT INTERESTED'</div>
        </div>
        <div class="tags-wrap" id="avoid-org-tags"></div>
      </div>
    </div>
  </section>

  <!-- SECTION 12: ROLE PREFERENCES & WORK NATURE -->
  <section class="section">
    <div class="section-label">
      <span>Section 12 · Role Preferences, Work Nature &amp; Job Security</span>
      <span class="section-badge badge-pref">Personal Preferences</span>
    </div>
    <div class="card">
      <div class="tags-row">
        <div>
          <div class="tags-row-label">Preferred Job Roles</div>
          <div class="row-subtext">Technical, Software / IT, Engineering, Data / Analytics, Administration, Research</div>
        </div>
        <div class="tags-wrap" id="pref-role-tags"></div>
      </div>

      <div class="tags-row">
        <div>
          <div class="tags-row-label">Strictly Avoided Roles</div>
          <div class="row-subtext">Roles to mark as 'NOT INTERESTED' (e.g. Police / Uniformed, Defence Combat, Sales, Manual Labor)</div>
        </div>
        <div class="tags-wrap" id="avoid-role-tags"></div>
      </div>

      <div class="seg-row">
        <div>
          <div class="row-label">Work Nature</div>
          <div class="row-subtext">Desk duty vs field postings</div>
        </div>
        <div class="seg-control" id="work-nature-seg">
          <button class="seg-btn active" data-val="desk_only" onclick="setWorkNature('desk_only')">Desk Only</button>
          <button class="seg-btn" data-val="mixed" onclick="setWorkNature('mixed')">Mixed</button>
          <button class="seg-btn" data-val="field_acceptable" onclick="setWorkNature('field_acceptable')">Field Acceptable</button>
        </div>
      </div>

      <div class="seg-row">
        <div>
          <div class="row-label">Shift Preference</div>
          <div class="row-subtext">Day duties vs 24x7 rotational or night shifts</div>
        </div>
        <div class="seg-control" id="shift-seg">
          <button class="seg-btn active" data-val="day_shifts_only" onclick="setShiftPref('day_shifts_only')">Day Shifts Only</button>
          <button class="seg-btn" data-val="rotational_acceptable" onclick="setShiftPref('rotational_acceptable')">Rotational Ok</button>
          <button class="seg-btn" data-val="any" onclick="setShiftPref('any')">Any Shift</button>
        </div>
      </div>

      <div class="seg-row">
        <div>
          <div class="row-label">Job Security &amp; Tenure</div>
          <div class="row-subtext">Permanent post vs contractual / apprenticeship</div>
        </div>
        <div class="seg-control" id="security-seg">
          <button class="seg-btn active" data-val="permanent_only" onclick="setSecurityPref('permanent_only')">Permanent Only</button>
          <button class="seg-btn" data-val="permanent_preferred" onclick="setSecurityPref('permanent_preferred')">Permanent Preferred</button>
          <button class="seg-btn" data-val="any" onclick="setSecurityPref('any')">Any Tenure</button>
        </div>
      </div>

      <!-- Salary Preferences -->
      <div class="row">
        <div>
          <div class="row-label">Minimum Acceptable Gross Salary (Monthly)</div>
          <div class="row-subtext">Jobs below this threshold are deprioritized or excluded</div>
        </div>
        <div class="row-value">
          <span style="font-size: 13px; color: var(--t2);">₹</span>
          <input type="number" id="min-salary-inr" class="row-input-text" style="width: 100px;" placeholder="40000" />
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Enforce Salary as Hard Exclusion Filter</div>
          <div class="row-subtext">If unchecked, acts as a preference tag; if checked, excludes lower-paying jobs</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="salary-hard-filter-toggle" />
          <span class="toggle-track"></span>
        </label>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- TIER C: PRACTICAL CONSTRAINTS -->
  <!-- ================================================================= -->

  <!-- SECTION 13: APPLICATION FEES, BONDS & CONSTRAINTS -->
  <section class="section" id="sec-constraints">
    <div class="section-label">
      <span>Section 13 · Practical Application Constraints</span>
      <span class="section-badge badge-cons">Application Constraints</span>
    </div>
    <div class="card">
      <div class="seg-row">
        <div>
          <div class="row-label">Maximum Application Fee Willing to Pay</div>
          <div class="row-subtext">The engine calculates your category exemption fee (e.g. SC/ST/Women free)</div>
        </div>
        <div class="seg-control" id="fee-seg">
          <button class="seg-btn" data-val="0" onclick="setFeeVal('0')">Free only</button>
          <button class="seg-btn" data-val="250" onclick="setFeeVal('250')">≤ ₹250</button>
          <button class="seg-btn active" data-val="500" onclick="setFeeVal('500')">≤ ₹500</button>
          <button class="seg-btn" data-val="1000" onclick="setFeeVal('1000')">≤ ₹1,000</button>
          <button class="seg-btn" data-val="" onclick="setFeeVal('')">Any Fee</button>
        </div>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Exclude High-Fee Jobs</div>
          <div class="row-subtext">Mark jobs exceeding fee limit as 'NOT INTERESTED' (instead of warning only)</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="exclude-high-fee-toggle" />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Mandatory Service Bonds Acceptable</div>
          <div class="row-subtext">Willing to sign 2-3 year service agreements / surety bonds</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="service-bond-toggle" checked />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Willing to Travel for Examinations</div>
          <div class="row-subtext">Travel to other districts or neighboring states for Tier-1/Tier-2 exams</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="exam-travel-toggle" checked />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="tags-row">
        <div>
          <div class="tags-row-label">Hard Excluded Job Keywords (Never Alert Me)</div>
          <div class="row-subtext">Opportunities matching these keywords are strictly rejected</div>
        </div>
        <div class="tags-wrap" id="hard-exclusions-tags"></div>
      </div>

      <div class="tags-row">
        <div>
          <div class="tags-row-label">Specific Target Exams / Opportunities</div>
          <div class="row-subtext">e.g. SSC CGL, UPSC CSE, ISRO Scientist, State PSC Assistant Engineer</div>
        </div>
        <div class="tags-wrap" id="target-jobs-tags"></div>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- TIER D: APPLICATION READINESS -->
  <!-- ================================================================= -->

  <!-- SECTION 14: DOCUMENT READINESS CHECKLIST -->
  <section class="section" id="sec-readiness">
    <div class="section-label">
      <span>Section 14 · Document &amp; Application Readiness</span>
      <span class="section-badge badge-ready">Application Readiness</span>
    </div>
    <div class="card">
      <div style="padding: 12px 20px; font-size: 12.5px; color: var(--t2); border-bottom: 1px solid var(--divider);">
        Track readiness of official certificates. If a mandatory certificate is expired or missing, the classifier flags <b>Tier D Readiness Warnings</b> without invalidating legal eligibility.
      </div>

      <div class="doc-grid" id="doc-readiness-grid">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </section>

  <!-- SECTION 15: CLASSIFICATION BEHAVIOR -->
  <section class="section">
    <div class="section-label">
      <span>Section 15 · Classification Strictness &amp; Ambiguity Rules</span>
      <span class="section-badge badge-hard">Engine Behavior</span>
    </div>
    <div class="card">
      <div class="row">
        <div>
          <div class="row-label">When Circular Information is Missing / Ambiguous</div>
          <div class="row-subtext">How to classify posts with uncertain equivalence or missing cutoff dates</div>
        </div>
        <select id="unknown-handling-select" class="row-select">
          <option value="REVIEW" selected>Send to REVIEW (Conservative &amp; Safest)</option>
          <option value="POTENTIALLY_ELIGIBLE">Potentially Eligible (Optimistic)</option>
          <option value="NOT_ELIGIBLE">Treat as Not Eligible (Strict)</option>
        </select>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Conceal 'Not Interested' Circulars</div>
          <div class="row-subtext">Hide deprioritized opportunities from the main dashboard feed</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="hide-not-interested-toggle" />
          <span class="toggle-track"></span>
        </label>
      </div>

      <div class="row">
        <div>
          <div class="row-label">Alert on Review / Ambiguous Cases</div>
          <div class="row-subtext">Send Telegram notification for circulars requiring manual verification</div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="alert-uncertain-toggle" checked />
          <span class="toggle-track"></span>
        </label>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- SECTION 16: LIVE PROFILE SUMMARY -->
  <!-- ================================================================= -->
  <section class="section" id="sec-summary">
    <div class="section-label">
      <span>Section 16 · Candidate Profile Summary</span>
      <span class="section-badge badge-pref">4-Tier Live Review</span>
    </div>
    <div class="summary-card">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <h3 style="font-size: 16px; font-weight: 700; color: var(--t1);">Consolidated 4-Tier Verification Matrix</h3>
        <span style="font-size: 11.5px; color: var(--blue); font-weight: 600;">Reactive Live Update</span>
      </div>
      <div class="summary-grid" id="summary-grid-content">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </section>

</div>

<!-- STICKY ACTION BAR -->
<div class="sticky-bar">
  <div class="sticky-bar-inner">
    <div class="status-note">
      <span class="status-dot-saved" id="status-dot"></span>
      <span id="save-status-text">All profile layers synchronized</span>
    </div>
    <div class="btn-group">
      <button class="btn-save" id="btnSaveOnly" onclick="saveProfile(false)">Save Profile</button>
      <button class="btn-reeval" id="btnSaveReeval" onclick="saveProfile(true)">⚡ Save &amp; Re-Evaluate All Jobs</button>
    </div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<!-- MODAL: ADD EXPERIENCE RECORD -->
<div class="modal-backdrop" id="modal-add-exp">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title">Add Employment Record</div>
      <button class="modal-close" onclick="closeAddExpModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="modal-field">
        <label>Organization / Employer Name</label>
        <input type="text" id="m-exp-employer" class="row-input-text" placeholder="e.g. Infosys, DRDO, State PWD" />
      </div>
      <div class="modal-field">
        <label>Sector</label>
        <select id="m-exp-sector" class="row-select">
          <option value="private" selected>Private Sector</option>
          <option value="government">Central / State Government</option>
          <option value="psu">Public Sector Undertaking (PSU)</option>
          <option value="banking">Public Sector Bank</option>
          <option value="autonomous">Autonomous Scientific Body</option>
        </select>
      </div>
      <div class="modal-field">
        <label>Designation / Job Title</label>
        <input type="text" id="m-exp-role" class="row-input-text" placeholder="e.g. Software Engineer, Junior Assistant" />
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div class="modal-field">
          <label>Total Duration (Months)</label>
          <input type="number" id="m-exp-months" class="row-input-text" placeholder="24" min="1" />
        </div>
        <div class="modal-field">
          <label>Contract Type</label>
          <select id="m-exp-contract" class="row-select">
            <option value="permanent" selected>Regular / Permanent</option>
            <option value="contract">Contractual</option>
            <option value="apprentice">Apprenticeship</option>
            <option value="internship">Internship</option>
          </select>
        </div>
      </div>
      <div class="modal-field" style="display: flex; align-items: center; gap: 8px; margin-top: 6px;">
        <input type="checkbox" id="m-exp-cert" checked style="width: 16px; height: 16px; accent-color: var(--blue);" />
        <label for="m-exp-cert" style="margin-bottom: 0; font-size: 13px;">Experience Certificate / Relieving Letter Available</label>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-save" onclick="closeAddExpModal()">Cancel</button>
      <button class="btn-reeval" onclick="submitAddExp()">Add Employment</button>
    </div>
  </div>
</div>

<script>
// =========================================================================
// STATE ARCHITECTURE
// =========================================================================
const S = {
  // Experience Records
  experienceRecords: [],
  
  // Tags Lists (Degrees tag-cloud removed because user strictly holds B.Tech)
  branches: ["Computer Science", "Information Technology", "CSE", "IT"],
  sectors: ["Central Govt", "State Govt", "PSU", "Banking", "Defense"],
  relocStates: ["Andhra Pradesh", "Telangana", "Karnataka"],
  prefOrgs: ["ISRO", "DRDO", "BARC", "UPSC", "SSC", "NIC", "RBI"],
  avoidOrgs: [],
  prefRoles: ["Software / IT", "Technical", "Engineering", "Data / Analytics"],
  avoidRoles: ["Police / Uniformed", "Defence Combat", "Sales / Field Agent"],
  certifications: ["NIELIT CCC", "Typing English 40 WPM"],
  subjOther: [],
  hardExclusions: ["Police", "Combat", "Manual Labor"],
  targetJobs: ["SSC CGL", "ISRO Scientist", "NIC Technical Assistant", "UPSC CSE"],

  // Branch Strictness Matrix
  branchMappings: {
    "Computer Science": "ACCEPT",
    "Information Technology": "ACCEPT",
    "CSE": "ACCEPT",
    "IT": "ACCEPT",
    "Computer Engineering": "ACCEPT",
    "AI & ML": "ACCEPT",
    "Data Science": "ACCEPT",
    "Electronics": "ACCEPT",
    "ECE": "ACCEPT",
    "Electrical": "POSSIBLY_ACCEPT",
    "Mechanical": "DO_NOT_ACCEPT",
    "Civil": "DO_NOT_ACCEPT"
  },

  // Document Readiness Dict (Tier D)
  documentsReadiness: {
    "tenth_cert": { document_key: "tenth_cert", name: "10th Board Certificate (Proof of DOB)", status: "AVAILABLE", valid_up_to_date: null, notes: "Permanent proof of age" },
    "twelfth_cert": { document_key: "twelfth_cert", name: "12th Board Certificate & Marksheet", status: "AVAILABLE", valid_up_to_date: null, notes: "Shows PCM subjects" },
    "degree_cert": { document_key: "degree_cert", name: "Degree Certificate / Provisional", status: "AVAILABLE", valid_up_to_date: null, notes: "Convocation degree available" },
    "caste_ews_cert": { document_key: "caste_ews_cert", name: "Category / EWS / OBC-NCL Certificate", status: "AVAILABLE", valid_up_to_date: "2026-03-31", notes: "Current financial year validity" },
    "domicile_cert": { document_key: "domicile_cert", name: "Domicile / Nativity Certificate", status: "AVAILABLE", valid_up_to_date: null, notes: "State quota proof" },
    "driving_licence": { document_key: "driving_licence", name: "Driving Licence (LMV)", status: "AVAILABLE", valid_up_to_date: "2035-12-31", notes: "Light Motor Vehicle" },
    "experience_cert": { document_key: "experience_cert", name: "Experience Certificate / Service Letter", status: "NOT_APPLICABLE", valid_up_to_date: null, notes: "Fresher or no current req" },
    "noc": { document_key: "noc", name: "No Objection Certificate (NOC for Govt)", status: "NOT_APPLICABLE", valid_up_to_date: null, notes: "Required if currently employed in Govt/PSU" }
  },

  // Controls
  expVal: "fresher",
  feeVal: "500",
  workNature: "desk_only",
  shiftPref: "day_shifts_only",
  securityPref: "permanent_only"
};

const DEFAULT_BRANCH_MATRIX_KEYS = [
  "Computer Science", "Information Technology", "Computer Engineering",
  "AI & ML", "Data Science", "Electronics", "Electrical", "Mechanical", "Civil"
];

// SCORE DUAL-INPUT MUTUAL DISABLING & AUTO-SAVE PIPELINE
function handleScoreInput(prefix, type) {
  const pctEl = document.getElementById(`${prefix}-pct`);
  const cgpaEl = document.getElementById(`${prefix}-cgpa`);
  const clearBtn = document.getElementById(`${prefix}-score-clear`);
  if (!pctEl || !cgpaEl) return;

  if (type === 'pct') {
    const val = (pctEl.value || '').trim();
    if (val !== '') {
      cgpaEl.value = '';
      cgpaEl.disabled = true;
      cgpaEl.classList.add('disabled-score');
      if (clearBtn) clearBtn.style.display = 'inline-flex';
    } else {
      cgpaEl.disabled = false;
      cgpaEl.classList.remove('disabled-score');
      if (clearBtn) clearBtn.style.display = 'none';
    }
  } else if (type === 'cgpa') {
    const val = (cgpaEl.value || '').trim();
    if (val !== '') {
      pctEl.value = '';
      pctEl.disabled = true;
      pctEl.classList.add('disabled-score');
      if (clearBtn) clearBtn.style.display = 'inline-flex';
    } else {
      pctEl.disabled = false;
      pctEl.classList.remove('disabled-score');
      if (clearBtn) clearBtn.style.display = 'none';
    }
  }
  markDirty();
  renderSummary();
  scheduleAutoSave();
}

function clearScorePair(prefix) {
  const pctEl = document.getElementById(`${prefix}-pct`);
  const cgpaEl = document.getElementById(`${prefix}-cgpa`);
  const clearBtn = document.getElementById(`${prefix}-score-clear`);
  if (pctEl) {
    pctEl.value = '';
    pctEl.disabled = false;
    pctEl.classList.remove('disabled-score');
  }
  if (cgpaEl) {
    cgpaEl.value = '';
    cgpaEl.disabled = false;
    cgpaEl.classList.remove('disabled-score');
  }
  if (clearBtn) clearBtn.style.display = 'none';
  markDirty();
  renderSummary();
  scheduleAutoSave();
}

function syncScorePairState(prefix) {
  const pctEl = document.getElementById(`${prefix}-pct`);
  const cgpaEl = document.getElementById(`${prefix}-cgpa`);
  const clearBtn = document.getElementById(`${prefix}-score-clear`);
  if (!pctEl || !cgpaEl) return;

  const hasPct = (pctEl.value || '').trim() !== '';
  const hasCgpa = (cgpaEl.value || '').trim() !== '';

  if (hasPct && !hasCgpa) {
    cgpaEl.disabled = true;
    cgpaEl.classList.add('disabled-score');
    if (clearBtn) clearBtn.style.display = 'inline-flex';
  } else if (hasCgpa && !hasPct) {
    pctEl.disabled = true;
    pctEl.classList.add('disabled-score');
    if (clearBtn) clearBtn.style.display = 'inline-flex';
  } else if (hasPct && hasCgpa) {
    cgpaEl.value = '';
    cgpaEl.disabled = true;
    cgpaEl.classList.add('disabled-score');
    if (clearBtn) clearBtn.style.display = 'inline-flex';
  } else {
    pctEl.disabled = false;
    pctEl.classList.remove('disabled-score');
    cgpaEl.disabled = false;
    cgpaEl.classList.remove('disabled-score');
    if (clearBtn) clearBtn.style.display = 'none';
  }
}

let autoSaveTimer = null;
function scheduleAutoSave() {
  markDirty();
  if (autoSaveTimer) clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(() => {
    saveProfile(false, true);
  }, 1200);
}

// =========================================================================
// LOAD PROFILE
// =========================================================================
async function loadProfile() {
  try {
    const res = await fetch('/api/requirements');
    if (!res.ok) return;
    const d = await res.json();

    // 1. Personal
    if (d.personal) {
      if (d.personal.full_name) document.getElementById('full-name').value = d.personal.full_name;
      if (d.personal.gender) document.getElementById('gender').value = d.personal.gender;
      if (d.personal.nationality) document.getElementById('nationality').value = d.personal.nationality;
      if (d.personal.state_of_domicile) document.getElementById('domicile-state').value = d.personal.state_of_domicile;
      if (d.personal.permanent_state) document.getElementById('permanent-state').value = d.personal.permanent_state;
      if (d.personal.current_city) document.getElementById('current-city').value = d.personal.current_city;
      if (d.personal.current_state) document.getElementById('current-state').value = d.personal.current_state;
      if (d.personal.local_area_district) document.getElementById('local-area').value = d.personal.local_area_district;
      document.getElementById('all-india-toggle').checked = (d.personal.willing_to_relocate_all_india !== false);
      if (d.personal.preferred_relocation_states) S.relocStates = [...d.personal.preferred_relocation_states];
    }
    if (d.date_of_birth) {
      document.getElementById('dob').value = d.date_of_birth;
      updateDobAgeDisplay();
    }

    // 2. Category & Relaxation
    if (d.age) {
      if (d.age.category) document.getElementById('cat-select').value = d.age.category;
      document.getElementById('age-relax-toggle').checked = (d.age.category_age_relaxations && Object.keys(d.age.category_age_relaxations).length > 0);
    }
    handleCategoryChange();

    // 3. 10th Standard Form
    const tenthRecord = (d.education_records || []).find(r => r.level === '10th');
    if (tenthRecord || d.education_history) {
      document.getElementById('tenth-board').value = tenthRecord?.institution_board || d.education_history?.tenth_board || '';
      document.getElementById('tenth-year').value = tenthRecord?.passing_year || d.education_history?.tenth_year || '';
      const tPct = tenthRecord?.percentage ?? d.education_history?.tenth_percentage;
      const tCgpa = tenthRecord?.cgpa ?? d.education_history?.tenth_cgpa;
      if (tPct != null && tCgpa != null) {
        document.getElementById('tenth-pct').value = tPct;
        document.getElementById('tenth-cgpa').value = '';
      } else if (tPct != null) {
        document.getElementById('tenth-pct').value = tPct;
      } else if (tCgpa != null) {
        document.getElementById('tenth-cgpa').value = tCgpa;
      }
      syncScorePairState('tenth');
    }

    // 4. 12th Standard & Subjects Form
    const twelfthRecord = (d.education_records || []).find(r => r.level === '12th');
    if (twelfthRecord || d.education_history || d.subjects_10_12) {
      document.getElementById('twelfth-board').value = twelfthRecord?.institution_board || d.education_history?.twelfth_board || '';
      document.getElementById('twelfth-year').value = twelfthRecord?.passing_year || d.education_history?.twelfth_year || '';
      document.getElementById('twelfth-stream').value = d.subjects_10_12?.twelfth_stream || d.education_history?.twelfth_stream || 'Science-PCM';
      const twPct = twelfthRecord?.percentage ?? d.education_history?.twelfth_percentage;
      const twCgpa = twelfthRecord?.cgpa ?? d.education_history?.twelfth_cgpa;
      if (twPct != null && twCgpa != null) {
        document.getElementById('twelfth-pct').value = twPct;
        document.getElementById('twelfth-cgpa').value = '';
      } else if (twPct != null) {
        document.getElementById('twelfth-pct').value = twPct;
      } else if (twCgpa != null) {
        document.getElementById('twelfth-cgpa').value = twCgpa;
      }
      syncScorePairState('twelfth');

      if (d.subjects_10_12) {
        document.getElementById('subj-maths').checked = !!d.subjects_10_12.studied_maths_12th;
        document.getElementById('subj-physics').checked = !!d.subjects_10_12.studied_physics_12th;
        document.getElementById('subj-chemistry').checked = !!d.subjects_10_12.studied_chemistry_12th;
        document.getElementById('subj-biology').checked = !!d.subjects_10_12.studied_biology_12th;
        document.getElementById('subj-cs').checked = !!d.subjects_10_12.studied_computer_science_12th;
        document.getElementById('subj-english').checked = (d.subjects_10_12.studied_english !== false);
        if (d.subjects_10_12.other_subjects) S.subjOther = [...d.subjects_10_12.other_subjects];
      }
    }

    // 5. Graduation (B.Tech) Form
    const btechRecord = (d.education_records || []).find(r => r.level === 'bachelors');
    document.getElementById('btech-branch').value = btechRecord?.branch || d.education_history?.graduation_branch || (d.education?.branches && d.education.branches[0]) || 'Computer Science and Engineering';
    document.getElementById('btech-univ').value = btechRecord?.institution_board || d.education_history?.graduation_university || '';
    document.getElementById('btech-year').value = btechRecord?.passing_year || d.education_history?.graduation_year || '';
    const bPct = btechRecord?.percentage ?? d.education_history?.graduation_percentage ?? d.education?.minimum_percentage;
    const bCgpa = btechRecord?.cgpa ?? d.education_history?.graduation_cgpa;
    if (bPct != null && bCgpa != null) {
      document.getElementById('btech-pct').value = bPct;
      document.getElementById('btech-cgpa').value = '';
    } else if (bPct != null) {
      document.getElementById('btech-pct').value = bPct;
    } else if (bCgpa != null) {
      document.getElementById('btech-cgpa').value = bCgpa;
    }
    syncScorePairState('btech');

    document.getElementById('btech-mode').value = btechRecord?.mode || 'full_time';
    document.getElementById('btech-status').value = btechRecord?.completion_status || 'completed';

    if (d.education && d.education.branches) S.branches = [...d.education.branches];
    if (d.education_history && d.education_history.certifications) S.certifications = [...d.education_history.certifications];

    // 6. Branch Mappings
    if (d.branch_mappings && Object.keys(d.branch_mappings).length > 0) {
      S.branchMappings = { ...S.branchMappings, ...d.branch_mappings };
    }

    // 7. Experience & Records
    if (d.experience_records && d.experience_records.length > 0) {
      S.experienceRecords = [...d.experience_records];
    }
    if (d.experience) {
      document.getElementById('fresher-toggle').checked = (d.experience.fresher_allowed !== false);
      const maxYears = d.experience.max_years_experience_required ?? 0;
      if (d.experience.fresher_allowed && maxYears === 0) S.expVal = 'fresher';
      else if (maxYears <= 2) S.expVal = '0-2';
      else if (maxYears <= 5) S.expVal = '2-5';
      else S.expVal = '5+';
    }

    // 8. Licences
    if (d.licences && d.licences.length > 0) {
      const lmv = d.licences.find(l => l.category === 'LMV');
      if (lmv) document.getElementById('lic-lmv').value = lmv.validity_status;
      const hmv = d.licences.find(l => l.category === 'HMV');
      if (hmv) document.getElementById('lic-hmv').value = hmv.validity_status;
    } else if (d.education_history && d.education_history.has_driving_licence) {
      document.getElementById('lic-lmv').value = 'valid';
    }

    // 9. Physical & Medical
    if (d.physical) {
      if (d.physical.height_cm) document.getElementById('phys-height').value = d.physical.height_cm;
      if (d.physical.chest_normal_cm) document.getElementById('phys-chest-norm').value = d.physical.chest_normal_cm;
      if (d.physical.chest_expanded_cm) document.getElementById('phys-chest-exp').value = d.physical.chest_expanded_cm;
      document.getElementById('physical-tests-toggle').checked = !!d.physical.willing_physical_tests;
      document.getElementById('police-standards-toggle').checked = !!d.physical.willing_police_standards;
    } else if (d.constraints) {
      document.getElementById('physical-tests-toggle').checked = !!d.constraints.willing_physical_tests;
    }
    if (d.medical) {
      document.getElementById('med-color-blind').value = d.medical.has_color_blindness ? 'yes' : 'no';
      if (d.medical.eye_sight_specs) document.getElementById('med-eyesight').value = d.medical.eye_sight_specs;
    }

    // 10. Sectors & Organizations
    if (d.preferred_organizations) S.prefOrgs = [...d.preferred_organizations];
    if (d.avoid_organizations) S.avoidOrgs = [...d.avoid_organizations];

    const catMap = {
      central_government: 'Central Govt', state_government: 'State Govt', psu: 'PSU',
      banking: 'Banking', defense: 'Defense', autonomous_body: 'Autonomous'
    };
    if (d.job_categories) {
      S.sectors = d.job_categories.map(c => catMap[c] || c);
    }

    // 11. Role Preferences
    if (d.role_preferences) {
      if (d.role_preferences.preferred_roles) S.prefRoles = [...d.role_preferences.preferred_roles];
      if (d.role_preferences.avoid_roles) S.avoidRoles = [...d.role_preferences.avoid_roles];
      S.workNature = d.role_preferences.work_nature || 'desk_only';
      S.shiftPref = d.role_preferences.shift_preference || 'day_shifts_only';
      S.securityPref = d.role_preferences.job_security_preference || 'permanent_only';
    }

    // 12. Salary Preferences
    if (d.salary_preferences) {
      if (d.salary_preferences.min_gross_monthly_inr) document.getElementById('min-salary-inr').value = d.salary_preferences.min_gross_monthly_inr;
      document.getElementById('salary-hard-filter-toggle').checked = !!d.salary_preferences.is_hard_filter;
    }

    // 13. Constraints
    if (d.constraints) {
      document.getElementById('service-bond-toggle').checked = (d.constraints.service_bond_acceptable !== false);
      document.getElementById('exclude-high-fee-toggle').checked = !!d.constraints.exclude_high_fee_jobs;
      document.getElementById('exam-travel-toggle').checked = (d.constraints.willing_to_travel_for_exams !== false);
      if (d.constraints.max_application_fee != null) S.feeVal = String(d.constraints.max_application_fee);
      else S.feeVal = '';
    } else if (d.max_application_fee != null) {
      S.feeVal = String(d.max_application_fee);
    }

    if (d.hard_exclusions) S.hardExclusions = [...d.hard_exclusions];
    if (d.target_jobs) S.targetJobs = [...d.target_jobs];

    // 14. Document Readiness (Tier D)
    if (d.documents_readiness && Object.keys(d.documents_readiness).length > 0) {
      S.documentsReadiness = { ...S.documentsReadiness, ...d.documents_readiness };
    }

    // 15. Classification Behavior
    if (d.classification_preferences) {
      document.getElementById('unknown-handling-select').value = d.classification_preferences.unknown_handling || 'REVIEW';
      document.getElementById('hide-not-interested-toggle').checked = !!d.classification_preferences.hide_not_interested;
    }
    if (d.notification_preferences) {
      document.getElementById('alert-uncertain-toggle').checked = (d.notification_preferences.alert_on_uncertain !== false);
    }

  } catch (err) {
    console.error('Error loading profile:', err);
  }

  renderAll();
}

// =========================================================================
// RENDER HELPERS
// =========================================================================
function renderAll() {
  renderExperienceRecords();
  renderDocumentReadiness();
  renderBranchMatrix();
  renderSummary();

  renderTags('relocStates', 'reloc-states-wrap', '+ Add State');
  renderTags('branches', 'branch-tags', '+ Add Branch');
  renderTags('certifications', 'cert-tags', '+ Add Certification');
  renderTags('sector-tags', 'sector-tags', '+ Add Sector');
  renderTags('prefOrgs', 'pref-org-tags', '+ Add Org');
  renderTags('avoidOrgs', 'avoid-org-tags', '+ Add Org');
  renderTags('prefRoles', 'pref-role-tags', '+ Add Role');
  renderTags('avoidRoles', 'avoid-role-tags', '+ Add Avoided Role');
  renderTags('subjOther', 'subj-other-tags', '+ Add Subject');
  renderTags('hardExclusions', 'hard-exclusions-tags', '+ Add Hard Exclusion');
  renderTags('targetJobs', 'target-jobs-tags', '+ Add Target Job/Exam');

  syncSegButtons('exp-seg', S.expVal);
  syncSegButtons('fee-seg', S.feeVal);
  syncSegButtons('work-nature-seg', S.workNature);
  syncSegButtons('shift-seg', S.shiftPref);
  syncSegButtons('security-seg', S.securityPref);
}

// EXPERIENCE REPEATER
function renderExperienceRecords() {
  const c = document.getElementById('experience-records-container');
  if (!c) return;
  c.innerHTML = '';

  if (S.experienceRecords.length === 0) {
    c.innerHTML = '<div style="font-size: 12.5px; color: var(--t2); padding: 8px 0;">No employment history recorded (Currently registered as Fresher).</div>';
    return;
  }

  S.experienceRecords.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'repeater-card';
    card.innerHTML = `
      <div class="repeater-card-header">
        <span class="repeater-tag" style="background: rgba(52,199,89,.12); color: var(--green);">${escapeHtml((r.sector || 'private').toUpperCase())}</span>
        <button type="button" class="btn-repeater-del" onclick="deleteExpRecord(${idx})">Delete</button>
      </div>
      <div class="repeater-card-body">
        <div><b>${escapeHtml(r.employer)}</b> &middot; ${escapeHtml(r.designation || 'Role')}</div>
        <div class="repeater-card-sub">Duration: <b>${r.total_months || 0} Months</b> (${r.contract_type || 'regular'})</div>
        <div class="repeater-card-sub">Certificate: <b>${r.has_certificate ? '✓ Available' : '⚠ Missing'}</b></div>
      </div>
    `;
    c.appendChild(card);
  });
}

function deleteExpRecord(idx) {
  S.experienceRecords.splice(idx, 1);
  markDirty();
  renderExperienceRecords();
  renderSummary();
}

// DOCUMENT READINESS (TIER D)
function renderDocumentReadiness() {
  const grid = document.getElementById('doc-readiness-grid');
  if (!grid) return;
  grid.innerHTML = '';

  Object.values(S.documentsReadiness).forEach(doc => {
    const card = document.createElement('div');
    card.className = 'doc-card';
    card.innerHTML = `
      <div>
        <div class="doc-name">${escapeHtml(doc.name)}</div>
        <div class="doc-note">${escapeHtml(doc.notes || '')}</div>
      </div>
      <div>
        <select class="doc-select status-${doc.status}" onchange="updateDocStatus('${doc.document_key}', this.value)">
          <option value="AVAILABLE" ${doc.status === 'AVAILABLE' ? 'selected' : ''}>✓ Available &amp; Valid</option>
          <option value="RENEWAL_REQUIRED" ${doc.status === 'RENEWAL_REQUIRED' ? 'selected' : ''}>⚠ Renewal Required</option>
          <option value="EXPIRED" ${doc.status === 'EXPIRED' ? 'selected' : ''}>✕ Expired</option>
          <option value="NOT_AVAILABLE" ${doc.status === 'NOT_AVAILABLE' ? 'selected' : ''}>Not Possessed</option>
          <option value="NOT_APPLICABLE" ${doc.status === 'NOT_APPLICABLE' ? 'selected' : ''}>Not Applicable</option>
        </select>
      </div>
    `;
    grid.appendChild(card);
  });
}

function updateDocStatus(key, val) {
  if (S.documentsReadiness[key]) {
    S.documentsReadiness[key].status = val;
    markDirty();
    renderDocumentReadiness();
    renderSummary();
  }
}

// BRANCH MATRIX
function renderBranchMatrix() {
  const c = document.getElementById('branch-matrix-container');
  if (!c) return;
  c.innerHTML = '';

  DEFAULT_BRANCH_MATRIX_KEYS.forEach(bName => {
    const currentMode = S.branchMappings[bName] || 'ACCEPT';
    const row = document.createElement('div');
    row.className = 'branch-matrix-row';
    row.innerHTML = `
      <div class="branch-title">${escapeHtml(bName)}</div>
      <div class="matrix-toggles">
        <button type="button" class="matrix-opt ${currentMode === 'ACCEPT' ? 'active-accept' : ''}" onclick="setBranchStrictness('${bName}', 'ACCEPT')">ACCEPT</button>
        <button type="button" class="matrix-opt ${currentMode === 'POSSIBLY_ACCEPT' ? 'active-possibly' : ''}" onclick="setBranchStrictness('${bName}', 'POSSIBLY_ACCEPT')">POSSIBLY</button>
        <button type="button" class="matrix-opt ${currentMode === 'DO_NOT_ACCEPT' ? 'active-reject' : ''}" onclick="setBranchStrictness('${bName}', 'DO_NOT_ACCEPT')">EXCLUDE</button>
      </div>
    `;
    c.appendChild(row);
  });
}

function setBranchStrictness(bName, mode) {
  S.branchMappings[bName] = mode;
  markDirty();
  renderBranchMatrix();
}

// LIVE SUMMARY (SECTION 16)
function renderSummary() {
  const grid = document.getElementById('summary-grid-content');
  if (!grid) return;

  const cat = document.getElementById('cat-select') ? document.getElementById('cat-select').value : 'General';
  const btechBranch = document.getElementById('btech-branch') ? document.getElementById('btech-branch').value : 'Computer Science and Engineering';
  const btechPct = document.getElementById('btech-pct') ? document.getElementById('btech-pct').value : '';
  const btechCgpa = document.getElementById('btech-cgpa') ? document.getElementById('btech-cgpa').value : '';
  const btechScoreStr = btechPct ? `${btechPct}%` : (btechCgpa ? `${btechCgpa} CGPA` : 'Score unstated');

  const tenthPct = document.getElementById('tenth-pct') ? document.getElementById('tenth-pct').value : '';
  const tenthCgpa = document.getElementById('tenth-cgpa') ? document.getElementById('tenth-cgpa').value : '';
  const tenthScoreStr = tenthPct ? `${tenthPct}%` : (tenthCgpa ? `${tenthCgpa} CGPA` : 'Completed');

  const twelfthPct = document.getElementById('twelfth-pct') ? document.getElementById('twelfth-pct').value : '';
  const twelfthCgpa = document.getElementById('twelfth-cgpa') ? document.getElementById('twelfth-cgpa').value : '';
  const twelfthScoreStr = twelfthPct ? `${twelfthPct}%` : (twelfthCgpa ? `${twelfthCgpa} CGPA` : 'Completed');
  const twelfthStream = document.getElementById('twelfth-stream') ? document.getElementById('twelfth-stream').value : 'Science-PCM';

  const heightVal = document.getElementById('phys-height') ? document.getElementById('phys-height').value : '';

  // Document Tally
  let docsAvail = 0, docsWarn = 0;
  Object.values(S.documentsReadiness).forEach(d => {
    if (d.status === 'AVAILABLE') docsAvail++;
    if (d.status === 'RENEWAL_REQUIRED' || d.status === 'EXPIRED') docsWarn++;
  });

  grid.innerHTML = `
    <div class="summary-col">
      <div class="summary-col-title" style="color: var(--red);"><span class="badge-hard">Tier A</span> Hard Eligibility</div>
      <div class="summary-item"><b>Degree &amp; Branch</b> B.Tech in ${escapeHtml(btechBranch)} (${btechScoreStr})</div>
      <div class="summary-item"><b>12th Standard</b> ${escapeHtml(twelfthStream)} (${twelfthScoreStr}) &middot; ${document.getElementById('subj-maths')?.checked ? 'Maths ✓' : 'No Maths'}</div>
      <div class="summary-item"><b>10th Standard</b> Matriculation (${tenthScoreStr})</div>
      <div class="summary-item"><b>Category &amp; Quota</b> ${escapeHtml(cat)} &middot; Cutoff relaxation active</div>
      <div class="summary-item"><b>Physical / Licences</b> Height: ${heightVal ? heightVal + ' cm' : 'Unstated'} &middot; LMV: ${document.getElementById('lic-lmv')?.value || 'none'}</div>
    </div>

    <div class="summary-col">
      <div class="summary-col-title" style="color: var(--blue);"><span class="badge-pref">Tier B</span> Personal Preferences</div>
      <div class="summary-item"><b>Target Orgs</b> ${S.prefOrgs.slice(0, 4).join(', ') || 'None'}</div>
      <div class="summary-item"><b>Preferred Roles</b> ${S.prefRoles.slice(0, 3).join(', ') || 'Technical'}</div>
      <div class="summary-item"><b>Duty Nature</b> ${S.workNature.replace('_', ' ')} &middot; ${S.securityPref.replace('_', ' ')}</div>
      <div class="summary-item"><b>Salary Filter</b> ₹${document.getElementById('min-salary-inr')?.value || '40000'}/mo (${document.getElementById('salary-hard-filter-toggle')?.checked ? 'Hard Filter' : 'Preference'})</div>
    </div>

    <div class="summary-col">
      <div class="summary-col-title" style="color: var(--orange);"><span class="badge-cons">Tier C</span> Practical Constraints</div>
      <div class="summary-item"><b>Application Fee</b> Max: ${S.feeVal ? '₹' + S.feeVal : 'Any'}</div>
      <div class="summary-item"><b>Physical PET</b> ${document.getElementById('physical-tests-toggle')?.checked ? 'Acceptable' : 'Avoided'}</div>
      <div class="summary-item"><b>Service Bonds</b> ${document.getElementById('service-bond-toggle')?.checked ? 'Acceptable' : 'Refused'}</div>
      <div class="summary-item"><b>Hard Exclusions</b> ${S.hardExclusions.slice(0, 3).join(', ') || 'None'}</div>
    </div>

    <div class="summary-col">
      <div class="summary-col-title" style="color: var(--purple);"><span class="badge-ready">Tier D</span> Document Readiness</div>
      <div class="summary-item"><b>Ready Documents</b> <span style="color: var(--green); font-weight: 600;">${docsAvail} Verified</span></div>
      <div class="summary-item"><b>Document Warnings</b> <span style="color: ${docsWarn > 0 ? 'var(--orange)' : 'var(--t2)'}; font-weight: 600;">${docsWarn} Renewal/Action</span></div>
      <div class="summary-item"><b>EWS / OBC Status</b> ${cat === 'EWS' ? 'Current Financial Year' : (cat === 'OBC' ? 'Central NCL valid' : 'Standard')}</div>
      <div class="summary-item"><b>Readiness Verdict</b> ${docsWarn > 0 ? '⚠ Warning on application' : '✓ Application Ready'}</div>
    </div>
  `;
}

// TAGS RENDERER
function renderTags(stateKey, containerId, addLabel) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '';

  const list = (stateKey === 'sector-tags') ? S.sectors : S[stateKey];
  (list || []).forEach((item, idx) => {
    const span = document.createElement('span');
    span.className = 'tag';
    span.innerHTML = `${escapeHtml(item)} <span class="tag-x" onclick="removeTag('${stateKey}', ${idx})">&times;</span>`;
    el.appendChild(span);
  });

  const addBtn = document.createElement('span');
  addBtn.className = 'tag-add';
  addBtn.innerHTML = `${addLabel || '+ Add'}`;
  addBtn.onclick = () => promptAddTag(stateKey);
  el.appendChild(addBtn);
}

function promptAddTag(stateKey) {
  const val = prompt('Enter new value:');
  if (!val || !val.trim()) return;
  const clean = val.trim();
  if (stateKey === 'sector-tags') {
    if (!S.sectors.includes(clean)) S.sectors.push(clean);
  } else {
    if (!S[stateKey].includes(clean)) S[stateKey].push(clean);
  }
  markDirty();
  renderAll();
}

function removeTag(stateKey, idx) {
  if (stateKey === 'sector-tags') {
    S.sectors.splice(idx, 1);
  } else {
    S[stateKey].splice(idx, 1);
  }
  markDirty();
  renderAll();
}

// CONDITIONAL PANELS
function handleCategoryChange() {
  const cat = document.getElementById('cat-select').value;
  const pEws = document.getElementById('panel-ews');
  const pObc = document.getElementById('panel-obc');
  const pScst = document.getElementById('panel-scst');

  pEws.classList.toggle('show', cat === 'EWS');
  pObc.classList.toggle('show', cat === 'OBC');
  pScst.classList.toggle('show', cat === 'SC' || cat === 'ST');
  markDirty();
  renderSummary();
}

function togglePwbdPanel() {
  const checked = document.getElementById('pwbd-toggle').checked;
  document.getElementById('panel-pwbd').classList.toggle('show', checked);
  markDirty();
}

function toggleEsmPanel() {
  const checked = document.getElementById('esm-toggle').checked;
  document.getElementById('panel-esm').classList.toggle('show', checked);
  markDirty();
}

// CONTROL HELPERS
function setExpBucket(val) { S.expVal = val; syncSegButtons('exp-seg', val); markDirty(); }
function setFeeVal(val) { S.feeVal = val; syncSegButtons('fee-seg', val); markDirty(); renderSummary(); }
function setWorkNature(val) { S.workNature = val; syncSegButtons('work-nature-seg', val); markDirty(); renderSummary(); }
function setShiftPref(val) { S.shiftPref = val; syncSegButtons('shift-seg', val); markDirty(); }
function setSecurityPref(val) { S.securityPref = val; syncSegButtons('security-seg', val); markDirty(); renderSummary(); }

function syncSegButtons(containerId, activeVal) {
  const wrap = document.getElementById(containerId);
  if (!wrap) return;
  wrap.querySelectorAll('.seg-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-val') === activeVal);
  });
}

function updateDobAgeDisplay() {
  const dobStr = document.getElementById('dob').value;
  const label = document.getElementById('dob-calc-label');
  if (!dobStr) {
    label.textContent = 'Calculates exact age on notification cutoff dates';
    return;
  }
  const dob = new Date(dobStr);
  const now = new Date();
  let age = now.getFullYear() - dob.getFullYear();
  const m = now.getMonth() - dob.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < dob.getDate())) age--;
  label.textContent = `Current Age: ${age} years old · Used for automated cutoff evaluation`;
  markDirty();
  renderSummary();
}

function markDirty() {
  const el = document.getElementById('save-status-text');
  if (el) el.textContent = 'Unsaved changes';
  const dot = document.getElementById('status-dot');
  if (dot) dot.style.background = 'var(--orange)';
}

// MODAL FOR EXPERIENCE
function openAddExpModal() { document.getElementById('modal-add-exp').classList.add('show'); }
function closeAddExpModal() { document.getElementById('modal-add-exp').classList.remove('show'); }
function submitAddExp() {
  const employer = document.getElementById('m-exp-employer').value.trim() || 'Company';
  const sector = document.getElementById('m-exp-sector').value;
  const role = document.getElementById('m-exp-role').value.trim() || 'Role';
  const months = parseInt(document.getElementById('m-exp-months').value, 10) || 12;
  const contract = document.getElementById('m-exp-contract').value;
  const cert = document.getElementById('m-exp-cert').checked;

  S.experienceRecords.push({
    employer, sector, designation: role, total_months: months,
    mode: "full_time", contract_type: contract, has_certificate: cert, is_current: false, is_relevant: true
  });
  closeAddExpModal();
  markDirty();
  renderExperienceRecords();
  renderSummary();
}

// =========================================================================
// SAVE & RE-EVALUATE PIPELINE (WITH SILENT AUTO-SAVE SUPPORT)
// =========================================================================
async function saveProfile(triggerReeval, isAutoSave = false) {
  const btnSave = document.getElementById('btnSaveOnly');
  const btnReeval = document.getElementById('btnSaveReeval');
  if (!isAutoSave) {
    if (btnSave) btnSave.disabled = true;
    if (btnReeval) btnReeval.disabled = true;
  }
  const statusEl = document.getElementById('save-status-text');
  const statusDot = document.getElementById('status-dot');
  if (statusEl) statusEl.textContent = isAutoSave ? 'Saving changes...' : 'Saving profile...';
  if (statusDot) statusDot.style.background = 'var(--orange)';

  const expYears = S.expVal === 'fresher' ? 0 : (S.expVal === '0-2' ? 2 : (S.expVal === '2-5' ? 5 : 10));

  const sectorRevMap = {
    'Central Govt': 'central_government', 'State Govt': 'state_government', 'PSU': 'psu',
    'Banking': 'banking', 'Defense': 'defense', 'Autonomous': 'autonomous_body'
  };
  const mappedSectors = S.sectors.map(s => sectorRevMap[s] || s.toLowerCase().replace(/\s+/g, '_'));

  // Licences
  const licencesList = [];
  const lmvVal = document.getElementById('lic-lmv').value;
  if (lmvVal !== 'none') licencesList.push({ category: 'LMV', validity_status: lmvVal, expiry_date: null });
  const hmvVal = document.getElementById('lic-hmv').value;
  if (hmvVal !== 'none') licencesList.push({ category: 'HMV', validity_status: hmvVal, expiry_date: null });
  const councilVal = document.getElementById('lic-council').value;
  if (councilVal !== 'none') licencesList.push({ category: councilVal, validity_status: 'valid', expiry_date: null });

  // Scores (allow either Percentage OR CGPA)
  const tenthPct = parseFloat(document.getElementById('tenth-pct').value) || null;
  const tenthCgpa = parseFloat(document.getElementById('tenth-cgpa').value) || null;

  const twelfthPct = parseFloat(document.getElementById('twelfth-pct').value) || null;
  const twelfthCgpa = parseFloat(document.getElementById('twelfth-cgpa').value) || null;

  let btechPct = parseFloat(document.getElementById('btech-pct').value) || null;
  const btechCgpa = parseFloat(document.getElementById('btech-cgpa').value) || null;
  if (btechPct == null && btechCgpa != null) {
    btechPct = Math.round(btechCgpa * 9.5 * 10) / 10;
  }

  // Exact 3 Chronological Education Records
  const eduRecords = [
    {
      level: "10th",
      degree_name: "Secondary School Certificate (10th)",
      branch: "All Subjects",
      institution_board: document.getElementById('tenth-board').value.trim() || null,
      passing_year: parseInt(document.getElementById('tenth-year').value, 10) || null,
      percentage: tenthPct,
      cgpa: tenthCgpa,
      mode: "full_time",
      completion_status: "completed"
    },
    {
      level: "12th",
      degree_name: "Senior Secondary Certificate (12th)",
      branch: document.getElementById('twelfth-stream').value,
      institution_board: document.getElementById('twelfth-board').value.trim() || null,
      passing_year: parseInt(document.getElementById('twelfth-year').value, 10) || null,
      percentage: twelfthPct,
      cgpa: twelfthCgpa,
      mode: "full_time",
      completion_status: "completed"
    },
    {
      level: "bachelors",
      degree_name: "B.Tech",
      branch: document.getElementById('btech-branch').value.trim() || "Computer Science and Engineering",
      institution_board: document.getElementById('btech-univ').value.trim() || null,
      passing_year: parseInt(document.getElementById('btech-year').value, 10) || null,
      percentage: btechPct,
      cgpa: btechCgpa,
      mode: document.getElementById('btech-mode').value,
      completion_status: document.getElementById('btech-status').value
    }
  ];

  // Compile payload across all 4 tiers
  const payload = {
    // TIER A: HARD ELIGIBILITY
    personal: {
      full_name: document.getElementById('full-name').value.trim() || null,
      gender: document.getElementById('gender').value,
      nationality: document.getElementById('nationality').value,
      state_of_domicile: document.getElementById('domicile-state').value || null,
      current_state: document.getElementById('current-state').value.trim() || null,
      current_city: document.getElementById('current-city').value.trim() || null,
      permanent_state: document.getElementById('permanent-state').value.trim() || null,
      local_area_district: document.getElementById('local-area').value.trim() || null,
      willing_to_relocate: true,
      willing_to_relocate_all_india: document.getElementById('all-india-toggle').checked,
      preferred_relocation_states: S.relocStates
    },
    date_of_birth: document.getElementById('dob').value || null,
    age: {
      maximum: 30,
      category: document.getElementById('cat-select').value,
      category_age_relaxations: document.getElementById('age-relax-toggle').checked ? { OBC: 3, SC: 5, ST: 5, PwD: 10, 'Ex-Serviceman': 5 } : {}
    },
    education: {
      minimum_level: "bachelors",
      accepted_degrees: ["B.Tech", "B.E.", "Bachelor of Technology", "Bachelor of Engineering", "Graduation in Engineering", "Any Degree"],
      branches: S.branches.length ? S.branches : ["Computer Science", "Information Technology", "CSE", "IT"],
      minimum_percentage: btechPct || 60
    },
    education_records: eduRecords,
    subjects_10_12: {
      twelfth_stream: document.getElementById('twelfth-stream').value,
      studied_maths_12th: document.getElementById('subj-maths').checked,
      studied_physics_12th: document.getElementById('subj-physics').checked,
      studied_chemistry_12th: document.getElementById('subj-chemistry').checked,
      studied_biology_12th: document.getElementById('subj-biology').checked,
      studied_computer_science_12th: document.getElementById('subj-cs').checked,
      studied_english: document.getElementById('subj-english').checked,
      other_subjects: S.subjOther
    },
    education_history: {
      tenth_board: document.getElementById('tenth-board').value.trim() || null,
      tenth_year: parseInt(document.getElementById('tenth-year').value, 10) || null,
      tenth_percentage: tenthPct,
      tenth_cgpa: tenthCgpa,
      twelfth_board: document.getElementById('twelfth-board').value.trim() || null,
      twelfth_year: parseInt(document.getElementById('twelfth-year').value, 10) || null,
      twelfth_stream: document.getElementById('twelfth-stream').value,
      twelfth_percentage: twelfthPct,
      twelfth_cgpa: twelfthCgpa,
      graduation_degree: "B.Tech",
      graduation_branch: document.getElementById('btech-branch').value.trim() || "Computer Science and Engineering",
      graduation_university: document.getElementById('btech-univ').value.trim() || null,
      graduation_year: parseInt(document.getElementById('btech-year').value, 10) || null,
      graduation_percentage: btechPct,
      graduation_cgpa: btechCgpa,
      has_driving_licence: (lmvVal === 'valid'),
      certifications: S.certifications
    },
    branch_mappings: S.branchMappings,
    experience: {
      fresher_allowed: document.getElementById('fresher-toggle').checked,
      max_years_experience_required: expYears
    },
    experience_records: S.experienceRecords,
    licences: licencesList,
    physical: {
      height_cm: parseFloat(document.getElementById('phys-height').value) || null,
      chest_normal_cm: parseFloat(document.getElementById('phys-chest-norm').value) || null,
      chest_expanded_cm: parseFloat(document.getElementById('phys-chest-exp').value) || null,
      weight_kg: null,
      willing_physical_tests: document.getElementById('physical-tests-toggle').checked,
      willing_running: document.getElementById('physical-tests-toggle').checked,
      willing_jump: document.getElementById('physical-tests-toggle').checked,
      willing_police_standards: document.getElementById('police-standards-toggle').checked
    },
    medical: {
      willing_medical_exam: true,
      has_color_blindness: (document.getElementById('med-color-blind').value === 'yes'),
      visual_standards_acceptable: true,
      eye_sight_specs: document.getElementById('med-eyesight').value.trim() || null
    },

    // TIER B: PERSONAL PREFERENCES
    preferred_organizations: S.prefOrgs,
    avoid_organizations: S.avoidOrgs,
    job_categories: mappedSectors,
    role_preferences: {
      preferred_roles: S.prefRoles,
      avoid_roles: S.avoidRoles,
      work_nature: S.workNature,
      job_security_preference: S.securityPref,
      shift_preference: S.shiftPref
    },
    salary_preferences: {
      min_gross_monthly_inr: parseInt(document.getElementById('min-salary-inr').value, 10) || null,
      min_basic_pay_inr: null,
      preferred_pay_level: null,
      is_hard_filter: document.getElementById('salary-hard-filter-toggle').checked
    },

    // TIER C: PRACTICAL CONSTRAINTS
    constraints: {
      willing_physical_tests: document.getElementById('physical-tests-toggle').checked,
      max_application_fee: S.feeVal ? parseInt(S.feeVal, 10) : null,
      exclude_high_fee_jobs: document.getElementById('exclude-high-fee-toggle').checked,
      willing_to_travel_for_exams: document.getElementById('exam-travel-toggle').checked,
      max_travel_distance_km: null,
      service_bond_acceptable: document.getElementById('service-bond-toggle').checked,
      max_bond_years: 3,
      transfer_tolerance: "state_or_district",
      min_salary_gross_monthly: parseInt(document.getElementById('min-salary-inr').value, 10) || null
    },
    max_application_fee: S.feeVal ? parseInt(S.feeVal, 10) : null,
    hard_exclusions: S.hardExclusions,
    target_jobs: S.targetJobs,

    // TIER D: DOCUMENT READINESS
    documents_readiness: S.documentsReadiness,

    // SYSTEM BEHAVIOR
    matching_mode: "balanced",
    location: {
      allowed: document.getElementById('all-india-toggle').checked ? ["All India"] : S.relocStates,
      exclude_locations: []
    },
    classification_preferences: {
      unknown_handling: document.getElementById('unknown-handling-select').value,
      hide_not_interested: document.getElementById('hide-not-interested-toggle').checked
    },
    notification_preferences: {
      alert_on_uncertain: document.getElementById('alert-uncertain-toggle').checked,
      min_vacancies: 1,
      min_salary_inr_month: 0
    }
  };

  // Local draft backup
  try {
    localStorage.setItem('job_alerts_profile_backup', JSON.stringify(payload));
  } catch(e) {}

  try {
    const putRes = await fetch('/api/requirements', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!putRes.ok) throw new Error('Failed to update profile');

    if (triggerReeval) {
      showToast('Profile saved. Re-evaluating circulars...');
      const reevalRes = await fetch('/api/requirements/re-evaluate', { method: 'POST' });
      if (!reevalRes.ok) throw new Error('Re-evaluation error');
      const reevalData = await reevalRes.json();
      const counts = reevalData.counts || {};
      showToast(`✓ Profile saved & ${counts.total || 46} jobs re-evaluated! (${counts.ELIGIBLE || 0} eligible)`);
    } else if (!isAutoSave) {
      showToast('✓ Profile successfully updated across all 4 tiers');
    }
    if (statusEl) statusEl.textContent = isAutoSave ? '✓ Automatically saved' : 'All profile layers synchronized';
    if (statusDot) statusDot.style.background = 'var(--green)';
  } catch (err) {
    console.error(err);
    if (!isAutoSave) showToast('Error: ' + err.message);
    if (statusEl) statusEl.textContent = 'Save failed: ' + err.message;
    if (statusDot) statusDot.style.background = 'var(--red)';
  } finally {
    if (btnSave) btnSave.disabled = false;
    if (btnReeval) btnReeval.disabled = false;
  }
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3200);
}

function escapeHtml(s) {
  return String(s || '').replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' })[c]);
}

window.addEventListener('DOMContentLoaded', () => {
  loadProfile();

  // Attach global auto-save listeners so entered values are never discarded
  document.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      scheduleAutoSave();
    }
  });
  document.addEventListener('change', (e) => {
    if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') {
      scheduleAutoSave();
    }
  });
});
</script>
</body>
</html>
"""
