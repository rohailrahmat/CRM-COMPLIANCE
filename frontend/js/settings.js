/**
 * System Settings & Data Operations Controller
 */

const SettingsView = {
    init() {
        this.setupForm();
        this.setupDatabaseOperations();
    },

    render(settings) {
        if (!settings) return;
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el && val !== undefined) el.value = val;
        };

        setVal('set-specialist-name', settings.specialist_name);
        setVal('set-business-brand', settings.business_brand);
        setVal('set-specialist-email', settings.specialist_email);
        setVal('set-specialist-phone', settings.specialist_phone);
        setVal('set-calendly-link', settings.calendly_link);
        setVal('set-wise-account', settings.wise_account);
    },

    setupForm() {
        const form = document.getElementById('form-settings');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                specialist_name: document.getElementById('set-specialist-name').value,
                business_brand: document.getElementById('set-business-brand').value,
                specialist_email: document.getElementById('set-specialist-email').value,
                specialist_phone: document.getElementById('set-specialist-phone').value,
                calendly_link: document.getElementById('set-calendly-link').value,
                wise_account: document.getElementById('set-wise-account').value
            };

            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (result.success) {
                    App.toast("Branding settings saved successfully", "success");
                    App.refreshData();
                }
            } catch (err) {
                App.toast("Failed to update settings", "error");
            }
        });
    },

    setupDatabaseOperations() {
        const btnReset = document.getElementById('btn-reset-db');
        const btnBackup = document.getElementById('btn-backup-data');
        const btnWipe = document.getElementById('btn-wipe-leads');

        if (btnReset) {
            btnReset.addEventListener('click', async () => {
                if (!confirm("Reset database to clean verified demo dataset with 14 active dispensaries?")) return;
                try {
                    const res = await fetch('/api/database/reset', { method: 'POST' });
                    const result = await res.json();
                    if (result.success) {
                        App.toast("Database reset to verified demo dataset!", "success");
                        App.refreshData();
                    }
                } catch (err) {
                    App.toast("Failed to reset database", "error");
                }
            });
        }

        if (btnBackup) {
            btnBackup.addEventListener('click', () => {
                const backupData = {
                    version: "2.0.0",
                    timestamp: new Date().toISOString(),
                    stats: App.state.stats,
                    leads: App.state.leads,
                    activities: App.state.activities,
                    settings: App.state.settings
                };

                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(backupData, null, 2));
                const link = document.createElement("a");
                link.setAttribute("href", dataStr);
                link.setAttribute("download", `cannabis_crm_backup_${new Date().toISOString().slice(0, 10)}.json`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                App.toast("Backup JSON downloaded", "success");
            });
        }

        if (btnWipe) {
            btnWipe.addEventListener('click', async () => {
                if (!confirm("⚠️ WARNING: This will permanently delete all leads and activity records from the database. Proceed?")) return;
                
                try {
                    for (const lead of App.state.leads) {
                        await fetch(`/api/leads/${lead.id}`, { method: 'DELETE' });
                    }
                    App.toast("All contacts wiped from database", "warning");
                    App.refreshData();
                } catch (err) {
                    App.toast("Error wiping database", "error");
                }
            });
        }
    }
};

window.SettingsView = SettingsView;
SettingsView.init();
