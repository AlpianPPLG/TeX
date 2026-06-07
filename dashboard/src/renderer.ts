/**
 * TeX Dashboard - SVG Chart Renderer
 * Renders radar charts and progress rings without external chart libraries
 * Version: 1.0
 */

import { RadarPoint, SVGRadarConfig } from './types';

export class SVGRenderer {
  /**
   * Generate radar chart SVG from category scores
   * Six-axis radar representing six security domains
   */
  static generateRadarChart(
    categoryScores: Record<string, number>,
    width: number = 400,
    height: number = 400
  ): string {
    const config: SVGRadarConfig = {
      centerX: width / 2,
      centerY: height / 2,
      radius: Math.min(width, height) / 2.5,
      axisCount: 6,
    };

    const axes = Object.keys(categoryScores).slice(0, 6);
    const scores = axes.map((axis) => categoryScores[axis] || 0);

    // Generate axis lines and labels
    const axisLines = axes
      .map((axis, i) => {
        const angle = (Math.PI * 2 * i) / config.axisCount - Math.PI / 2;
        const x2 = config.centerX + config.radius * Math.cos(angle);
        const y2 = config.centerY + config.radius * Math.sin(angle);

        const labelX = config.centerX + (config.radius + 30) * Math.cos(angle);
        const labelY = config.centerY + (config.radius + 30) * Math.sin(angle);

        return {
          line: `<line x1="${config.centerX}" y1="${config.centerY}" x2="${x2}" y2="${y2}" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>`,
          label: `<text x="${labelX}" y="${labelY}" text-anchor="middle" dominant-baseline="middle" font-size="12" fill="rgba(255,255,255,0.7)">${axis.toUpperCase()}</text>`,
        };
      })
      .reduce((acc, item) => {
        acc.lines.push(item.line);
        acc.labels.push(item.label);
        return acc;
      }, { lines: [] as string[], labels: [] as string[] });

    // Generate grid circles
    const gridCircles = [25, 50, 75, 100]
      .map(
        (percent) =>
          `<circle cx="${config.centerX}" cy="${config.centerY}" r="${
            (config.radius * percent) / 100
          }" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>`
      )
      .join('');

    // Generate score polygon
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

    // Combine SVG
    const svg = `<svg viewBox="0 0 ${width} ${height}" class="radar-chart" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>
          .radar-chart { background-color: rgba(0, 0, 0, 0.5); }
        </style>
      </defs>
      ${gridCircles}
      ${axisLines.lines.join('')}
      ${scorePolygon}
      ${axisLines.labels.join('')}
    </svg>`;

    return svg;
  }

  /**
   * Generate SVG progress ring for score visualization
   */
  static generateProgressRing(
    score: number,
    radius: number = 60,
    strokeWidth: number = 6
  ): string {
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;

    // Color by score threshold
    let color = '#10b981'; // green
    if (score < 80) color = '#f59e0b'; // amber
    if (score < 60) color = '#ef4444'; // red

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

  /**
   * Generate severity color badge
   */
  static getSeverityColor(severity: string): string {
    const colorMap: Record<string, string> = {
      CRITICAL: '#ef4444',
      HIGH: '#f97316',
      MEDIUM: '#eab308',
      LOW: '#6b7280',
      PASS: '#10b981',
    };
    return colorMap[severity] || '#6b7280';
  }

  /**
   * Generate severity badge HTML
   */
  static generateSeverityBadge(severity: string): string {
    const color = this.getSeverityColor(severity);
    return `<span style="display:inline-block; padding:2px 8px; border-radius:4px; background-color:${color}; color:white; font-size:12px; font-weight:bold;">${severity}</span>`;
  }

  /**
   * Format large numbers with commas
   */
  static formatNumber(num: number): string {
    return num.toLocaleString();
  }

  /**
   * Format timestamp to readable date
   */
  static formatDate(timestamp: number): string {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  /**
   * Format timestamp to time string
   */
  static formatTime(timestamp: number): string {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }
}
