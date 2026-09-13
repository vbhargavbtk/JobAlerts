"""
HTML Template for Apple-Inspired Personal Job Alerts
Clean, calm, minimalist interface with progressive disclosure, light aesthetic (#F5F5F7),
SF Pro typography, segmented controls, grouped cards, and slide-over details sheet.
"""

JOBS_DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Job Alerts</title>
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
      --status-green: #248A3D;
      --status-green-bg: #E8F5E9;
      --status-green-dot: #34C759;
      --status-amber: #B26A00;
      --status-amber-bg: #FFF4E5;
      --status-amber-dot: #FF9500;
      --status-red: #D70015;
      --status-red-bg: #FEECEB;
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-xl: 20px;
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

    /* GLOBAL HEADER (APPLE STYLE) */
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
      display: flex;
      align-items: center;
      gap: 6px;
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
      cursor: pointer;
    }

    .nav-tab:hover {
      color: var(--text-primary);
    }

    .nav-tab.active {
      color: var(--text-primary);
      font-weight: 600;
    }

    .header-secondary-actions {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .header-link-secondary {
      font-size: 13px;
      color: var(--text-secondary);
      text-decoration: none;
      transition: color 0.15s;
    }

    .header-link-secondary:hover {
      color: var(--accent-blue);
    }

    /* MAIN CONTAINER */
    main {
      max-width: 1080px;
      width: 100%;
      margin: 0 auto;
      padding: 48px 24px 80px 24px;
      flex: 1;
    }

    /* HERO SECTION */
    .hero-container {
      text-align: center;
      margin-bottom: 36px;
    }

    .hero-headline {
      font-size: 38px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .hero-subheadline {
      font-size: 17px;
      color: var(--text-secondary);
      font-weight: 400;
      margin-bottom: 16px;
    }

    .hero-summary-bar {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      font-size: 13px;
      color: var(--text-secondary);
      background: rgba(0, 0, 0, 0.03);
      padding: 6px 16px;
      border-radius: var(--radius-full);
    }

    .summary-dot {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: var(--text-tertiary);
    }

    /* SEARCH & FILTER CONTROLS */
    .controls-wrapper {
      max-width: 720px;
      margin: 0 auto 40px auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .search-container {
      position: relative;
      width: 100%;
    }

    .search-icon-svg {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      width: 16px;
      height: 16px;
      color: var(--text-tertiary);
      pointer-events: none;
    }

    .search-field {
      width: 100%;
      height: 46px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0 16px 0 44px;
      font-size: 15px;
      color: var(--text-primary);
      outline: none;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }

    .search-field:focus {
      border-color: var(--accent-blue);
      box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15);
    }

    .search-field::placeholder {
      color: var(--text-tertiary);
    }

    /* SEGMENTED PILLS BAR */
    .filters-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }

    .segmented-control {
      display: inline-flex;
      background: #EAEAEF;
      padding: 3px;
      border-radius: var(--radius-full);
      gap: 2px;
    }

    .segment-btn {
      border: none;
      background: transparent;
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      border-radius: var(--radius-full);
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .segment-btn:hover {
      color: var(--text-primary);
    }

    .segment-btn.active {
      background: #FFFFFF;
      color: var(--text-primary);
      font-weight: 600;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }

    .count-chip {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: var(--radius-full);
      background: rgba(0, 0, 0, 0.06);
      color: var(--text-secondary);
    }

    .segment-btn.active .count-chip {
      background: rgba(0, 0, 0, 0.08);
      color: var(--text-primary);
    }

    .secondary-filters {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .filter-chip {
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      font-size: 13px;
      color: var(--text-secondary);
      padding: 6px 14px;
      border-radius: var(--radius-full);
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      user-select: none;
      white-space: nowrap;
    }

    .filter-chip:hover {
      border-color: rgba(0, 0, 0, 0.18);
      color: var(--text-primary);
    }

    .filter-chip.active {
      background: var(--text-primary);
      color: #FFFFFF;
      border-color: var(--text-primary);
    }

    .filter-select-pill {
      border: 1px solid var(--border-subtle);
      background-color: var(--bg-surface);
      font-size: 13px;
      color: var(--text-secondary);
      padding: 6px 28px 6px 14px;
      border-radius: var(--radius-full);
      cursor: pointer;
      font-weight: 500;
      transition: all 0.15s ease;
      outline: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2386868B' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 10px center;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
      font-family: inherit;
      white-space: nowrap;
    }

    .filter-select-pill:hover {
      border-color: rgba(0, 0, 0, 0.22);
      color: var(--text-primary);
    }

    .filter-select-pill.active {
      background-color: rgba(0, 113, 227, 0.08);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
      font-weight: 600;
    }

    .filter-row-secondary {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      width: 100%;
      margin-top: 4px;
    }

    .btn-clear-filters {
      border: none;
      background: transparent;
      color: var(--status-red);
      font-size: 12.5px;
      font-weight: 500;
      padding: 5px 10px;
      border-radius: var(--radius-full);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: background 0.15s ease;
    }

    .btn-clear-filters:hover {
      background: var(--status-red-bg);
    }

    /* SECTION HEADER */
    .section-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .section-title {
      font-size: 20px;
      font-weight: 600;
      letter-spacing: -0.015em;
      color: var(--text-primary);
    }

    .section-count {
      font-size: 13px;
      color: var(--text-secondary);
    }

    /* JOB CARDS LIST */
    .jobs-list {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .job-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 24px;
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: relative;
    }

    .job-card:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
      border-color: rgba(0, 0, 0, 0.14);
    }

    .card-meta-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .card-org-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      letter-spacing: -0.005em;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      font-weight: 500;
      padding: 3px 10px;
      border-radius: var(--radius-full);
    }

    .status-badge.status-eligible {
      background: var(--status-green-bg);
      color: var(--status-green);
    }

    .status-badge.status-eligible .status-dot {
      background: var(--status-green-dot);
    }

    .status-badge.status-uncertain {
      background: var(--status-amber-bg);
      color: var(--status-amber);
    }

    .status-badge.status-uncertain .status-dot {
      background: var(--status-amber-dot);
    }

    .status-badge.status-ineligible {
      background: var(--status-red-bg);
      color: var(--status-red);
    }

    .status-badge.status-ineligible .status-dot {
      background: #FF3B30;
    }

    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }

    .card-title-row {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .card-post-title {
      font-size: 19px;
      font-weight: 600;
      letter-spacing: -0.015em;
      color: var(--text-primary);
      line-height: 1.35;
    }

    .card-key-attributes {
      font-size: 13px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .attribute-separator {
      color: var(--border-divider);
    }

    .card-description-text {
      font-size: 14px;
      line-height: 1.55;
      color: #3A3A3C;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 12px;
      border-top: 1px solid rgba(0, 0, 0, 0.04);
      gap: 12px;
      flex-wrap: wrap;
    }

    .footer-metadata {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      color: var(--text-tertiary);
    }

    .fee-pill {
      font-size: 11.5px;
      font-weight: 500;
      padding: 2px 8px;
      border-radius: var(--radius-full);
      background: var(--bg-surface-secondary);
      color: var(--text-secondary);
    }

    .fee-pill.fee-free {
      background: rgba(52, 199, 89, 0.12);
      color: var(--status-green);
    }

    .footer-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn-details {
      font-size: 13px;
      font-weight: 500;
      color: var(--accent-blue);
      text-decoration: none;
      padding: 6px 10px;
      border-radius: var(--radius-sm);
      transition: background 0.15s;
      background: transparent;
      border: none;
      cursor: pointer;
    }

    .btn-details:hover {
      background: var(--accent-blue-subtle);
    }

    .btn-apply-primary {
      font-size: 13px;
      font-weight: 500;
      color: #FFFFFF;
      background: var(--accent-blue);
      padding: 7px 16px;
      border-radius: var(--radius-full);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: background 0.15s ease;
      border: none;
      cursor: pointer;
    }

    .btn-apply-primary:hover {
      background: var(--accent-blue-hover);
    }

    .btn-icon-action {
      border: 1px solid transparent;
      background: transparent;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: var(--radius-full);
      transition: all 0.15s ease;
      color: var(--text-tertiary);
      padding: 0;
      line-height: 1;
      position: relative;
    }

    .btn-icon-action:hover {
      background: var(--bg-surface-secondary);
      color: var(--text-primary);
      border-color: rgba(0, 0, 0, 0.08);
    }

    .btn-star.active {
      color: #FF9500;
      background: rgba(255, 149, 0, 0.12);
      border-color: rgba(255, 149, 0, 0.28);
    }

    .btn-star.active:hover {
      background: rgba(255, 149, 0, 0.18);
    }

    .btn-applied.active {
      color: #34C759;
      background: rgba(52, 199, 89, 0.12);
      border-color: rgba(52, 199, 89, 0.28);
    }

    .btn-applied.active:hover {
      background: rgba(52, 199, 89, 0.18);
    }

    .btn-delete {
      color: var(--text-tertiary);
    }

    .btn-delete:hover {
      background: var(--status-red-bg);
      color: var(--status-red);
      border-color: rgba(215, 0, 21, 0.2);
    }

    .applied-date-badge {
      font-size: 11.5px;
      font-weight: 500;
      color: #248A3D;
      background: var(--status-green-bg);
      padding: 3px 8px;
      border-radius: var(--radius-full);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .sheet-status-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 6px;
      flex-wrap: wrap;
    }

    .btn-sheet-toggle {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: var(--radius-full);
      font-size: 13px;
      font-weight: 500;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .btn-sheet-toggle:hover {
      background: var(--bg-surface-secondary);
      color: var(--text-primary);
    }

    .btn-sheet-toggle.star-active {
      background: rgba(255, 149, 0, 0.12);
      color: #D97706;
      border-color: rgba(255, 149, 0, 0.3);
      font-weight: 600;
    }

    .btn-sheet-toggle.applied-active {
      background: rgba(52, 199, 89, 0.12);
      color: #248A3D;
      border-color: rgba(52, 199, 89, 0.3);
      font-weight: 600;
    }

    .btn-sheet-toggle.btn-sheet-delete {
      color: var(--status-red);
      border-color: rgba(215, 0, 21, 0.25);
      background: var(--status-red-bg);
    }

    .btn-sheet-toggle.btn-sheet-delete:hover {
      background: #FDDCDA;
      color: #B20010;
    }

    /* SLIDE-OVER SHEET (APPLE STYLE) */
    .sheet-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.25);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      z-index: 1000;
      display: none;
      justify-content: flex-end;
      opacity: 0;
      transition: opacity 0.25s ease;
    }

    .sheet-overlay.open {
      display: flex;
      opacity: 1;
    }

    .sheet-panel {
      background: #FFFFFF;
      width: 100%;
      max-width: 580px;
      height: 100%;
      box-shadow: -10px 0 30px rgba(0, 0, 0, 0.08);
      display: flex;
      flex-direction: column;
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .sheet-overlay.open .sheet-panel {
      transform: translateX(0);
    }

    .sheet-header {
      padding: 20px 28px;
      border-bottom: 1px solid var(--border-divider);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      background: #FFFFFF;
      z-index: 10;
    }

    .sheet-close-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--bg-surface-secondary);
      border: none;
      color: var(--text-secondary);
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s;
    }

    .sheet-close-btn:hover {
      background: var(--bg-surface-tertiary);
      color: var(--text-primary);
    }

    .sheet-body {
      padding: 32px 28px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 28px;
    }

    .sheet-hero-section {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .sheet-org {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .sheet-title {
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      line-height: 1.25;
    }

    .sheet-cta-bar {
      margin-top: 8px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .btn-sheet-apply {
      width: 100%;
      padding: 12px;
      background: var(--accent-blue);
      color: #FFFFFF;
      text-align: center;
      border-radius: var(--radius-md);
      font-size: 14px;
      font-weight: 500;
      text-decoration: none;
      display: block;
      transition: background 0.15s;
    }

    .btn-sheet-apply:hover {
      background: var(--accent-blue-hover);
    }

    .btn-sheet-pdf {
      width: 100%;
      padding: 10px;
      background: var(--bg-surface-secondary);
      color: var(--text-primary);
      text-align: center;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 500;
      text-decoration: none;
      display: block;
      transition: background 0.15s;
    }

    .btn-sheet-pdf:hover {
      background: var(--bg-surface-tertiary);
    }

    .sheet-section {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .sheet-section-heading {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
    }

    .sheet-specs-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      background: var(--bg-surface-secondary);
      border-radius: var(--radius-md);
      padding: 16px;
    }

    .spec-item {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .spec-label {
      font-size: 11px;
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .spec-val {
      font-size: 13.5px;
      font-weight: 500;
      color: var(--text-primary);
    }

    .criteria-checklist {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .criteria-row {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 13.5px;
      padding: 8px 12px;
      background: var(--bg-surface-secondary);
      border-radius: var(--radius-sm);
    }

    .criteria-indicator {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: bold;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .criteria-pass {
      background: var(--status-green-bg);
      color: var(--status-green);
    }

    .criteria-warn {
      background: var(--status-amber-bg);
      color: var(--status-amber);
    }

    .tag-cloud {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .spec-tag {
      font-size: 12px;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      background: var(--bg-surface-secondary);
      color: var(--text-primary);
    }

    .collapsible-debug {
      margin-top: 10px;
      border-top: 1px solid var(--border-divider);
      padding-top: 16px;
    }

    .collapsible-debug summary {
      font-size: 12px;
      color: var(--text-tertiary);
      cursor: pointer;
      outline: none;
    }

    .json-inspector {
      background: var(--bg-surface-secondary);
      border-radius: var(--radius-sm);
      padding: 12px;
      font-family: var(--font-mono);
      font-size: 11.5px;
      color: var(--text-secondary);
      white-space: pre-wrap;
      max-height: 200px;
      overflow-y: auto;
      margin-top: 8px;
    }

    /* EMPTY STATE */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }

    .empty-title {
      font-size: 17px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .empty-subtitle {
      font-size: 14px;
      color: var(--text-secondary);
      max-width: 380px;
    }

    .btn-reset-filters {
      font-size: 13px;
      color: var(--accent-blue);
      background: transparent;
      border: none;
      cursor: pointer;
      font-weight: 500;
      margin-top: 4px;
    }

    /* TOAST */
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

    @media (max-width: 680px) {
      main {
        padding: 32px 16px 60px 16px;
      }
      .hero-headline {
        font-size: 28px;
      }
      .card-post-title {
        font-size: 17px;
      }
      .sheet-panel {
        max-width: 100%;
      }
    }

    .btn-clear-eligible {
      font-size: 12px;
      font-weight: 500;
      color: var(--status-red);
      background: var(--status-red-bg);
      border: 1px solid rgba(215, 0, 21, 0.2);
      border-radius: var(--radius-full);
      padding: 3px 10px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s ease;
    }

    .btn-clear-eligible:hover {
      background: #FDDCDA;
      color: #B20010;
    }

    /* APPLE-STYLE CONFIRMATION MODAL */
    .confirm-modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 1200;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    .confirm-modal-overlay.open {
      opacity: 1;
    }

    .confirm-modal-card {
      background: var(--bg-surface);
      border-radius: var(--radius-xl);
      max-width: 400px;
      width: 100%;
      padding: 28px 24px 20px 24px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.18);
      text-align: center;
      transform: scale(0.95);
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .confirm-modal-overlay.open .confirm-modal-card {
      transform: scale(1);
    }

    .confirm-modal-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--status-red-bg);
      color: var(--status-red);
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px auto;
    }

    .confirm-modal-title {
      font-size: 17px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .confirm-modal-desc {
      font-size: 13.5px;
      color: var(--text-secondary);
      line-height: 1.5;
      margin-bottom: 24px;
    }

    .confirm-modal-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn-modal-cancel {
      flex: 1;
      padding: 9px 16px;
      font-size: 13.5px;
      font-weight: 500;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-divider);
      background: var(--bg-surface-secondary);
      color: var(--text-primary);
      cursor: pointer;
      transition: background 0.15s;
    }

    .btn-modal-cancel:hover {
      background: var(--bg-surface-tertiary);
    }

    .btn-modal-confirm-delete {
      flex: 1;
      padding: 9px 16px;
      font-size: 13.5px;
      font-weight: 500;
      border-radius: var(--radius-full);
      border: none;
      background: var(--status-red);
      color: #FFFFFF;
      cursor: pointer;
      transition: background 0.15s;
    }

    .btn-modal-confirm-delete:hover {
      background: #B20010;
    }
  </style>
</head>
<body>
  <!-- UNIFIED NAV -->
  <header>
    <div class="header-inner">
      <a href="/jobs" class="brand-logo">Job Alerts</a>
      <nav class="nav-tabs">
        <a href="/jobs" class="nav-tab active" id="navJobs" onclick="navigateToView('jobs', event)">Jobs</a>
        <a href="/plan-to-apply" class="nav-tab" id="navPlan" onclick="navigateToView('plan_to_apply', event)">⭐ Plan to Apply</a>
        <a href="/applied" class="nav-tab" id="navApplied" onclick="navigateToView('applied', event)">✓ Applied</a>
        <a href="/admin/requirements" class="nav-tab" id="navProfile">Profile &amp; Rules</a>
        <a href="/admin/channels" class="nav-tab" id="navChannels">Channels</a>
      </nav>
    </div>
  </header>

  <main>
    <!-- HERO SECTION -->
    <div class="hero-container">
      <h1 class="hero-headline" id="heroHeadline">Jobs that fit you.</h1>
      <p class="hero-subheadline" id="heroSubheadline">Verified government circulars evaluated against your personal profile.</p>
      <div class="hero-summary-bar" id="heroSummaryBar">
        <span id="heroStatEligible">-- eligible opportunities</span>
        <span class="summary-dot"></span>
        <span id="heroStatReview">-- need review</span>
        <span class="summary-dot"></span>
        <span id="heroStatFree">-- free to apply</span>
      </div>
    </div>

    <!-- SEARCH & SEGMENTED FILTER CONTROLS -->
    <div class="controls-wrapper">
      <div class="search-container">
        <svg class="search-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input 
          type="text" 
          id="searchInput" 
          class="search-field" 
          placeholder="Search jobs, exams, organizations..."
          oninput="applyFilters()"
        />
      </div>

      <div class="filters-bar" id="filtersBar">
        <!-- ROW 1: STATUS SEGMENTS & SORTING -->
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; gap: 10px;">
          <!-- SEGMENTED CONTROLS -->
          <div class="segmented-control" id="statusSegments">
            <button class="segment-btn active" data-status="ELIGIBLE" onclick="setStatusSegment('ELIGIBLE')">
              For you <span class="count-chip" id="countEligibleChip">0</span>
            </button>
            <button class="segment-btn" data-status="UNCERTAIN" onclick="setStatusSegment('UNCERTAIN')">
              Needs review <span class="count-chip" id="countReviewChip">0</span>
            </button>
            <button class="segment-btn" data-status="ALL" onclick="setStatusSegment('ALL')">
              All
            </button>
          </div>

          <!-- SORT DROPDOWN -->
          <div style="display: flex; align-items: center; gap: 8px;">
            <label for="sortBySelect" style="font-size: 12px; color: var(--text-tertiary); font-weight: 500;">Sort:</label>
            <select id="sortBySelect" class="filter-select-pill" onchange="applyFilters()">
              <option value="newest">Newest first</option>
              <option value="deadline">Deadline: Ending soon</option>
              <option value="vacancies">Vacancies: High to low</option>
            </select>
          </div>
        </div>

        <!-- ROW 2: SECONDARY FILTERS & CHIPS -->
        <div class="filter-row-secondary" id="secondaryFilters">
          <!-- EDUCATION LEVEL FILTER -->
          <select id="educationFilter" class="filter-select-pill" onchange="applyFilters()" title="Filter by required qualification">
            <option value="all">All Qualifications</option>
            <option value="engineering">Engineering (B.Tech / B.E. / MCA)</option>
            <option value="graduate">Graduate (Degree / B.Sc / B.Com)</option>
            <option value="diploma">Diploma / ITI</option>
            <option value="postgraduate">Post Graduate / Master's</option>
            <option value="school">10th / 12th Pass</option>
          </select>

          <!-- SECONDARY FILTER CHIPS -->
          <button class="filter-chip" id="feeFilterChip" onclick="toggleFeeFilter()">
            Free to apply
          </button>
          <button class="filter-chip" id="fresherFilterChip" onclick="toggleFresherFilter()">
            Freshers
          </button>
          <button class="filter-chip" id="closingSoonChip" onclick="toggleClosingSoonFilter()">
            Closing soon
          </button>
          <button class="filter-chip" id="bulkHiringChip" onclick="toggleBulkHiringFilter()">
            Bulk hiring (50+)
          </button>

          <!-- QUICK RESET BUTTON -->
          <button class="btn-clear-filters" id="btnClearFilters" style="display: none;" onclick="resetAllFilters()">
            ✕ Clear filters
          </button>
        </div>
      </div>
    </div>

    <!-- LIST HEADER -->
    <div class="section-header">
      <div style="display: flex; align-items: center; gap: 12px;">
        <div class="section-title" id="sectionTitleHeading">For you</div>
        <button id="btnClearEligible" class="btn-clear-eligible" style="display: none;" onclick="confirmClearEligible()">
          Clear all eligible
        </button>
      </div>
      <div class="section-count" id="jobsCountSummary">0 opportunities</div>
    </div>

    <!-- JOB CARDS LIST -->
    <div id="jobsListContainer" class="jobs-list">
      <div class="empty-state">
        <div class="empty-title">Loading opportunities...</div>
        <div class="empty-subtitle">Retrieving verified government notifications for your profile.</div>
      </div>
    </div>
  </main>

  <!-- APPLE-STYLE SLIDE-OVER SHEET -->
  <div class="sheet-overlay" id="sheetOverlay" onclick="handleOverlayClick(event)">
    <div class="sheet-panel">
      <div class="sheet-header">
        <div style="font-size: 13px; font-weight: 500; color: var(--text-secondary);">Job Details</div>
        <button class="sheet-close-btn" onclick="closeSheet()">&times;</button>
      </div>
      <div class="sheet-body" id="sheetBodyContent">
        <!-- Dynamic content injected here -->
      </div>
    </div>
  </div>

  <!-- SUBTLE TOAST PILL -->
  <div class="toast-pill" id="toastPill"></div>

  <!-- APPLE-STYLE CONFIRMATION MODAL -->
  <div class="confirm-modal-overlay" id="confirmModalOverlay" onclick="handleConfirmBackdrop(event)">
    <div class="confirm-modal-card">
      <div class="confirm-modal-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
      </div>
      <h3 class="confirm-modal-title" id="confirmModalTitle">Delete Opportunity?</h3>
      <p class="confirm-modal-desc" id="confirmModalDesc">Are you sure you want to delete this opportunity? This action cannot be undone.</p>
      <div class="confirm-modal-actions">
        <button class="btn-modal-cancel" onclick="closeConfirmModal()">Cancel</button>
        <button class="btn-modal-confirm-delete" id="confirmModalActionBtn">Delete</button>
      </div>
    </div>
  </div>

  <script>
    let allJobs = [];
    let currentView = 'jobs'; // 'jobs' | 'plan_to_apply' | 'applied'
    let currentSegment = 'ELIGIBLE';
    let isFreeOnly = false;
    let isFresherOnly = false;
    let isClosingSoon = false;
    let isBulkHiring = false;

    function trashIconSvg() {
      return `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>`;
    }

    function starIconSvg(filled) {
      if (filled) {
        return `<svg width="18" height="18" viewBox="0 0 24 24" fill="#FF9500" stroke="#FF9500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`;
      }
      return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`;
    }

    function checkCircleSvg(filled) {
      if (filled) {
        return `<svg width="18" height="18" viewBox="0 0 24 24" fill="#34C759" stroke="#34C759" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" fill="#34C759"></circle><polyline points="16 9 10 15 7 12" stroke="#FFFFFF" fill="none" stroke-width="2.2"></polyline></svg>`;
      }
      return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 9 10 15 7 12"></polyline></svg>`;
    }

    function detectView() {
      const p = window.location.pathname.toLowerCase();
      const h = window.location.hash.toLowerCase();
      if (p.includes('/plan-to-apply') || h === '#plan-to-apply' || h === '#saved') {
        return 'plan_to_apply';
      }
      if (p.includes('/applied') || h === '#applied') {
        return 'applied';
      }
      return 'jobs';
    }

    async function loadJobs() {
      try {
        const res = await fetch('/api/jobs?limit=100');
        if (!res.ok) throw new Error('Could not load jobs');
        allJobs = await res.json();
        currentView = detectView();
        syncViewUI();
      } catch (err) {
        console.error(err);
        document.getElementById('jobsListContainer').innerHTML = `
          <div class="empty-state">
            <div class="empty-title">Could not load opportunities</div>
            <div class="empty-subtitle">${escapeHtml(err.message)}</div>
            <button class="btn-reset-filters" onclick="loadJobs()">Retry</button>
          </div>
        `;
      }
    }

    function navigateToView(view, e) {
      if (e) e.preventDefault();
      currentView = view;
      const path = view === 'plan_to_apply' ? '/plan-to-apply' : (view === 'applied' ? '/applied' : '/jobs');
      if (window.location.pathname !== path) {
        history.pushState({ view }, '', path);
      }
      syncViewUI();
    }

    function syncViewUI() {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      const filtersBar = document.getElementById('filtersBar');
      const heroHeadline = document.getElementById('heroHeadline');
      const heroSubheadline = document.getElementById('heroSubheadline');
      const heroSummaryBar = document.getElementById('heroSummaryBar');

      if (currentView === 'plan_to_apply') {
        const tab = document.getElementById('navPlan');
        if (tab) tab.classList.add('active');
        if (filtersBar) filtersBar.style.display = 'none';
        if (heroHeadline) heroHeadline.textContent = 'Plan to Apply';
        if (heroSubheadline) heroSubheadline.textContent = "Opportunities you have starred with the intention to apply.";
        const plannedCount = allJobs.filter(j => j.user_status === 'plan_to_apply').length;
        if (heroSummaryBar) {
          heroSummaryBar.innerHTML = `<span>${plannedCount} planned ${plannedCount === 1 ? 'opportunity' : 'opportunities'}</span>`;
        }
      } else if (currentView === 'applied') {
        const tab = document.getElementById('navApplied');
        if (tab) tab.classList.add('active');
        if (filtersBar) filtersBar.style.display = 'none';
        if (heroHeadline) heroHeadline.textContent = 'Applied';
        if (heroSubheadline) heroSubheadline.textContent = 'Government opportunities you have marked as applied.';
        const appliedCount = allJobs.filter(j => j.user_status === 'applied').length;
        if (heroSummaryBar) {
          heroSummaryBar.innerHTML = `<span>${appliedCount} applied ${appliedCount === 1 ? 'opportunity' : 'opportunities'}</span>`;
        }
      } else {
        const tab = document.getElementById('navJobs');
        if (tab) tab.classList.add('active');
        if (filtersBar) filtersBar.style.display = 'flex';
        if (heroHeadline) heroHeadline.textContent = 'Jobs that fit you.';
        if (heroSubheadline) heroSubheadline.textContent = 'Verified government circulars evaluated against your personal profile.';
        updateTopMetrics();
      }

      applyFilters();
    }

    function updateTopMetrics() {
      const eligible = allJobs.filter(j => j.eligibility_status === 'ELIGIBLE').length;
      const review = allJobs.filter(j => j.eligibility_status === 'UNCERTAIN').length;
      const free = allJobs.filter(j => j.is_free).length;

      const heroSummaryBar = document.getElementById('heroSummaryBar');
      if (heroSummaryBar) {
        heroSummaryBar.innerHTML = `
          <span id="heroStatEligible">${eligible} eligible opportunities</span>
          <span class="summary-dot"></span>
          <span id="heroStatReview">${review} need review</span>
          <span class="summary-dot"></span>
          <span id="heroStatFree">${free} free to apply</span>
        `;
      }

      const elChip = document.getElementById('countEligibleChip');
      if (elChip) elChip.textContent = eligible;
      const revChip = document.getElementById('countReviewChip');
      if (revChip) revChip.textContent = review;
    }

    function setStatusSegment(status) {
      currentSegment = status;
      document.querySelectorAll('#statusSegments .segment-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-status') === status);
      });
      applyFilters();
    }

    function toggleFeeFilter() {
      isFreeOnly = !isFreeOnly;
      document.getElementById('feeFilterChip').classList.toggle('active', isFreeOnly);
      applyFilters();
    }

    function toggleFresherFilter() {
      isFresherOnly = !isFresherOnly;
      document.getElementById('fresherFilterChip').classList.toggle('active', isFresherOnly);
      applyFilters();
    }

    function toggleClosingSoonFilter() {
      isClosingSoon = !isClosingSoon;
      document.getElementById('closingSoonChip')?.classList.toggle('active', isClosingSoon);
      applyFilters();
    }

    function toggleBulkHiringFilter() {
      isBulkHiring = !isBulkHiring;
      document.getElementById('bulkHiringChip')?.classList.toggle('active', isBulkHiring);
      applyFilters();
    }

    async function togglePlanToApply(jobId, event) {
      if (event) event.stopPropagation();
      const job = allJobs.find(j => j.id === jobId);
      if (!job) return;

      const willBePlanned = (job.user_status !== 'plan_to_apply');
      const newStatus = willBePlanned ? 'plan_to_apply' : null;
      const oldStatus = job.user_status;
      const oldAppliedAt = job.applied_at;

      // Optimistic UI update
      job.user_status = newStatus;
      if (newStatus === null) {
        showToast('Removed from Plan to Apply');
      } else {
        showToast('Added to Plan to Apply');
      }

      if (currentView === 'plan_to_apply') {
        const plannedCount = allJobs.filter(j => j.user_status === 'plan_to_apply').length;
        const heroSummaryBar = document.getElementById('heroSummaryBar');
        if (heroSummaryBar) {
          heroSummaryBar.innerHTML = `<span>${plannedCount} planned ${plannedCount === 1 ? 'opportunity' : 'opportunities'}</span>`;
        }
      }

      applyFilters();

      try {
        const res = await fetch(`/api/jobs/${jobId}/user-status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error('Failed to update status');
      } catch (err) {
        console.error(err);
        job.user_status = oldStatus;
        job.applied_at = oldAppliedAt;
        showToast('Error saving: ' + err.message);
        applyFilters();
      }
    }

    async function toggleApplied(jobId, event) {
      if (event) event.stopPropagation();
      const job = allJobs.find(j => j.id === jobId);
      if (!job) return;

      const willBeApplied = (job.user_status !== 'applied');
      const newStatus = willBeApplied ? 'applied' : null;
      const oldStatus = job.user_status;
      const oldAppliedAt = job.applied_at;

      // Optimistic UI update: Marking as Applied automatically removes from Plan to Apply
      job.user_status = newStatus;
      job.applied_at = willBeApplied ? new Date().toISOString() : null;

      if (willBeApplied) {
        showToast('Marked as Applied');
      } else {
        showToast('Marked as Not Applied');
      }

      if (currentView === 'applied') {
        const appliedCount = allJobs.filter(j => j.user_status === 'applied').length;
        const heroSummaryBar = document.getElementById('heroSummaryBar');
        if (heroSummaryBar) {
          heroSummaryBar.innerHTML = `<span>${appliedCount} applied ${appliedCount === 1 ? 'opportunity' : 'opportunities'}</span>`;
        }
      }

      applyFilters();

      try {
        const res = await fetch(`/api/jobs/${jobId}/user-status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error('Failed to update status');
        const data = await res.json();
        if (data.applied_at) {
          job.applied_at = data.applied_at;
        }
        applyFilters();
      } catch (err) {
        console.error(err);
        job.user_status = oldStatus;
        job.applied_at = oldAppliedAt;
        showToast('Error saving: ' + err.message);
        applyFilters();
      }
    }

    function applyFilters() {
      const query = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();
      const eduVal = document.getElementById('educationFilter')?.value || 'all';
      const sortVal = document.getElementById('sortBySelect')?.value || 'newest';

      const eduSelect = document.getElementById('educationFilter');
      if (eduSelect) eduSelect.classList.toggle('active', eduVal !== 'all');

      // Heading title
      if (currentView === 'plan_to_apply') {
        document.getElementById('sectionTitleHeading').textContent = 'Plan to Apply';
      } else if (currentView === 'applied') {
        document.getElementById('sectionTitleHeading').textContent = 'Applied';
      } else if (currentSegment === 'ELIGIBLE') {
        document.getElementById('sectionTitleHeading').textContent = 'For you';
      } else if (currentSegment === 'UNCERTAIN') {
        document.getElementById('sectionTitleHeading').textContent = 'Needs review';
      } else {
        document.getElementById('sectionTitleHeading').textContent = 'All Opportunities';
      }

      let filtered = allJobs.filter(job => {
        // Tab / view filtering
        if (currentView === 'plan_to_apply') {
          if (job.user_status !== 'plan_to_apply') return false;
        } else if (currentView === 'applied') {
          if (job.user_status !== 'applied') return false;
        } else {
          // Regular jobs view
          if (currentSegment !== 'ALL' && job.eligibility_status !== currentSegment) {
            return false;
          }
          if (isFreeOnly && !job.is_free) {
            return false;
          }
          if (isFresherOnly) {
            const sd = job.structured_data || {};
            const isFresher = sd.experience_required === false || sd.experience_years_min === 0;
            if (!isFresher) return false;
          }
          if (isClosingSoon) {
            const dl = job.structured_data?.application_deadline;
            if (!dl) return false;
            try {
              const d = new Date(dl);
              const now = new Date();
              const diffDays = Math.ceil((d - now) / (1000 * 60 * 60 * 24));
              if (diffDays < 0 || diffDays > 14) return false;
            } catch {
              return false;
            }
          }
          if (isBulkHiring) {
            const vac = job.structured_data?.vacancies;
            if (!vac) return false;
            const match = String(vac).match(/\d+/);
            if (!match || parseInt(match[0], 10) < 50) return false;
          }
          if (eduVal !== 'all') {
            const quals = (job.structured_data?.qualification || []).map(q => q.toLowerCase());
            const text = quals.join(' ');
            if (eduVal === 'engineering') {
              const ok = ['b.tech', 'b.e', 'btech', 'engineering degree', 'degree in engineering', 'bca', 'mca', 'cse', 'civil', 'mechanical'].some(k => text.includes(k));
              if (!ok) return false;
            } else if (eduVal === 'diploma') {
              const ok = ['diploma', 'polytechnic', 'iti', 'gnm', 'trade certificate', 'apprenticeship'].some(k => text.includes(k));
              if (!ok) return false;
            } else if (eduVal === 'graduate') {
              const ok = ['graduate', 'bachelor', 'degree', 'b.sc', 'b.com', 'bba', 'b.a', 'graduation'].some(k => text.includes(k));
              if (!ok) return false;
            } else if (eduVal === 'postgraduate') {
              const ok = ['master', 'm.sc', 'm.com', 'm.tech', 'mba', 'm.d', 'phd', 'post-graduate', 'postgraduate', 'pg degree'].some(k => text.includes(k));
              if (!ok) return false;
            } else if (eduVal === 'school') {
              const ok = ['10th', '12th', 'matric', '10+2', 'intermediate', '8th', '5th'].some(k => text.includes(k));
              if (!ok) return false;
            }
          }
        }

        // Query search
        if (query) {
          const org = (job.organization || '').toLowerCase();
          const post = (job.post_name || '').toLowerCase();
          const desc = (job.short_description || '').toLowerCase();
          const quals = (job.structured_data?.qualification || []).join(' ').toLowerCase();
          const branches = (job.structured_data?.accepted_branches || []).join(' ').toLowerCase();
          if (!org.includes(query) && !post.includes(query) && !desc.includes(query) && !quals.includes(query) && !branches.includes(query)) {
            return false;
          }
        }

        return true;
      });

      // Sorting
      if (sortVal === 'deadline') {
        filtered.sort((a, b) => {
          const da = a.structured_data?.application_deadline ? new Date(a.structured_data.application_deadline).getTime() : Infinity;
          const db = b.structured_data?.application_deadline ? new Date(b.structured_data.application_deadline).getTime() : Infinity;
          return da - db;
        });
      } else if (sortVal === 'vacancies') {
        filtered.sort((a, b) => {
          const va = parseInt((String(a.structured_data?.vacancies || '').match(/\d+/) || [0])[0], 10);
          const vb = parseInt((String(b.structured_data?.vacancies || '').match(/\d+/) || [0])[0], 10);
          return vb - va;
        });
      } else {
        filtered.sort((a, b) => {
          const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
          const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
          return tb - ta;
        });
      }

      // Show or hide clear button
      const hasActive = isFreeOnly || isFresherOnly || isClosingSoon || isBulkHiring || (eduVal !== 'all') || query || (currentSegment !== 'ELIGIBLE');
      const clearBtn = document.getElementById('btnClearFilters');
      if (clearBtn) {
        clearBtn.style.display = hasActive ? 'inline-flex' : 'none';
      }

      // Show or hide "Clear all eligible" button
      const clearEligibleBtn = document.getElementById('btnClearEligible');
      if (clearEligibleBtn) {
        const eligibleCount = allJobs.filter(j => j.eligibility_status === 'ELIGIBLE').length;
        const showClearEligible = (currentView === 'jobs' && currentSegment === 'ELIGIBLE' && eligibleCount > 0);
        clearEligibleBtn.style.display = showClearEligible ? 'inline-flex' : 'none';
      }

      renderJobList(filtered);
    }

    function renderJobList(jobs) {
      const container = document.getElementById('jobsListContainer');
      document.getElementById('jobsCountSummary').textContent = `${jobs.length} ${jobs.length === 1 ? 'opportunity' : 'opportunities'}`;

      if (!jobs || jobs.length === 0) {
        let emptyTitle = 'No matching opportunities';
        let emptySubtitle = 'Try adjusting your filters or search terms.';
        let actionHtml = `<button class="btn-reset-filters" onclick="resetAllFilters()">Reset filters</button>`;

        if (currentView === 'plan_to_apply') {
          emptyTitle = 'No jobs planned yet';
          emptySubtitle = "Star jobs you want to apply for and they'll appear here.";
          actionHtml = `<button class="btn-reset-filters" onclick="navigateToView('jobs')">Explore opportunities →</button>`;
        } else if (currentView === 'applied') {
          emptyTitle = 'No applied jobs yet';
          emptySubtitle = "Jobs you've marked as applied will appear here.";
          actionHtml = `<button class="btn-reset-filters" onclick="navigateToView('jobs')">Explore opportunities →</button>`;
        }

        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-title">${emptyTitle}</div>
            <div class="empty-subtitle">${emptySubtitle}</div>
            ${actionHtml}
          </div>
        `;
        return;
      }

      container.innerHTML = jobs.map(job => {
        const sd = job.structured_data || {};
        const org = escapeHtml(job.organization || 'Government Department');
        const post = escapeHtml(job.post_name || 'Recruitment Post');
        const isPlanToApply = (job.user_status === 'plan_to_apply');
        const isApplied = (job.user_status === 'applied');

        // Status badge
        let statusBadgeHtml = '';
        if (job.eligibility_status === 'ELIGIBLE') {
          statusBadgeHtml = `<span class="status-badge status-eligible"><span class="status-dot"></span> Eligible</span>`;
        } else if (job.eligibility_status === 'UNCERTAIN') {
          statusBadgeHtml = `<span class="status-badge status-uncertain"><span class="status-dot"></span> Review needed</span>`;
        } else {
          statusBadgeHtml = `<span class="status-badge status-ineligible"><span class="status-dot"></span> Ineligible</span>`;
        }

        // Applied date badge
        let appliedDateBadgeHtml = '';
        if (isApplied && job.applied_at) {
          appliedDateBadgeHtml = `<span class="applied-date-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Applied ${formatDate(job.applied_at)}</span>`;
        } else if (isApplied) {
          appliedDateBadgeHtml = `<span class="applied-date-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Applied</span>`;
        }

        // Key attributes line (e.g. Graduate · Civil · 232 Vacancies)
        const attributes = [];
        if (sd.qualification && sd.qualification.length > 0) {
          attributes.push(escapeHtml(sd.qualification[0]));
        }
        if (sd.accepted_branches && sd.accepted_branches.length > 0) {
          attributes.push(escapeHtml(sd.accepted_branches[0]));
        }
        if (sd.vacancies) {
          attributes.push(`${sd.vacancies} vacancies`);
        }
        if (sd.location && sd.location.length > 0) {
          attributes.push(escapeHtml(sd.location[0]));
        }
        const attrsLine = attributes.join(' <span class="attribute-separator">·</span> ');

        // Short Description
        const descText = escapeHtml(job.short_description || `${org} is recruiting for ${post}. Review circular for full eligibility terms.`);

        // Deadline text
        const deadlineText = sd.application_deadline ? `Closes ${formatDate(sd.application_deadline)}` : 'Deadline not specified';

        // Fee text
        let feeBadge = '';
        if (job.is_free) {
          feeBadge = `<span class="fee-pill fee-free">No application fee</span>`;
        } else if (sd.application_fee && sd.application_fee.length > 0) {
          feeBadge = `<span class="fee-pill">Fee required</span>`;
        }

        const applyUrl = job.effective_apply_url;

        return `
          <div class="job-card" onclick="openJobSheet('${job.id}')">
            <div class="card-meta-top">
              <div class="card-org-name">${org}</div>
              <div style="display: flex; align-items: center; gap: 8px;">
                ${statusBadgeHtml}
                ${appliedDateBadgeHtml}
              </div>
            </div>

            <div class="card-title-row">
              <h2 class="card-post-title">${post}</h2>
              ${attrsLine ? `<div class="card-key-attributes">${attrsLine}</div>` : ''}
            </div>

            <div class="card-description-text">
              ${descText}
            </div>

            <div class="card-footer">
              <div class="footer-metadata">
                <span>${deadlineText}</span>
                ${feeBadge}
              </div>

              <div class="footer-actions">
                <button 
                  class="btn-icon-action btn-star ${isPlanToApply ? 'active' : ''}" 
                  onclick="togglePlanToApply('${job.id}', event)" 
                  title="${isPlanToApply ? 'Remove from Plan to Apply' : 'Plan to Apply'}"
                  aria-label="${isPlanToApply ? 'Remove from Plan to Apply' : 'Plan to Apply'}"
                >
                  ${starIconSvg(isPlanToApply)}
                </button>

                <button 
                  class="btn-icon-action btn-applied ${isApplied ? 'active' : ''}" 
                  onclick="toggleApplied('${job.id}', event)" 
                  title="${isApplied ? 'Mark as Not Applied' : 'Mark as Applied'}"
                  aria-label="${isApplied ? 'Mark as Not Applied' : 'Mark as Applied'}"
                >
                  ${checkCircleSvg(isApplied)}
                </button>

                <button 
                  class="btn-icon-action btn-delete" 
                  onclick="confirmDeleteJob('${job.id}', event)" 
                  title="Delete opportunity"
                  aria-label="Delete opportunity"
                >
                  ${trashIconSvg()}
                </button>

                <button class="btn-details" onclick="openJobSheet('${job.id}'); event.stopPropagation();">
                  Details →
                </button>
                ${applyUrl ? `
                  <a href="${escapeHtml(applyUrl)}" target="_blank" rel="noopener noreferrer" class="btn-apply-primary" onclick="event.stopPropagation();">
                    Apply on website ↗
                  </a>
                ` : ''}
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function openJobSheet(jobId) {
      const job = allJobs.find(j => j.id === jobId);
      if (!job) return;

      const sd = job.structured_data || {};
      const expl = job.eligibility_explanation || {};
      const org = escapeHtml(job.organization || 'Government Organization');
      const post = escapeHtml(job.post_name || 'Recruitment Post');
      const applyUrl = job.effective_apply_url;
      const pdfUrl = job.effective_notification_url;
      const isPlanToApply = (job.user_status === 'plan_to_apply');
      const isApplied = (job.user_status === 'applied');

      // Status indicator
      let statusLabel = 'Eligible';
      if (job.eligibility_status === 'UNCERTAIN') statusLabel = 'Review Needed';
      if (job.eligibility_status === 'NOT_ELIGIBLE') statusLabel = 'Ineligible';

      // Checklist items
      let criteriaHtml = '';
      if (expl.criteria) {
        const rows = [];
        for (const [k, v] of Object.entries(expl.criteria)) {
          const isPass = v.status === 'PASS';
          const icon = isPass ? '✓' : (v.status === 'UNKNOWN' ? '?' : '✕');
          const cls = isPass ? 'criteria-pass' : 'criteria-warn';
          const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
          rows.push(`
            <div class="criteria-row">
              <div class="criteria-indicator ${cls}">${icon}</div>
              <div>
                <div style="font-weight: 500; color: var(--text-primary); font-size: 13px;">${escapeHtml(label)}</div>
                <div style="color: var(--text-secondary); font-size: 12px; margin-top: 1px;">${escapeHtml(String(v.details || 'Matched requirements'))}</div>
              </div>
            </div>
          `);
        }
        criteriaHtml = `
          <div class="sheet-section">
            <div class="sheet-section-heading">Eligibility Evaluation</div>
            <div class="criteria-checklist">${rows.join('')}</div>
          </div>
        `;
      }

      // Qualifications & Branches
      const quals = (sd.qualification || []).map(q => `<span class="spec-tag">${escapeHtml(q)}</span>`).join('');
      const branches = (sd.accepted_branches || []).map(b => `<span class="spec-tag">${escapeHtml(b)}</span>`).join('');

      // Fees
      const feeDetails = (sd.application_fee && sd.application_fee.length > 0)
        ? sd.application_fee.map(f => `<li style="margin-bottom: 4px;">${escapeHtml(f)}</li>`).join('')
        : '<li>No application fee or fee details unstated.</li>';

      // Selection Process
      const stages = (sd.selection_process && sd.selection_process.length > 0)
        ? sd.selection_process.map(s => `<li style="margin-bottom: 4px;">${escapeHtml(s)}</li>`).join('')
        : '<li>Standard written examination / interview.</li>';

      document.getElementById('sheetBodyContent').innerHTML = `
        <div class="sheet-hero-section">
          <div class="sheet-org">${org}</div>
          <h1 class="sheet-title">${post}</h1>
          <div style="font-size: 13px; color: var(--text-secondary);">
            ${sd.notification_number ? `Circular: ${escapeHtml(sd.notification_number)}` : ''}
          </div>

          <div class="sheet-status-actions">
            <button 
              class="btn-sheet-toggle ${isPlanToApply ? 'star-active' : ''}" 
              onclick="togglePlanToApply('${job.id}', event); openJobSheet('${job.id}');"
              title="${isPlanToApply ? 'Remove from Plan to Apply' : 'Plan to Apply'}"
            >
              ${starIconSvg(isPlanToApply)}
              <span>${isPlanToApply ? 'Planned to Apply' : 'Plan to Apply'}</span>
            </button>
            <button 
              class="btn-sheet-toggle ${isApplied ? 'applied-active' : ''}" 
              onclick="toggleApplied('${job.id}', event); openJobSheet('${job.id}');"
              title="${isApplied ? 'Mark as Not Applied' : 'Mark as Applied'}"
            >
              ${checkCircleSvg(isApplied)}
              <span>${isApplied ? 'Applied' : 'Mark as Applied'}</span>
            </button>
            <button 
              class="btn-sheet-toggle btn-sheet-delete" 
              onclick="confirmDeleteJob('${job.id}', event)"
              title="Delete opportunity"
            >
              ${trashIconSvg()}
              <span>Delete</span>
            </button>
          </div>

          <div class="sheet-cta-bar">
            ${applyUrl ? `
              <a href="${escapeHtml(applyUrl)}" target="_blank" rel="noopener noreferrer" class="btn-sheet-apply">
                Apply on Official Website ↗
              </a>
            ` : ''}
            ${pdfUrl ? `
              <a href="${escapeHtml(pdfUrl)}" target="_blank" rel="noopener noreferrer" class="btn-sheet-pdf">
                Download Official Notification PDF
              </a>
            ` : ''}
          </div>
        </div>

        <div class="sheet-section">
          <div class="sheet-section-heading">Key Specifications</div>
          <div class="sheet-specs-grid">
            <div class="spec-item">
              <span class="spec-label">Vacancies</span>
              <span class="spec-val">${sd.vacancies || 'Not declared'}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">Experience</span>
              <span class="spec-val">${sd.experience_required === false || sd.experience_years_min === 0 ? 'Freshers eligible' : (sd.experience_years_min ? `${sd.experience_years_min}+ years` : 'Refer circular')}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">Age Limit</span>
              <span class="spec-val">${sd.age_max ? `Up to ${sd.age_max} years` : 'Standard terms'}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">Salary Scale</span>
              <span class="spec-val">${escapeHtml(sd.salary || sd.pay_level || 'Govt rules')}</span>
            </div>
          </div>
        </div>

        <div class="sheet-section">
          <div class="sheet-section-heading">Overview</div>
          <p style="font-size: 14px; line-height: 1.6; color: #3A3A3C;">
            ${escapeHtml(job.short_description || '')}
          </p>
        </div>

        ${criteriaHtml}

        <div class="sheet-section">
          <div class="sheet-section-heading">Education & Discipline</div>
          ${quals ? `<div style="margin-bottom: 6px;"><span style="font-size: 12px; color: var(--text-secondary);">Degrees:</span> <div class="tag-cloud" style="margin-top: 4px;">${quals}</div></div>` : ''}
          ${branches ? `<div><span style="font-size: 12px; color: var(--text-secondary);">Branches:</span> <div class="tag-cloud" style="margin-top: 4px;">${branches}</div></div>` : ''}
        </div>

        <div class="sheet-section">
          <div class="sheet-section-heading">Application Fee</div>
          <ul style="padding-left: 18px; font-size: 13.5px; color: var(--text-primary); line-height: 1.5;">
            ${feeDetails}
          </ul>
        </div>

        <div class="sheet-section">
          <div class="sheet-section-heading">Selection Process</div>
          <ul style="padding-left: 18px; font-size: 13.5px; color: var(--text-primary); line-height: 1.5;">
            ${stages}
          </ul>
        </div>

        <div class="collapsible-debug">
          <details>
            <summary>Technical details & AI payload</summary>
            <div class="json-inspector">${escapeHtml(JSON.stringify(sd, null, 2))}</div>
          </details>
        </div>
      `;

      const overlay = document.getElementById('sheetOverlay');
      overlay.style.display = 'flex';
      setTimeout(() => overlay.classList.add('open'), 10);
    }

    function closeSheet() {
      const overlay = document.getElementById('sheetOverlay');
      overlay.classList.remove('open');
      setTimeout(() => overlay.style.display = 'none', 250);
    }

    function handleOverlayClick(e) {
      if (e.target.id === 'sheetOverlay') {
        closeSheet();
      }
    }

    function resetAllFilters() {
      const searchInp = document.getElementById('searchInput');
      if (searchInp) searchInp.value = '';
      setStatusSegment('ELIGIBLE');
      isFreeOnly = false;
      isFresherOnly = false;
      isClosingSoon = false;
      isBulkHiring = false;
      document.getElementById('feeFilterChip')?.classList.remove('active');
      document.getElementById('fresherFilterChip')?.classList.remove('active');
      document.getElementById('closingSoonChip')?.classList.remove('active');
      document.getElementById('bulkHiringChip')?.classList.remove('active');
      const eduSelect = document.getElementById('educationFilter');
      if (eduSelect) {
        eduSelect.value = 'all';
        eduSelect.classList.remove('active');
      }
      const sortSelect = document.getElementById('sortBySelect');
      if (sortSelect) sortSelect.value = 'newest';
      applyFilters();
    }

    function formatDate(dateStr) {
      try {
        const d = new Date(dateStr);
        if (isNaN(d)) return dateStr;
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      } catch {
        return dateStr;
      }
    }

    function showToast(msg) {
      const toast = document.getElementById('toastPill');
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
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

    let pendingDeleteJobId = null;

    function confirmDeleteJob(jobId, event) {
      if (event) event.stopPropagation();
      const job = allJobs.find(j => j.id === jobId);
      const postName = job ? (job.post_name || 'this opportunity') : 'this opportunity';
      
      pendingDeleteJobId = jobId;

      document.getElementById('confirmModalTitle').textContent = 'Delete Opportunity?';
      document.getElementById('confirmModalDesc').textContent = `Are you sure you want to delete "${escapeHtml(postName)}"? This opportunity will be permanently removed.`;
      
      const actionBtn = document.getElementById('confirmModalActionBtn');
      actionBtn.textContent = 'Delete';
      actionBtn.onclick = executeDeleteJob;

      const overlay = document.getElementById('confirmModalOverlay');
      overlay.style.display = 'flex';
      setTimeout(() => overlay.classList.add('open'), 10);
    }

    function confirmClearEligible() {
      const eligibleCount = allJobs.filter(j => j.eligibility_status === 'ELIGIBLE').length;
      if (eligibleCount === 0) return;

      pendingDeleteJobId = null;

      document.getElementById('confirmModalTitle').textContent = 'Clear All Eligible Opportunities?';
      document.getElementById('confirmModalDesc').textContent = `Are you sure you want to permanently delete all ${eligibleCount} eligible opportunities? This action cannot be undone.`;

      const actionBtn = document.getElementById('confirmModalActionBtn');
      actionBtn.textContent = `Delete ${eligibleCount} Jobs`;
      actionBtn.onclick = executeClearEligible;

      const overlay = document.getElementById('confirmModalOverlay');
      overlay.style.display = 'flex';
      setTimeout(() => overlay.classList.add('open'), 10);
    }

    function closeConfirmModal() {
      const overlay = document.getElementById('confirmModalOverlay');
      overlay.classList.remove('open');
      setTimeout(() => {
        overlay.style.display = 'none';
        pendingDeleteJobId = null;
      }, 200);
    }

    function handleConfirmBackdrop(e) {
      if (e.target.id === 'confirmModalOverlay') {
        closeConfirmModal();
      }
    }

    async function executeDeleteJob() {
      const jobId = pendingDeleteJobId;
      if (!jobId) return;

      closeConfirmModal();
      closeSheet();

      const idx = allJobs.findIndex(j => j.id === jobId);
      if (idx === -1) return;
      const removedJob = allJobs[idx];

      // Optimistic UI update
      allJobs.splice(idx, 1);
      updateTopMetrics();
      applyFilters();
      showToast('Opportunity deleted');

      try {
        const res = await fetch(`/api/jobs/${jobId}`, {
          method: 'DELETE'
        });
        if (!res.ok) {
          throw new Error('Server returned ' + res.status);
        }
      } catch (err) {
        console.error(err);
        // Rollback
        allJobs.splice(idx, 0, removedJob);
        updateTopMetrics();
        applyFilters();
        showToast('Failed to delete opportunity: ' + err.message);
      }
    }

    async function executeClearEligible() {
      closeConfirmModal();
      closeSheet();

      const backupJobs = [...allJobs];
      const eligibleCount = allJobs.filter(j => j.eligibility_status === 'ELIGIBLE').length;

      // Optimistic UI update
      allJobs = allJobs.filter(j => j.eligibility_status !== 'ELIGIBLE');
      updateTopMetrics();
      applyFilters();
      showToast(`Deleted ${eligibleCount} eligible opportunities`);

      try {
        const res = await fetch('/api/jobs?status=ELIGIBLE', {
          method: 'DELETE'
        });
        if (!res.ok) {
          throw new Error('Server returned ' + res.status);
        }
      } catch (err) {
        console.error(err);
        allJobs = backupJobs;
        updateTopMetrics();
        applyFilters();
        showToast('Failed to clear eligible opportunities: ' + err.message);
      }
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const modal = document.getElementById('confirmModalOverlay');
        if (modal && modal.classList.contains('open')) {
          closeConfirmModal();
        } else {
          closeSheet();
        }
      }
    });

    window.addEventListener('popstate', () => {
      currentView = detectView();
      syncViewUI();
    });
    window.addEventListener('hashchange', () => {
      currentView = detectView();
      syncViewUI();
    });
    document.addEventListener('DOMContentLoaded', loadJobs);
  </script>
</body>
</html>
"""
