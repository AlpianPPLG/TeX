/**
 * TeX Dashboard - Main Initialization
 * Compiles to vanilla JavaScript for browser use (no Node.js runtime required)
 * Version: 1.0
 */

import { AuditSummary } from './types';
import { RuleEngine } from './rule-engine';
import { SVGRenderer } from './renderer';

class TexDashboard {
  private summary: AuditSummary | null = null;
  private engine: RuleEngine | null = null;

  /**
   * Initialize dashboard by fetching and rendering audit summary
   */
  async initialize(summaryUrl: string = 'data/audit_summary.json'): Promise<void> {
    try {
      console.log('[TeX Dashboard] Initializing...');

      // Fetch audit summary
      const response = await fetch(summaryUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch summary: ${response.statusText}`);
      }

      this.summary = await response.json();
      this.engine = new RuleEngine(this.summary);

      console.log('[TeX Dashboard] Loaded SPI:', this.summary.spi);

      // Render dashboard components
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

  /**
   * Render header with hostname and timestamp
   */
  private renderHeader(): void {
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

  /**
   * Render SPI summary and finding counts
   */
  private renderSummary(): void {
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

  /**
   * Render SVG radar chart
   */
  private renderRadarChart(): void {
    if (!this.summary) return;

    const radarContainer = document.getElementById('radar-chart');
    if (!radarContainer) return;

    const radarSvg = SVGRenderer.generateRadarChart(
      this.summary.category_scores,
      400,
      400
    );

    radarContainer.innerHTML = `
      <div class="chart-container">
        <h2>Security Domain Scores</h2>
        ${radarSvg}
      </div>
    `;
  }

  /**
   * Render category score cards
   */
  private renderCategoryScores(): void {
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

    categoriesContainer.innerHTML = `
      <div class="categories-grid">
        ${cards}
      </div>
    `;
  }

  /**
   * Render findings table with filtering
   */
  private renderFindingsTable(): void {
    if (!this.summary || !this.engine) return;

    const tableContainer = document.getElementById('findings-table');
    if (!tableContainer) return;

    const failedFindings = this.engine.filterByStatus('FAIL').getResults();

    const rows = failedFindings
      .slice(0, 50) // Limit to first 50
      .map(
        (finding) => `
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
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  }

  /**
   * Render audit metadata
   */
  private renderMetadata(): void {
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

  /**
   * Display error message
   */
  private displayError(message: string): void {
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

  /**
   * Escape HTML special characters
   */
  private escapeHtml(text: string): string {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, (char) => map[char]);
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

// Export for use in browser console
declare global {
  interface Window {
    TexDashboard: typeof TexDashboard;
  }
}

window.TexDashboard = TexDashboard;
