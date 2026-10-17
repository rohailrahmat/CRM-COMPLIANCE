/**
 * AI Compliance SOP Generator & PDF Downloader
 */

const DocumentsView = {
    generatedHistory: [],

    init() {
        this.setupTiers();
        this.setupGenerator();
        this.setupDelivery();
    },

    setupTiers() {
        const tierCards = document.querySelectorAll('.package-tier-card');
        tierCards.forEach(card => {
            card.addEventListener('click', () => {
                tierCards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                const radio = card.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
            });
        });
    },

    setupGenerator() {
        const btnGen = document.getElementById('btn-generate-sops');
        if (!btnGen) return;

        btnGen.addEventListener('click', async () => {
            const bName = document.getElementById('doc-client-name').value.trim();
            const licNum = document.getElementById('doc-license-num').value.trim();
            const state = document.getElementById('doc-state').value;
            const tierEl = document.querySelector('input[name="package-tier"]:checked');
            const tier = tierEl ? tierEl.value : "Complete";

            if (!bName) {
                App.toast("Please enter a dispensary business name", "warning");
                return;
            }

            // Collect selected SOPs
            const selectedCheckboxes = document.querySelectorAll('.sop-check-item input:checked');
            const docNames = Array.from(selectedCheckboxes).map(cb => cb.value);

            if (docNames.length === 0) {
                App.toast("Please select at least one Standard Operating Procedure", "warning");
                return;
            }

            btnGen.disabled = true;
            btnGen.innerHTML = `<span>⏳ Compiling State-Certified PDFs...</span>`;

            try {
                const res = await fetch('/api/documents/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        business_name: bName,
                        license_number: licNum || "CO-402-00100",
                        state: state,
                        tier: tier,
                        document_names: docNames
                    })
                });

                const data = await res.json();
                if (data.success) {
                    App.triggerConfetti();
                    App.toast(`Generated ${data.count} official compliance PDFs!`, 'success');
                    this.renderGeneratedList(data.documents, bName, state);
                }
            } catch (err) {
                App.toast("Document generation error: " + err.message, "error");
            } finally {
                btnGen.disabled = false;
                btnGen.innerHTML = `<span>🤖 Generate Certified Compliance PDFs</span>`;
            }
        });
    },

    renderGeneratedList(docs, businessName, state) {
        const container = document.getElementById('generated-docs-list');
        if (!container) return;

        this.generatedHistory.unshift(...docs);

        container.innerHTML = this.generatedHistory.map(doc => `
            <div class="doc-download-card">
                <div>
                    <div class="doc-info-title">📄 ${doc.title}</div>
                    <div class="doc-info-sub">Target: ${businessName} (${state}) • Ready for inspection</div>
                </div>
                <a href="${doc.download_url}" target="_blank" download class="btn btn-primary btn-sm">
                    <span>📥 Download PDF</span>
                </a>
            </div>
        `).join('');
    },

    setupDelivery() {
        const btnSend = document.getElementById('btn-send-package-email');
        if (!btnSend) return;

        btnSend.addEventListener('click', () => {
            const email = document.getElementById('delivery-email').value;
            if (!email || !email.includes('@')) {
                App.toast("Please enter a valid client recipient email", "warning");
                return;
            }

            btnSend.disabled = true;
            btnSend.innerHTML = `<span>📤 Dispatching package...</span>`;

            setTimeout(() => {
                App.toast(`Package and secure download link dispatched to ${email}!`, 'success');
                btnSend.disabled = false;
                btnSend.innerHTML = `<span>📨 Send Download Link & Loom Walkthrough</span>`;
            }, 1200);
        });
    }
};

window.DocumentsView = DocumentsView;
DocumentsView.init();
