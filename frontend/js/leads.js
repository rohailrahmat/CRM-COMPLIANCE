/**
 * Lead Generator & Contact Manager View
 */

const LeadsView = {
    currentLeads: [],

    init() {
        this.setupScraper();
        this.setupFilters();
        this.setupExports();
    },

    render(leads) {
        this.currentLeads = leads || [];
        this.applyFilters();
    },

    setupScraper() {
        const btnLaunch = document.getElementById('btn-launch-scraper');
        const terminal = document.getElementById('scraper-terminal');
        const fillBar = document.getElementById('scraper-progress-fill');
        const logBox = document.getElementById('scraper-output-log');
        const statusText = document.getElementById('scraper-status-text');

        if (!btnLaunch) return;

        btnLaunch.addEventListener('click', async () => {
            const state = document.getElementById('select-target-state').value;
            const licType = document.getElementById('select-license-type').value;
            const count = parseInt(document.getElementById('input-lead-quantity').value) || 20;

            btnLaunch.disabled = true;
            terminal.style.display = 'block';
            fillBar.style.width = '10%';
            statusText.textContent = 'CONNECTING...';
            logBox.innerHTML = `[CONNECT] Establishing SSL socket to ${state} Cannabis Licensing Registry...\n`;

            // Simulation step 1
            await new Promise(r => setTimeout(r, 600));
            fillBar.style.width = '35%';
            logBox.innerHTML += `[QUERY] Searching licensed active ${licType} facilities...\n`;
            statusText.textContent = 'EXTRACTING RECORDS...';

            // Simulation step 2
            await new Promise(r => setTimeout(r, 700));
            fillBar.style.width = '70%';
            logBox.innerHTML += `[PARSE] Resolving ownership records, business addresses, phone numbers & corporate emails...\n`;
            statusText.textContent = 'VALIDATING CONTACTS...';

            // Call API
            try {
                const res = await fetch('/api/leads/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state, count, license_type: licType })
                });
                const data = await res.json();

                fillBar.style.width = '100%';
                statusText.textContent = 'COMPLETE';
                logBox.innerHTML += `[SUCCESS] Indexed ${data.count} verified dispensary prospects from ${state}.\n`;
                logBox.scrollTop = logBox.scrollHeight;

                App.toast(`Extracted ${data.count} new leads from ${state}!`, 'success');
                await App.refreshData();

                setTimeout(() => {
                    terminal.style.display = 'none';
                    fillBar.style.width = '0%';
                    btnLaunch.disabled = false;
                }, 4000);

            } catch (err) {
                statusText.textContent = 'ERROR';
                logBox.innerHTML += `[ERROR] Extraction failed: ${err.message}\n`;
                btnLaunch.disabled = false;
            }
        });
    },

    setupFilters() {
        const searchInput = document.getElementById('table-search-input');
        const filterState = document.getElementById('table-filter-state');
        const filterStage = document.getElementById('table-filter-stage');

        const handler = () => this.applyFilters();

        if (searchInput) searchInput.addEventListener('input', handler);
        if (filterState) filterState.addEventListener('change', handler);
        if (filterStage) filterStage.addEventListener('change', handler);
    },

    applyFilters() {
        const search = (document.getElementById('table-search-input')?.value || '').toLowerCase();
        const stateVal = document.getElementById('table-filter-state')?.value || 'all';
        const stageVal = document.getElementById('table-filter-stage')?.value || 'all';

        const filtered = this.currentLeads.filter(lead => {
            const matchesSearch = !search ||
                lead.business_name?.toLowerCase().includes(search) ||
                lead.owner_name?.toLowerCase().includes(search) ||
                lead.city?.toLowerCase().includes(search) ||
                lead.license_number?.toLowerCase().includes(search);

            const matchesState = stateVal === 'all' || lead.state === stateVal;
            const matchesStage = stageVal === 'all' || lead.status === stageVal;

            return matchesSearch && matchesState && matchesStage;
        });

        this.renderTable(filtered);
    },

    renderTable(leads) {
        const tbody = document.getElementById('leads-table-body');
        if (!tbody) return;

        if (leads.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 2.5rem; color: #64748B;">
                        No prospects match your current search filters. Click <b>"Extract Registry Leads"</b> or <b>"➕ Add Lead"</b>.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = leads.map(lead => {
            const stages = [
                { val: 'new', label: 'New Lead' },
                { val: 'contacted', label: 'Contacted' },
                { val: 'responded', label: 'Responded' },
                { val: 'call_booked', label: 'Call Booked' },
                { val: 'proposal_sent', label: 'Proposal Sent' },
                { val: 'closed', label: 'Closed Won' }
            ];

            const options = stages.map(s => 
                `<option value="${s.val}" ${lead.status === s.val ? 'selected' : ''}>${s.label}</option>`
            ).join('');

            return `
                <tr data-id="${lead.id}">
                    <td>
                        <span class="table-business-name">${lead.business_name}</span>
                        <span class="table-license-num">${lead.license_number || 'PENDING'}</span>
                    </td>
                    <td>
                        <div style="font-weight: 500;">${lead.owner_name || 'Owner / Executive'}</div>
                        <div style="font-size: 0.7rem; color: #64748B;">${lead.license_type || 'Retail'}</div>
                    </td>
                    <td>
                        <div>${lead.city || 'Metro'}, ${lead.state}</div>
                    </td>
                    <td>
                        <a href="tel:${lead.phone}" class="table-meta-link">${lead.phone || 'N/A'}</a>
                    </td>
                    <td>
                        <a href="mailto:${lead.email}" class="table-meta-link">${lead.email || 'N/A'}</a>
                        ${lead.linkedin ? `<a href="https://${lead.linkedin}" target="_blank" class="table-meta-link" style="color: #10B981;">LinkedIn Profile ↗</a>` : ''}
                    </td>
                    <td>
                        <select class="stage-pill-select" onchange="LeadsView.handleStageChange(${lead.id}, this.value)">
                            ${options}
                        </select>
                    </td>
                    <td>
                        <span style="font-family: 'Outfit'; font-weight: 700; color: #34D399;">$${lead.deal_value || 997}</span>
                    </td>
                    <td>
                        <div style="display: flex; gap: 0.4rem;">
                            <button class="btn btn-ghost btn-xs" onclick="LeadsView.triggerSOPForLead(${lead.id})" title="Generate SOPs">📄 SOP</button>
                            <button class="btn btn-ghost btn-xs text-danger" onclick="LeadsView.deleteLead(${lead.id})" title="Delete">🗑️</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },

    async handleStageChange(leadId, newStage) {
        try {
            const res = await fetch(`/api/leads/${leadId}/status`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStage })
            });
            const result = await res.json();
            if (result.success) {
                if (newStage === 'closed') {
                    App.triggerConfetti();
                }
                App.toast(`Lead stage moved to ${newStage.toUpperCase()}`, 'success');
                App.refreshData();
            }
        } catch (err) {
            App.toast("Failed to update status", "error");
        }
    },

    async deleteLead(leadId) {
        if (!confirm("Are you sure you want to remove this prospect from the CRM?")) return;
        try {
            const res = await fetch(`/api/leads/${leadId}`, { method: 'DELETE' });
            const result = await res.json();
            if (result.success) {
                App.toast("Lead removed", "info");
                App.refreshData();
            }
        } catch (err) {
            App.toast("Failed to delete lead", "error");
        }
    },

    triggerSOPForLead(leadId) {
        const lead = this.currentLeads.find(l => l.id === leadId);
        if (!lead) return;

        document.getElementById('doc-client-name').value = lead.business_name;
        document.getElementById('doc-license-num').value = lead.license_number || 'CO-402-00100';
        document.getElementById('doc-state').value = lead.state || 'Colorado';
        document.getElementById('nav-documents').click();
        App.toast(`Pre-filled SOP form for ${lead.business_name}`, 'info');
    },

    setupExports() {
        const btnCsv = document.getElementById('btn-export-leads-csv');
        const btnJson = document.getElementById('btn-export-leads-json');

        if (btnCsv) {
            btnCsv.addEventListener('click', () => {
                if (!this.currentLeads.length) {
                    App.toast("No leads to export", "warning");
                    return;
                }
                const headers = ["ID", "Business Name", "License #", "Type", "Owner", "City", "State", "Phone", "Email", "LinkedIn", "Status", "Value"];
                const rows = this.currentLeads.map(l => [
                    l.id, `"${l.business_name}"`, `"${l.license_number}"`, `"${l.license_type}"`,
                    `"${l.owner_name}"`, `"${l.city}"`, `"${l.state}"`, `"${l.phone}"`, `"${l.email}"`,
                    `"${l.linkedin}"`, l.status, l.deal_value
                ]);

                const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
                const encodedUri = encodeURI(csvContent);
                const link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", `cannabis_leads_${new Date().toISOString().slice(0, 10)}.csv`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                App.toast("Exported leads to CSV", "success");
            });
        }

        if (btnJson) {
            btnJson.addEventListener('click', () => {
                if (!this.currentLeads.length) {
                    App.toast("No leads to export", "warning");
                    return;
                }
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.currentLeads, null, 2));
                const link = document.createElement("a");
                link.setAttribute("href", dataStr);
                link.setAttribute("download", `cannabis_leads_${new Date().toISOString().slice(0, 10)}.json`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                App.toast("Exported leads to JSON", "success");
            });
        }
    }
};

window.LeadsView = LeadsView;
LeadsView.init();
