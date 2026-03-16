// ========================================
// CareerMantra AI - Analytics Dashboard
// Charts + Stats + Progress Tracker
// ========================================

class CareerAnalytics {
    constructor() {
        this.stats = {
            totalPractice: 47,
            avgScore: 8.2,
            streak: 5,
            interviews: 12,
            bestLevel: 9,
            totalTime: '23h 45m'
        };
        this.practiceData = [
            { level: 1, score: 10, date: '2026-03-10' },
            { level: 2, score: 9, date: '2026-03-11' },
            { level: 3, score: 8, date: '2026-03-12' },
            { level: 4, score: 10, date: '2026-03-13' },
            { level: 5, score: 7, date: '2026-03-14' },
            { level: 6, score: 9, date: '2026-03-15' }
        ];
        this.init();
    }

    init() {
        this.renderStats();
        this.createCharts();
        this.initFilters();
        this.loadProgressData();
        this.animateCounters();
    }

    renderStats() {
        const statsHtml = `
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                <div class="stat-card" data-target="${this.stats.totalPractice}">
                    <div class="stat-icon">📚</div>
                    <div class="stat-value" data-counter="true">0</div>
                    <div class="stat-label">Practice Sessions</div>
                </div>
                <div class="stat-card" data-target="${this.stats.avgScore}">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-value" data-counter="true">0.0</div>
                    <div class="stat-label">Avg Score</div>
                </div>
                <div class="stat-card" data-target="${this.stats.streak}">
                    <div class="stat-icon">🔥</div>
                    <div class="stat-value" data-counter="true">0</div>
                    <div class="stat-label">Streak</div>
                </div>
                <div class="stat-card" data-target="${this.stats.interviews}">
                    <div class="stat-icon">🎤</div>
                    <div class="stat-value" data-counter="true">0</div>
                    <div class="stat-label">Mock Interviews</div>
                </div>
                <div class="stat-card" data-target="${this.stats.bestLevel}">
                    <div class="stat-icon">🥇</div>
                    <div class="stat-value" data-counter="true">0</div>
                    <div class="stat-label">Best Level</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⏱️</div>
                    <div class="stat-value">${this.stats.totalTime}</div>
                    <div class="stat-label">Total Practice Time</div>
                </div>
            </div>
        `;
        document.getElementById('stats-grid').innerHTML = statsHtml;
    }

    createCharts() {
        // Progress Chart (Line Chart)
        this.renderLineChart('progress-chart', this.practiceData);
        
        // Level Distribution (Bar Chart)
        this.renderBarChart('level-chart', [
            { level: 'Easy', score: 95 },
            { level: 'Medium', score: 82 },
            { level: 'Hard', score: 71 }
        ]);
        
        // Weekly Activity (Doughnut Chart)
        this.renderDoughnutChart('activity-chart', [
            { day: 'Mon', sessions: 3 },
            { day: 'Tue', sessions: 5 },
            { day: 'Wed', sessions: 2 },
            { day: 'Thu', sessions: 4 },
            { day: 'Fri', sessions: 6 },
            { day: 'Sat', sessions: 1 },
            { day: 'Sun', sessions: 0 }
        ]);
    }

    renderLineChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Responsive sizing
        const width = canvas.offsetWidth;
        const height = canvas.offsetHeight;
        canvas.width = width * 2;
        canvas.height = height * 2;
        ctx.scale(2, 2);
        
        // Grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            ctx.beginPath();
            ctx.moveTo(60, height * 0.15 + (height * 0.7 / 5) * i);
            ctx.lineTo(width - 20, height * 0.15 + (height * 0.7 / 5) * i);
            ctx.stroke();
        }
        
        // Data points and line
        const maxScore = 10;
        const points = data.map((d, i) => ({
            x: 80 + (width - 100) * i / (data.length - 1),
            y: height * 0.15 + (height * 0.7) * (1 - d.score / maxScore)
        }));
        
        // Draw line
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.shadowColor = '#3b82f6';
        ctx.shadowBlur = 10;
        ctx.beginPath();
        points.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
        ctx.stroke();
        ctx.shadowBlur = 0;
        
        // Data points
        points.forEach(p => {
            ctx.fillStyle = '#3b82f6';
            ctx.beginPath();
            ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.stroke();
        });
        
        // Labels
        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 14px Inter, sans-serif';
        ctx.textAlign = 'center';
        data.forEach((d, i) => {
            ctx.fillText(d.score, points[i].x, points[i].y - 25);
        });
    }

    renderBarChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth * 2;
        canvas.height = canvas.offsetHeight * 2;
        ctx.scale(2, 2);
        
        const barWidth = (canvas.offsetWidth - 80) / data.length;
        const maxScore = Math.max(...data.map(d => d.score));
        
        data.forEach((item, i) => {
            const barHeight = (canvas.offsetHeight * 0.7) * (item.score / maxScore);
            const x = 40 + i * barWidth;
            const y = canvas.offsetHeight * 0.85 - barHeight;
            
            // Bar
            ctx.fillStyle = `hsl(${220 - i * 30}, 70%, 50%)`;
            ctx.shadowColor = `hsl(${220 - i * 30}, 70%, 40%)`;
            ctx.shadowBlur = 15;
            ctx.fillRect(x, y, barWidth * 0.7, barHeight);
            ctx.shadowBlur = 0;
            
            // Label
            ctx.fillStyle = '#1f2937';
            ctx.font = 'bold 12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(item.score, x + barWidth * 0.35, y - 10);
            ctx.fillText(item.level, x + barWidth * 0.35, canvas.offsetHeight * 0.88);
        });
    }

    renderDoughnutChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth * 2;
        canvas.height = canvas.offsetHeight * 2;
        ctx.scale(2, 2);
        
        const centerX = canvas.offsetWidth / 2;
        const centerY = canvas.offsetHeight / 2;
        const radius = Math.min(centerX, centerY) * 0.4;
        const total = data.reduce((sum, d) => sum + d.sessions, 0);
        
        let startAngle = 0;
        data.forEach((item, i) => {
            const sliceAngle = (Math.PI * 2 * item.sessions) / total;
            ctx.fillStyle = `hsl(${i * 50}, 70%, 60%)`;
            ctx.shadowColor = `hsl(${i * 50}, 70%, 40%)`;
            ctx.shadowBlur = 20;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();
            startAngle += sliceAngle;
        });
        ctx.shadowBlur = 0;
        
        // Center circle
        ctx.fillStyle = '#f8fafc';
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * 0.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 4;
        ctx.stroke();
    }

    animateCounters() {
        const counters = document.querySelectorAll('[data-counter="true"]');
        counters.forEach(counter => {
            const target = parseFloat(counter.closest('.stat-card').dataset.target);
            const isDecimal = target % 1 !== 0;
            let current = 0;
            const increment = target / 100;
            const updateCounter = () => {
                if (isDecimal) {
                    current += increment;
                    counter.textContent = current.toFixed(1);
                } else {
                    current += increment;
                    counter.textContent = Math.floor(current);
                }
                if (current < target) {
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = isDecimal ? target.toFixed(1) : Math.floor(target);
                }
            };
            updateCounter();
        });
    }

    initFilters() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                this.filterData(filter);
            });
        });
    }

    filterData(filter) {
        // Simulate data filtering
        showToast(`Filtering by ${filter}... 📊`, 'info');
    }

    loadProgressData() {
        // Load from localStorage or API
        const saved = localStorage.getItem('analytics_data');
        if (saved) {
            this.stats = { ...this.stats, ...JSON.parse(saved) };
            this.renderStats();
        }
    }

    saveProgress() {
        localStorage.setItem('analytics_data', JSON.stringify(this.stats));
    }
}

// 🎮 Initialize Analytics
const analytics = new CareerAnalytics();

// 🔔 Export for HTML onclick
window.exportData = () => {
    const dataStr = JSON.stringify(analytics.stats, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'career-analytics.json';
    link.click();
    showToast('Analytics exported! 📥');
};

// 🎨 Auto-inject CSS for charts
const style = document.createElement('style');
style.textContent = `
    .stat-card { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .stat-card:hover { transform: translateY(-8px) scale(1.02); }
    canvas { max-height: 300px; }
    .filter-btn.active { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
`;
document.head.appendChild(style);
