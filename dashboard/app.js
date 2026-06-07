// TeX Dashboard - Compiled Vanilla JavaScript Bundle (from TypeScript)
// Version: 1.0
// No external dependencies - runs directly in browser

class RuleEngine {
  constructor(summary) {
    this.checks = summary.all_checks || [];
    this.originalChecks = [...this.checks];
  }

  filterBySeverity(severity) {
    this.checks = this.checks.filter(c => c.severity === severity);
    return this;
  }

  filterByStatus(status) {
    this.checks = this.checks.filter(c => c.status === status);
    return this;
  }

  filterByModule(module) {
    this.checks = this.checks.filter(c => c.module === module);
    return this;
  }

  searchByTitle(keyword) {
    const q = keyword.toLowerCase();
    this.checks = this.checks.filter(
      c => c.title.toLowerCase().includes(q) || c.cis_id.toLowerCase().includes(q)
    );
    return this;
  }

  limit(n) {
    this.checks = this.checks.slice(0, n);
    return this;
  }

  sortBySeverity() {
    const severityOrder = { CRITICAL: 1, HIGH: 2, MEDIUM: 3, LOW: 4, PASS: 5 };
    this.checks.sort(
      (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
    );
    return this;
  }

  getResults() {
    return this.checks;
  }

  reset() {
    this.checks = [...this.originalChecks];
    return this;
  }

  count() {
    return this.checks.length;
  }

  countBySeverity() {
    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, PASS: 0 };
    this.originalChecks.forEach(check => {
      counts[check.severity]++;
    });
    return counts;
  }

  getModules() {
    return Array.from(new Set(this.originalChecks.map(c => c.module)));
  }

  getModuleFindings(module) {
    return this.originalChecks.filter(c => c.module === module);
  }

  getTopCritical(n = 10) {
    return this.originalChecks.filter(c => c.severity === 'CRITICAL').slice(0, n);
  }

  exportAsCSV() {
    const headers = [
      'CIS ID', 'Module', 'Title', 'Status', 'Severity',
      'Actual Value', 'Expected Value', 'Remediation',
    ];
    const rows = this.checks.map(check => [
      check.cis_id, check.module, check.title, check.status, check.severity,
      `"${check.actual_value}"`, `"${check.expected_value}"`, `"${check.remediation}"`,
    ]);
    return [headers, ...rows].map(row => row.join(',')).join('\n') + '\n';
  }
}

class SVGRenderer {
  static generateRadarChart(categoryScores, width = 400, height = 400) {
    const config = {
      centerX: width / 2,
      centerY: height / 2,
      radius: Math.min(width, height) / 2.5,
      axisCount: 6,
    };

    const axes = Object.keys(categoryScores).slice(0, 6);
    const scores = axes.map(axis => categoryScores[axis] || 0);

    const axisLines = axes.map((axis, i) => {
      const angle = (Math.PI * 2 * i) / config.axisCount - Math.PI / 2;
      const x2 = config.centerX + config.radius * Math.cos(angle);
      const y2 = config.centerY + config.radius * Math.sin(angle);
      const labelX = config.centerX + (config.radius + 30) * Math.cos(angle);
      const labelY = config.centerY + (config.radius + 30) * Math.sin(angle);

      return {
        line: `<line x1="${config.centerX}" y1="${config.centerY}" x2="${x2}" y2="${y2}" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>`,
        label: `<text x="${labelX}" y="${labelY}" text-anchor="middle" dominant-baseline="middle" font-size="12" fill="rgba(255,255,255,0.7)">${axis.toUpperCase()}</text>`,
      };
    }).reduce((acc, item) => {
      acc.lines.push(item.line);
      acc.labels.push(item.label);
      return acc;
    }, { lines: [], labels: [] });

    const gridCircles = [25, 50, 75, 100]
      .map(
        percent =>
          `<circle cx="${config.centerX}" cy="${config.centerY}" r="${
            (config.radius * percent) / 100
          }" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>`
      )
      .join('');

    const polygonPoints = scores
      .map((score, i) => {
        const angle = (Math.PI * 2 * i) / config.axisCount - Math.PI / 2;
        const distance = (config.radius * score) / 100;
        const x = config.centerX + distance * Math.cos(angle);
        const y = config.centerY + distance * Math.sin(angle);
        return `${x},${y}`;
      })
      .join(' ');

    const scorePolygon = `<polygon points="${polygonPoints}" fill="rgba(99, 102, 241, 0.35)" stroke="#6366f1" stroke-width="2"/>`;

    const svg = `<svg viewBox="0 0 ${width} ${height}" class="radar-chart" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>.radar-chart { background-color: rgba(0, 0, 0, 0.5); }</style>
      </defs>
      ${gridCircles}
      ${axisLines.lines.join('')}
      ${scorePolygon}
      ${axisLines.labels.join('')}
    </svg>`;

    return svg;
  }

  static generateProgressRing(score, radius = 60, strokeWidth = 6) {
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    let color = '#10b981';
    if (score < 80) color = '#f59e0b';
    if (score < 60) color = '#ef4444';

    const svg = `<svg width="${(radius + strokeWidth) * 2}" height="${(radius + strokeWidth) * 2}" class="progress-ring">
      <circle cx="${radius + strokeWidth}" cy="${radius + strokeWidth}" r="${radius}" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="${strokeWidth}"/>
      <circle cx="${radius + strokeWidth}" cy="${radius + strokeWidth}" r="${radius}" fill="none" stroke="${color}" stroke-width="${strokeWidth}" 
              stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" stroke-linecap="round"
              style="transform: rotate(-90deg); transform-origin: ${radius + strokeWidth}px ${radius + strokeWidth}px; transition: stroke-dashoffset 0.35s;"/>
      <text x="${radius + strokeWidth}" y="${radius + strokeWidth}" text-anchor="middle" dominant-baseline="middle" font-size="24" font-weight="bold" fill="${color}">${score.toFixed(1)}</text>
      <text x="${radius + strokeWidth}" y="${radius + strokeWidth + 20}" text-anchor="middle" dominant-baseline="middle" font-size="12" fill="rgba(255,255,255,0.7)">/100</text>
    </svg>`;

    return svg;
  }

  static getSeverityColor(severity) {
    const colorMap = {
      CRITICAL: '#ef4444',
      HIGH: '#f97316',
      MEDIUM: '#eab308',
      LOW: '#6b7280',
      PASS: '#10b981',
    };
    return colorMap[severity] || '#6b7280';
  }

  static generateSeverityBadge(severity) {
    const color = this.getSeverityColor(severity);
    return `<span style="display:inline-block; padding:2px 8px; border-radius:4px; background-color:${color}; color:white; font-size:12px; font-weight:bold;">${severity}</span>`;
  }

  static formatNumber(num) {
    return num.toLocaleString();
  }

  static formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  static formatTime(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }
}

class TexDashboard {
  constructor() {
    this.summary = null;
    this.engine = null;
  }

  async initialize(summaryUrl = 'data/audit_summary.json') {
    try {
      console.log('[TeX Dashboard] Initializing...');
      const response = await fetch(summaryUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch summary: ${response.statusText}`);
      }
      this.summary = await response.json();
      this.engine = new RuleEngine(this.summary);
      console.log('[TeX Dashboard] Loaded SPI:', this.summary.spi);

      this.renderHeader();
      this.renderSummary();
      this.renderRadarChart();
      this.renderCategoryScores();
      this.renderFindingsTable();
      this.renderMetadata();

      console.log('[TeX Dashboard] Initialization complete');
    } catch (error) {
      console.error('[TeX Dashboard] Initialization failed:', error);
      this.displayError(String(error));
    }
  }

  renderHeader() {
    if (!this.summary) return;
    const header = document.getElementById('header');
    if (!header) return;
    const metadata = this.summary.audit_metadata || {};
    const hostname = this.summary.hostname || metadata.hostname || 'Unknown';
    header.innerHTML = `
      <div class="header-content">
        <h1>TeX Security Audit</h1>
        <p class="hostname">${this.escapeHtml(hostname)}</p>
        <p class="timestamp">Generated: ${SVGRenderer.formatDate(this.summary.generated_at)}</p>
      </div>
    `;
  }

  renderSummary() {
    if (!this.summary) return;
    const summary = document.getElementById('summary');
    if (!summary) return;
    const counts = this.engine?.countBySeverity() || {};
    const spi = this.summary.spi;
    const spiColor = spi >= 80 ? '#10b981' : spi >= 60 ? '#f59e0b' : '#ef4444';
    summary.innerHTML = `
      <div class="summary-grid">
        <div class="spi-card">
          <div class="spi-value" style="color: ${spiColor};">${spi.toFixed(1)}</div>
          <div class="spi-label">Security Posture Index</div>
        </div>
        <div class="finding-card critical">
          <div class="count">${counts['CRITICAL'] || 0}</div>
          <div class="label">Critical</div>
        </div>
        <div class="finding-card high">
          <div class="count">${counts['HIGH'] || 0}</div>
          <div class="label">High</div>
        </div>
        <div class="finding-card medium">
          <div class="count">${counts['MEDIUM'] || 0}</div>
          <div class="label">Medium</div>
        </div>
        <div class="finding-card low">
          <div class="count">${counts['LOW'] || 0}</div>
          <div class="label">Low</div>
        </div>
        <div class="finding-card pass">
          <div class="count">${counts['PASS'] || 0}</div>
          <div class="label">Passed</div>
        </div>
      </div>
    `;
  }

  renderRadarChart() {
    if (!this.summary) return;
    const radarContainer = document.getElementById('radar-chart');
    if (!radarContainer) return;
    const radarSvg = SVGRenderer.generateRadarChart(this.summary.category_scores, 400, 400);
    radarContainer.innerHTML = `
      <div class="chart-container">
        <h2>Security Domain Scores</h2>
        ${radarSvg}
      </div>
    `;
  }

  renderCategoryScores() {
    if (!this.summary) return;
    const categoriesContainer = document.getElementById('categories');
    if (!categoriesContainer) return;
    const scores = this.summary.category_scores;
    const cards = Object.entries(scores)
      .map(
        ([category, score]) => `
        <div class="category-card">
          <div class="category-name">${category.toUpperCase()}</div>
          ${SVGRenderer.generateProgressRing(score, 40, 4)}
          <div class="category-details">
            <span class="finding-count">${this.engine?.getModuleFindings(category).length || 0} checks</span>
          </div>
        </div>
      `
      )
      .join('');
    categoriesContainer.innerHTML = `<div class="categories-grid">${cards}</div>`;
  }

  renderFindingsTable() {
    if (!this.summary || !this.engine) return;
    const tableContainer = document.getElementById('findings-table');
    if (!tableContainer) return;
    const failedFindings = this.engine.filterByStatus('FAIL').getResults();
    const rows = failedFindings
      .slice(0, 50)
      .map(
        finding => `
        <tr class="finding-row severity-${finding.severity.toLowerCase()}">
          <td class="cis-id">${this.escapeHtml(finding.cis_id)}</td>
          <td class="severity">${SVGRenderer.generateSeverityBadge(finding.severity)}</td>
          <td class="title">${this.escapeHtml(finding.title)}</td>
          <td class="remediation">${this.escapeHtml(finding.remediation.substring(0, 100))}</td>
        </tr>
      `
      )
      .join('');
    tableContainer.innerHTML = `
      <div class="table-container">
        <h2>Failed Controls</h2>
        <table class="findings-table">
          <thead>
            <tr>
              <th>CIS ID</th>
              <th>Severity</th>
              <th>Title</th>
              <th>Remediation</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  renderMetadata() {
    if (!this.summary) return;
    const metadata = this.summary.audit_metadata || {};
    const metadataContainer = document.getElementById('metadata');
    if (!metadataContainer) return;
    metadataContainer.innerHTML = `
      <div class="metadata-grid">
        <div class="metadata-item">
          <span class="label">Hostname:</span>
          <span class="value">${this.escapeHtml(metadata.hostname || 'Unknown')}</span>
        </div>
        <div class="metadata-item">
          <span class="label">OS:</span>
          <span class="value">${this.escapeHtml(metadata.os_name || 'Unknown')}</span>
        </div>
        <div class="metadata-item">
          <span class="label">Kernel:</span>
          <span class="value">${this.escapeHtml(metadata.kernel_version || 'Unknown')}</span>
        </div>
        <div class="metadata-item">
          <span class="label">TeX Version:</span>
          <span class="value">${this.escapeHtml(metadata.tex_version || '1.0')}</span>
        </div>
      </div>
    `;
  }

  displayError(message) {
    const container = document.getElementById('container');
    if (container) {
      container.innerHTML = `
        <div class="error-message">
          <h2>Error Loading Dashboard</h2>
          <p>${this.escapeHtml(message)}</p>
          <p>Ensure audit_summary.json is in the data/ directory.</p>
        </div>
      `;
    }
  }

  escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, char => map[char]);
  }
}

// Initialize dashboard on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new TexDashboard();
    dashboard.initialize();
  });
} else {
  const dashboard = new TexDashboard();
  dashboard.initialize();
}

// Export for browser console
window.TexDashboard = TexDashboard;
window.RuleEngine = RuleEngine;
window.SVGRenderer = SVGRenderer;
