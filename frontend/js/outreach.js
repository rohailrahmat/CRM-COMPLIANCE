/**
 * Outreach Automation View Controller
 */

const OutreachView = {
    templates: {
        linkedin_connect: {
            subject: "",
            body: `Hi {name},

I noticed {business_name} in {city}. I help licensed cannabis dispensaries streamline their state compliance documentation and Metrc audit SOPs.

Would love to connect with fellow cannabis operators in {state}!

Best regards,
{sender_name}`
        },
        linkedin_followup: {
            subject: "",
            body: `Hi {name}, thanks for connecting!

Quick question: How is {business_name} currently managing state compliance documentation (SOPs, employee training logs, and inventory quarantine protocols)?

Most dispensary owners I talk to in {state} tell me traditional compliance consultants take 3 to 4 weeks and charge $8,000 to $15,000+.

We deliver a complete, state-certified 15-SOP Package customized for your license #{license_number} in under 72 hours for just $997.

Worth a quick 15-minute call to see how we bulletproof your facility against state audit fines?

My calendar: {calendly_link}`
        },
        cold_email: {
            subject: `Quick Question Regarding {business_name} Compliance Documentation`,
            body: `Hi {name},

Congratulations on your active license ({license_number}) for {business_name} in {city}!

I wanted to reach out because state cannabis compliance audits have tightened significantly this quarter across {state}.

How is your management team handling mandatory Standard Operating Procedures (SOPs), cash handling anti-diversion protocols, and Metrc track-and-trace reconciliation?

Rather than paying consultants $10K+ or spending 40+ hours drafting documents yourself, our automated platform delivers custom, certified compliance packages tailored to your exact POS system in 72 hours.

Do you have 10 minutes this Thursday or Friday for a quick walkthrough?

Direct Calendar Link: {calendly_link}

Best regards,
{sender_name}
Cannabis Compliance Documentation Specialist`
        },
        day7_followup: {
            subject: `Free Compliance Audit Checklist for {business_name}`,
            body: `Hi {name},

Following up on my note last week regarding compliance protocols for {business_name}.

I put together a quick 12-point State Audit Readiness Checklist for dispensaries in {state}. It covers the exact friction points state inspectors flag first (camera retention rules, visitor logs, and daily cycle counts).

Happy to send over the PDF checklist free of charge if you'd like to review it with your store manager.

Let me know!

Best,
{sender_name}`
        },
        closing_offer: {
            subject: `72-Hour Compliance Package for {business_name}`,
            body: `Hi {name},

Hope you're having a great week at {business_name}.

We have two onboarding slots open this week for dispensaries in {state}. If you lock in your Complete SOP Package before Friday, we will include the Full Employee Training Manual and Metrc Reconciliation protocol at no extra charge ($500 value).

Everything delivered ready for inspector review in 72 hours.

Reserve your slot here: {calendly_link}

Best,
{sender_name}`
        }
    },

    currentTemplateKey: 'linkedin_connect',

    init() {
        this.setupTemplateTabs();
        this.setupVariablePills();
        this.setupDispatcher();
    },

    render(state) {
        const eligible = state.leads ? state.leads.filter(l => l.status === 'new') : [];
        const eligibleCountEl = document.getElementById('outreach-eligible-count');
        if (eligibleCountEl) eligibleCountEl.textContent = eligible.length;

        this.loadTemplate(this.currentTemplateKey);
    },

    setupTemplateTabs() {
        const tabs = document.querySelectorAll('#template-tabs .tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const key = tab.getAttribute('data-template');
                this.currentTemplateKey = key;
                this.loadTemplate(key);
            });
        });
    },

    loadTemplate(key) {
        const tpl = this.templates[key];
        if (!tpl) return;

        const subjInput = document.getElementById('template-subject');
        const subjLbl = document.getElementById('lbl-template-subject');
        const bodyText = document.getElementById('template-body');

        if (tpl.subject) {
            subjInput.style.display = 'block';
            subjLbl.style.display = 'block';
            subjInput.value = tpl.subject;
        } else {
            subjInput.style.display = 'none';
            subjLbl.style.display = 'none';
            subjInput.value = '';
        }

        bodyText.value = tpl.body;
        this.updateCharCount();
    },

    setupVariablePills() {
        const bodyText = document.getElementById('template-body');
        if (bodyText) {
            bodyText.addEventListener('input', () => this.updateCharCount());
        }

        window.insertVariable = (variableTag) => {
            const textarea = document.getElementById('template-body');
            if (!textarea) return;

            const startPos = textarea.selectionStart;
            const endPos = textarea.selectionEnd;
            const text = textarea.value;

            textarea.value = text.substring(0, startPos) + variableTag + text.substring(endPos);
            textarea.focus();
            textarea.selectionStart = textarea.selectionEnd = startPos + variableTag.length;
            this.updateCharCount();
        };

        const btnSave = document.getElementById('btn-save-template');
        if (btnSave) {
            btnSave.addEventListener('click', () => {
                const bodyText = document.getElementById('template-body').value;
                const subj = document.getElementById('template-subject').value;
                this.templates[this.currentTemplateKey].body = bodyText;
                this.templates[this.currentTemplateKey].subject = subj;
                App.toast("Template saved to local memory", "success");
            });
        }
    },

    updateCharCount() {
        const body = document.getElementById('template-body')?.value || '';
        const countEl = document.getElementById('template-char-count');
        if (countEl) countEl.textContent = `${body.length} characters (LinkedIn max connect: 300)`;
    },

    setupDispatcher() {
        const btnExecute = document.getElementById('btn-execute-outreach');
        const progressBox = document.getElementById('dispatch-progress-box');
        const logText = document.getElementById('dispatch-log-text');
        const fillBar = document.getElementById('dispatch-bar-fill');

        if (!btnExecute) return;

        btnExecute.addEventListener('click', async () => {
            const newLeads = App.state.leads.filter(l => l.status === 'new');
            if (newLeads.length === 0) {
                App.toast("No pending leads in 'New' stage. Extract more leads first!", "warning");
                return;
            }

            const batchChoice = document.getElementById('outreach-batch-size').value;
            const limit = batchChoice === 'all' ? newLeads.length : parseInt(batchChoice);
            const targetLeads = newLeads.slice(0, limit);
            const delay = parseInt(document.getElementById('outreach-delay').value) || 2;

            btnExecute.disabled = true;
            progressBox.style.display = 'block';
            fillBar.style.width = '0%';

            for (let i = 0; i < targetLeads.length; i++) {
                const lead = targetLeads[i];
                const pct = Math.round(((i + 1) / targetLeads.length) * 100);
                
                logText.textContent = `[${i + 1}/${targetLeads.length}] Dispatching personalized outreach to ${lead.owner_name} @ ${lead.business_name}...`;
                fillBar.style.width = `${pct}%`;

                // Simulated human pause
                await new Promise(r => setTimeout(r, delay * 350));
            }

            try {
                const res = await fetch('/api/outreach/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        lead_ids: targetLeads.map(l => l.id),
                        template_type: this.currentTemplateKey,
                        delay_seconds: delay
                    })
                });

                const result = await res.json();
                if (result.success) {
                    logText.textContent = `[COMPLETE] Successfully sent ${result.contacted} personalized messages! Expected responses: ~${Math.max(1, Math.round(result.contacted * 0.15))}`;
                    App.toast(`Dispatched outreach to ${result.contacted} dispensaries!`, 'success');
                    await App.refreshData();

                    setTimeout(() => {
                        progressBox.style.display = 'none';
                        btnExecute.disabled = false;
                    }, 4000);
                }
            } catch (err) {
                logText.textContent = `[ERROR] Outreach failed: ${err.message}`;
                btnExecute.disabled = false;
            }
        });
    }
};

window.OutreachView = OutreachView;
OutreachView.init();
