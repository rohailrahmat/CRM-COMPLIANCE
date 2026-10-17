/**
 * Visual Kanban Pipeline Controller
 * Drag & Drop Kanban stage progression, deal values, and closing triggers.
 */

const PipelineView = {
    stages: [
        { id: 'new', label: '🆕 New Leads', color: '#94A3B8' },
        { id: 'contacted', label: '📧 Contacted', color: '#3B82F6' },
        { id: 'responded', label: '💬 Responded', color: '#8B5CF6' },
        { id: 'call_booked', label: '📞 Call Booked', color: '#F59E0B' },
        { id: 'proposal_sent', label: '📄 Proposal Sent', color: '#06B6D4' },
        { id: 'closed', label: '💰 Closed Won', color: '#10B981' }
    ],

    draggedLeadId: null,

    render(leads) {
        const board = document.getElementById('kanban-board');
        if (!board) return;

        let totalPipelineValue = 0;
        let closedCount = 0;

        board.innerHTML = this.stages.map(stage => {
            const stageLeads = (leads || []).filter(l => l.status === stage.id);
            const stageTotal = stageLeads.reduce((acc, l) => acc + (l.deal_value || 0), 0);
            totalPipelineValue += stageTotal;

            if (stage.id === 'closed') {
                closedCount = stageLeads.length;
            }

            const cardsHtml = stageLeads.map(lead => this.createCardHtml(lead, stage.id)).join('');

            return `
                <div class="kanban-column" data-stage="${stage.id}" ondragover="PipelineView.onDragOver(event)" ondragleave="PipelineView.onDragLeave(event)" ondrop="PipelineView.onDrop(event, '${stage.id}')">
                    <div class="kanban-column-header">
                        <div class="column-title-group">
                            <span class="column-title" style="color: ${stage.color}">${stage.label}</span>
                            <span class="column-count">${stageLeads.length}</span>
                        </div>
                        <span class="column-total-val">$${stageTotal.toLocaleString()}</span>
                    </div>
                    <div class="kanban-cards-wrapper" id="kanban-col-${stage.id}">
                        ${cardsHtml}
                    </div>
                </div>
            `;
        }).join('');

        // Header summary metrics
        const totalValEl = document.getElementById('kanban-total-value');
        if (totalValEl) totalValEl.textContent = `$${totalPipelineValue.toLocaleString()}`;

        const closedCountEl = document.getElementById('kanban-closed-count');
        if (closedCountEl) closedCountEl.textContent = `${closedCount} Closed`;
    },

    createCardHtml(lead, currentStage) {
        const nextStageMap = {
            'new': { next: 'contacted', label: 'Contact ➔' },
            'contacted': { next: 'responded', label: 'Responded ➔' },
            'responded': { next: 'call_booked', label: 'Book Call ➔' },
            'call_booked': { next: 'proposal_sent', label: 'Send Proposal ➔' },
            'proposal_sent': { next: 'closed', label: 'Close Deal ➔' },
            'closed': null
        };

        const nextAction = nextStageMap[currentStage];

        return `
            <div class="kanban-card" draggable="true" ondragstart="PipelineView.onDragStart(event, ${lead.id})" ondragend="PipelineView.onDragEnd(event)">
                <div class="card-top-row">
                    <span class="card-lead-name">${lead.business_name}</span>
                    <span class="card-state-pill">${lead.state}</span>
                </div>
                <div class="card-meta-text">👤 ${lead.owner_name || 'Owner'} (${lead.city || 'Metro'})</div>
                <div class="card-meta-text" style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #64748B;">
                    Lic: ${lead.license_number || 'N/A'}
                </div>
                <div class="card-footer-row">
                    <span class="card-deal-value">$${lead.deal_value || 997}</span>
                    ${nextAction ? `
                        <button class="card-advance-btn" onclick="PipelineView.advanceStage(${lead.id}, '${nextAction.next}')">
                            ${nextAction.label}
                        </button>
                    ` : '<span style="font-size: 0.68rem; color: #10B981; font-weight: 700;">✅ WON</span>'}
                </div>
            </div>
        `;
    },

    onDragStart(e, leadId) {
        this.draggedLeadId = leadId;
        e.target.classList.add('dragging');
        e.dataTransfer.setData('text/plain', leadId);
    },

    onDragEnd(e) {
        e.target.classList.remove('dragging');
        document.querySelectorAll('.kanban-column').forEach(col => col.classList.remove('drag-over'));
    },

    onDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    },

    onDragLeave(e) {
        e.currentTarget.classList.remove('drag-over');
    },

    async onDrop(e, targetStage) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        const leadId = this.draggedLeadId;
        if (!leadId) return;

        await this.advanceStage(leadId, targetStage);
        this.draggedLeadId = null;
    },

    async advanceStage(leadId, targetStage) {
        try {
            const res = await fetch(`/api/leads/${leadId}/status`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: targetStage })
            });
            const result = await res.json();
            if (result.success) {
                if (targetStage === 'closed') {
                    App.triggerConfetti();
                    App.toast("🎉 Deal Closed Won! Revenue updated.", "success");
                } else {
                    App.toast(`Moved lead to ${targetStage.replace('_', ' ').toUpperCase()}`, "info");
                }
                App.refreshData();
            }
        } catch (err) {
            App.toast("Failed to move lead stage", "error");
        }
    }
};

window.PipelineView = PipelineView;
