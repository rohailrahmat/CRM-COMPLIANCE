/**
 * Core Application Manager & Global State
 */

const App = {
    state: {
        currentPage: 'dashboard',
        stats: null,
        leads: [],
        activities: [],
        settings: {}
    },

    async init() {
        this.setupNavigation();
        this.setupModals();
        this.setupSidebarToggle();
        
        // Initial data fetch
        await this.refreshData();

        // Listen for global custom events
        window.addEventListener('lead-updated', () => this.refreshData());
    },

    async refreshData() {
        try {
            const [statsRes, leadsRes, actRes, setRes] = await Promise.all([
                fetch('/api/stats'),
                fetch('/api/leads'),
                fetch('/api/activities'),
                fetch('/api/settings')
            ]);

            this.state.stats = await statsRes.json();
            this.state.leads = await leadsRes.json();
            this.state.activities = await actRes.json();
            this.state.settings = await setRes.json();

            this.updateGlobalBadges();
            
            // Dispatch page-specific renders
            if (window.DashboardView) DashboardView.render(this.state);
            if (window.LeadsView) LeadsView.render(this.state.leads);
            if (window.PipelineView) PipelineView.render(this.state.leads);
            if (window.OutreachView) OutreachView.render(this.state);
            if (window.SettingsView) SettingsView.render(this.state.settings);

        } catch (err) {
            console.error("Data synchronization error:", err);
            this.toast("Failed to sync with local backend database", "error");
        }
    },

    updateGlobalBadges() {
        const stats = this.state.stats;
        if (!stats) return;

        // Sidebar Badges
        const leadsCountBadge = document.getElementById('badge-leads-count');
        if (leadsCountBadge) leadsCountBadge.textContent = stats.total_leads;

        const pipelineDealsBadge = document.getElementById('badge-pipeline-deals');
        if (pipelineDealsBadge) pipelineDealsBadge.textContent = stats.deals_closed;

        const sidebarRev = document.getElementById('sidebar-revenue-val');
        if (sidebarRev) sidebarRev.textContent = `$${stats.revenue_usd.toLocaleString()}`;

        const sidebarProg = document.getElementById('sidebar-progress');
        if (sidebarProg) {
            const pct = Math.min(100, Math.round((stats.revenue_usd / 12000) * 100));
            sidebarProg.style.width = `${Math.max(10, pct)}%`;
        }

        const specName = document.getElementById('sidebar-specialist-name');
        if (specName && this.state.settings.specialist_name) {
            specName.textContent = this.state.settings.specialist_name;
        }
    },

    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-item');
        const views = document.querySelectorAll('.page-view');
        const titleEl = document.getElementById('page-header-title');
        const subEl = document.getElementById('page-header-sub');

        const pageTitles = {
            dashboard: { title: 'Executive Dashboard', sub: 'Cannabis Compliance & Automated Client Acquisition' },
            leads: { title: 'State Registry Lead Generator', sub: 'Verified Dispensaries & Licensee Contact Scraping' },
            outreach: { title: 'Outreach Automation System', sub: 'Multi-Channel High-Conversion Personalization Engine' },
            pipeline: { title: 'Sales Pipeline Kanban Board', sub: 'Visual Deal Progression & Revenue Velocity' },
            documents: { title: 'AI Compliance SOP Generator', sub: 'Certified State-Audited PDF Standard Operating Procedures' },
            settings: { title: 'System Configuration', sub: 'Agency Branding, API Integration & Local Storage Controls' }
        };

        navButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetPage = btn.getAttribute('data-page');
                
                navButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                views.forEach(v => {
                    v.classList.remove('active');
                    if (v.id === `view-${targetPage}`) {
                        v.classList.add('active');
                    }
                });

                if (pageTitles[targetPage]) {
                    titleEl.textContent = pageTitles[targetPage].title;
                    subEl.textContent = pageTitles[targetPage].sub;
                }

                this.state.currentPage = targetPage;
                
                // Re-render charts or kanban if needed
                if (targetPage === 'dashboard' && window.DashboardView) DashboardView.renderCharts();
                if (targetPage === 'pipeline' && window.PipelineView) PipelineView.render(this.state.leads);
            });
        });
    },

    setupSidebarToggle() {
        const toggleBtn = document.getElementById('btn-sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }
    },

    setupModals() {
        // Quick Add Lead Modal
        const btnAddLead = document.getElementById('btn-quick-new-lead');
        const modalAddLead = document.getElementById('modal-add-lead');
        const closeLeadModal = document.getElementById('btn-close-lead-modal');
        const cancelLeadModal = document.getElementById('btn-cancel-lead-modal');
        const formAddLead = document.getElementById('form-quick-add-lead');

        const openLeadModal = () => modalAddLead.classList.add('open');
        const hideLeadModal = () => modalAddLead.classList.remove('open');

        if (btnAddLead) btnAddLead.addEventListener('click', openLeadModal);
        if (closeLeadModal) closeLeadModal.addEventListener('click', hideLeadModal);
        if (cancelLeadModal) cancelLeadModal.addEventListener('click', hideLeadModal);

        if (formAddLead) {
            formAddLead.addEventListener('submit', async (e) => {
                e.preventDefault();
                const payload = {
                    business_name: document.getElementById('add-business-name').value,
                    owner_name: document.getElementById('add-owner-name').value,
                    license_number: document.getElementById('add-license-number').value,
                    state: document.getElementById('add-state').value,
                    city: document.getElementById('add-city').value,
                    email: document.getElementById('add-email').value,
                    phone: document.getElementById('add-phone').value,
                    deal_value: parseInt(document.getElementById('add-deal-value').value) || 997,
                    status: document.getElementById('add-stage').value
                };

                try {
                    const res = await fetch('/api/leads', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (result.success) {
                        this.toast(`Added ${payload.business_name} to CRM`, 'success');
                        hideLeadModal();
                        formAddLead.reset();
                        this.refreshData();
                    }
                } catch (err) {
                    this.toast("Failed to save lead", "error");
                }
            });
        }

        // Quick Close Deal Modal
        const btnCloseDeal = document.getElementById('btn-quick-close-deal');
        const modalCloseDeal = document.getElementById('modal-close-deal');
        const btnDismissDeal = document.getElementById('btn-close-deal-modal');
        const btnCancelDeal = document.getElementById('btn-cancel-deal-modal');
        const formRecordDeal = document.getElementById('form-record-deal');

        const openDealModal = () => {
            this.populateDealLeadsDropdown();
            modalCloseDeal.classList.add('open');
        };
        const hideDealModal = () => modalCloseDeal.classList.remove('open');

        if (btnCloseDeal) btnCloseDeal.addEventListener('click', openDealModal);
        if (btnDismissDeal) btnDismissDeal.addEventListener('click', hideDealModal);
        if (btnCancelDeal) btnCancelDeal.addEventListener('click', hideDealModal);

        if (formRecordDeal) {
            formRecordDeal.addEventListener('submit', async (e) => {
                e.preventDefault();
                const leadId = document.getElementById('deal-lead-select').value;
                const pkgValue = parseInt(document.getElementById('deal-package').value);
                const notes = document.getElementById('deal-notes').value;

                try {
                    const res = await fetch(`/api/leads/${leadId}/status`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            status: 'closed',
                            notes: `Closed Won: $${pkgValue} Package. ${notes}`
                        })
                    });
                    const result = await res.json();
                    if (result.success) {
                        this.triggerConfetti();
                        this.toast(`🎉 Deal Closed! Revenue credited to your pipeline.`, 'success');
                        hideDealModal();
                        this.refreshData();
                    }
                } catch (err) {
                    this.toast("Failed to record closed deal", "error");
                }
            });
        }

        // Quick SOP package shortcut
        const btnQuickSop = document.getElementById('btn-quick-sop');
        if (btnQuickSop) {
            btnQuickSop.addEventListener('click', () => {
                document.getElementById('nav-documents').click();
            });
        }
    },

    populateDealLeadsDropdown() {
        const select = document.getElementById('deal-lead-select');
        if (!select) return;
        select.innerHTML = '';

        const activeLeads = this.state.leads.filter(l => l.status !== 'closed');
        if (activeLeads.length === 0) {
            select.innerHTML = '<option value="">No active leads available. Add one first!</option>';
            return;
        }

        activeLeads.forEach(lead => {
            const opt = document.createElement('option');
            opt.value = lead.id;
            opt.textContent = `${lead.business_name} (${lead.state}) - Stage: ${lead.status.toUpperCase()}`;
            select.appendChild(opt);
        });
    },

    toast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : 'ℹ️');
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    triggerConfetti() {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 80,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#10B981', '#34D399', '#3B82F6', '#F59E0B']
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
