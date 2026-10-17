/**
 * Executive Dashboard View Controller
 * Renders KPI cards, Chart.js animated analytics, priorities, and activity stream.
 */

const DashboardView = {
    pipelineChartInstance: null,
    growthChartInstance: null,

    defaultPriorities: [
        { id: 1, text: "Extract 20 new licensed dispensaries from Colorado MED registry", time: "25 min", done: true },
        { id: 2, text: "Dispatch 10 personalized LinkedIn connection requests", time: "15 min", done: false },
        { id: 3, text: "Follow up with 5 dispensaries in 'Responded' stage", time: "20 min", done: false },
        { id: 4, text: "Generate 15-SOP Package for tomorrow's audit demo", time: "10 min", done: false },
        { id: 5, text: "Deliver proposal to Chicago Windy City Botanicals", time: "15 min", done: true }
    ],

    render(state) {
        this.renderKPIs(state.stats);
        this.renderCharts(state.stats);
        this.renderPriorities();
        this.renderActivities(state.activities);
        this.setupFeedRefresh();
    },

    renderKPIs(stats) {
        if (!stats) return;

        const leadsEl = document.getElementById('kpi-leads-total');
        if (leadsEl) leadsEl.textContent = stats.total_leads;

        const sentEl = document.getElementById('kpi-messages-sent');
        if (sentEl) sentEl.textContent = stats.messages_sent;

        const respRateEl = document.getElementById('kpi-response-rate');
        if (respRateEl) respRateEl.textContent = `${stats.response_rate}% resp`;

        const callsEl = document.getElementById('kpi-calls-booked');
        if (callsEl) callsEl.textContent = stats.calls_booked;

        const revUsdEl = document.getElementById('kpi-revenue-usd');
        if (revUsdEl) revUsdEl.textContent = `$${stats.revenue_usd.toLocaleString()}`;

        const revPkrEl = document.getElementById('kpi-revenue-pkr');
        if (revPkrEl) revPkrEl.textContent = `${stats.revenue_pkr.toLocaleString()} PKR Earned 💰`;

        const dealsEl = document.getElementById('kpi-deals-count');
        if (dealsEl) dealsEl.textContent = `${stats.deals_closed} Deals Won`;
    },

    renderCharts(stats) {
        if (!stats) return;

        // 1. Pipeline Funnel Chart (Doughnut)
        const ctxPipeline = document.getElementById('pipelineChart');
        if (ctxPipeline) {
            if (this.pipelineChartInstance) {
                this.pipelineChartInstance.destroy();
            }

            const stages = stats.stages || {};
            const stageLabels = ['New Leads', 'Contacted', 'Responded', 'Calls Booked', 'Proposals Sent', 'Closed Won'];
            const stageData = [
                stages.new || 0,
                stages.contacted || 0,
                stages.responded || 0,
                stages.call_booked || 0,
                stages.proposal_sent || 0,
                stages.closed || 0
            ];

            this.pipelineChartInstance = new Chart(ctxPipeline, {
                type: 'doughnut',
                data: {
                    labels: stageLabels,
                    datasets: [{
                        data: stageData,
                        backgroundColor: [
                            '#334155', // New
                            '#3B82F6', // Contacted
                            '#8B5CF6', // Responded
                            '#F59E0B', // Call Booked
                            '#06B6D4', // Proposal Sent
                            '#10B981'  // Closed
                        ],
                        borderWidth: 2,
                        borderColor: '#0E1626'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#94A3B8',
                                font: { family: 'Plus Jakarta Sans', size: 11 },
                                boxWidth: 12,
                                padding: 10
                            }
                        }
                    },
                    cutout: '68%'
                }
            });
        }

        // 2. 90-Day Revenue Growth Chart (Line / Area)
        const ctxGrowth = document.getElementById('growthChart');
        if (ctxGrowth) {
            if (this.growthChartInstance) {
                this.growthChartInstance.destroy();
            }

            const labels = ['Week 1', 'Week 3', 'Week 6', 'Week 9', 'Week 12 (Target)'];
            const targetRevenueUSD = [1000, 3000, 6000, 9500, 12000];
            const currentRevenueUSD = [stats.revenue_usd, stats.revenue_usd * 1.4, null, null, null];

            this.growthChartInstance = new Chart(ctxGrowth, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: '90-Day Target ($12K / 3.3M PKR)',
                            data: targetRevenueUSD,
                            borderColor: 'rgba(255, 255, 255, 0.25)',
                            borderDash: [5, 5],
                            backgroundColor: 'transparent',
                            pointRadius: 3,
                            pointBackgroundColor: '#94A3B8'
                        },
                        {
                            label: 'Actual / Projected Revenue ($)',
                            data: currentRevenueUSD,
                            borderColor: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.12)',
                            fill: true,
                            tension: 0.35,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                            pointBackgroundColor: '#34D399'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.04)' },
                            ticks: { color: '#64748B', font: { size: 10 } }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.04)' },
                            ticks: {
                                color: '#64748B',
                                callback: val => `$${val.toLocaleString()}`
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: '#94A3B8',
                                font: { family: 'Plus Jakarta Sans', size: 11 }
                            }
                        }
                    }
                }
            });
        }
    },

    renderPriorities() {
        const container = document.getElementById('priority-list');
        if (!container) return;

        const saved = localStorage.getItem('verdant_priorities');
        const priorities = saved ? JSON.parse(saved) : this.defaultPriorities;

        container.innerHTML = priorities.map(item => `
            <div class="priority-item ${item.done ? 'completed' : ''}" data-id="${item.id}">
                <input type="checkbox" class="priority-check" ${item.done ? 'checked' : ''} onchange="DashboardView.togglePriority(${item.id})">
                <span class="priority-text">${item.text}</span>
                <span class="priority-time">⏱️ ${item.time}</span>
            </div>
        `).join('');
    },

    togglePriority(id) {
        const saved = localStorage.getItem('verdant_priorities');
        let priorities = saved ? JSON.parse(saved) : this.defaultPriorities;
        priorities = priorities.map(item => {
            if (item.id === id) {
                return { ...item, done: !item.done };
            }
            return item;
        });
        localStorage.setItem('verdant_priorities', JSON.stringify(priorities));
        this.renderPriorities();
    },

    renderActivities(activities) {
        const container = document.getElementById('activity-feed-list');
        if (!container) return;

        if (!activities || activities.length === 0) {
            container.innerHTML = '<div class="empty-state">No recent activities recorded.</div>';
            return;
        }

        const iconMap = {
            created: '🆕',
            message_sent: '📧',
            stage_changed: '🔄',
            call_booked: '📞',
            deal_closed: '💰',
            proposal_sent: '📄'
        };

        const bgMap = {
            created: 'rgba(59, 130, 246, 0.15)',
            message_sent: 'rgba(59, 130, 246, 0.15)',
            stage_changed: 'rgba(139, 92, 246, 0.15)',
            call_booked: 'rgba(245, 158, 11, 0.15)',
            deal_closed: 'rgba(16, 185, 129, 0.2)',
            proposal_sent: 'rgba(6, 182, 212, 0.15)'
        };

        container.innerHTML = activities.slice(0, 10).map(act => `
            <div class="activity-item">
                <div class="activity-icon" style="background: ${bgMap[act.activity_type] || 'rgba(255,255,255,0.05)'}">
                    ${iconMap[act.activity_type] || '⚡'}
                </div>
                <div class="activity-body">
                    <div class="activity-desc">${act.description}</div>
                    <div class="activity-time">${act.timestamp || 'Just now'}</div>
                </div>
            </div>
        `).join('');
    },

    setupFeedRefresh() {
        const btn = document.getElementById('btn-refresh-feed');
        if (btn) {
            btn.onclick = () => {
                App.refreshData();
                App.toast("Refreshed live activities", "info");
            };
        }
    }
};

window.DashboardView = DashboardView;
