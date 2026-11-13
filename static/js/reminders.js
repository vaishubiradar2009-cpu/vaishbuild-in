/**
 * ====================================================================
 * MediCare AI - Medicine Reminders Controller
 * File: static/js/reminders.js
 * ====================================================================
 */

class RemindersController {
    constructor() {
        this.medicineList = document.getElementById('medicine-reminders-list');
        this.addMedModal = document.getElementById('add-medicine-modal');
        this.openAddBtn = document.getElementById('open-add-med-btn');
        this.closeAddBtn = document.getElementById('close-med-modal-btn');
        this.cancelAddBtn = document.getElementById('cancel-med-modal-btn');
        this.medForm = document.getElementById('add-medicine-form');

        this.init();
    }

    init() {
        if (this.openAddBtn) {
            this.openAddBtn.addEventListener('click', () => this.openModal());
        }
        if (this.closeAddBtn) {
            this.closeAddBtn.addEventListener('click', () => this.closeModal());
        }
        if (this.cancelAddBtn) {
            this.cancelAddBtn.addEventListener('click', () => this.closeModal());
        }
        if (this.medForm) {
            this.medForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitAddMedicine();
            });
        }

        this.loadMedicines();
    }

    async loadMedicines() {
        if (!this.medicineList) return;
        this.medicineList.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading medicine schedule...</div>`;

        try {
            const data = await api.getMedicines();
            this.renderMedicines(data.medicines || []);
        } catch (err) {
            this.medicineList.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--danger);">Failed to load reminders: ${err.message}</div>`;
        }
    }

    renderMedicines(medicines) {
        if (!medicines || medicines.length === 0) {
            const lang = window.currentLanguage || 'en';
            const t = translations[lang] || translations.en;
            this.medicineList.innerHTML = `
                <div style="text-align: center; padding: 3rem 1rem; background: white; border: 1px dashed var(--border); border-radius: var(--radius-lg);">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-light)" stroke-width="1.5" style="margin-bottom: 0.75rem;"><path d="M10.5 20.5l10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"></path><line x1="8.5" y1="8.5" x2="15.5" y2="15.5"></line></svg>
                    <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 0.25rem;">${t.noMeds}</div>
                    <button class="btn btn-teal" onclick="window.remindersController.openModal()" style="margin-top: 0.75rem; font-size: 0.85rem; padding: 0.45rem 1rem;">
                        ${t.addMedBtn}
                    </button>
                </div>
            `;
            return;
        }

        const lang = window.currentLanguage || 'en';
        const t = translations[lang] || translations.en;

        this.medicineList.innerHTML = medicines.map(med => {
            const status = med.status_today || 'pending';
            const statusLabel = status === 'taken' ? t.markTaken : (status === 'skipped' ? t.markSkip : 'Pending');

            return `
                <div class="medicine-item">
                    <div class="med-info">
                        <div class="med-icon">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.5 20.5l10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"></path><line x1="8.5" y1="8.5" x2="15.5" y2="15.5"></line></svg>
                        </div>
                        <div>
                            <div class="med-title">${med.medicine_name} <span style="font-weight: 500; font-size: 0.85rem; color: var(--text-muted);">${med.dosage}</span></div>
                            <div class="med-timing">
                                ⏰ <strong>${med.reminder_time}</strong> • ${med.frequency} • <span style="text-transform: capitalize;">${(med.timing_relation || '').replace('_', ' ')}</span>
                            </div>
                            ${med.notes ? `<div style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.2rem;">Note: ${med.notes}</div>` : ''}
                        </div>
                    </div>

                    <div class="med-actions">
                        <span class="med-status-badge ${status}">
                            ${statusLabel}
                        </span>

                        ${status !== 'taken' ? `
                            <button class="btn btn-primary" onclick="window.remindersController.updateStatus('${med.id}', 'taken')" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">
                                ✓ ${t.markTaken}
                            </button>
                        ` : ''}

                        ${status === 'pending' ? `
                            <button class="btn btn-secondary" onclick="window.remindersController.updateStatus('${med.id}', 'skipped')" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">
                                ${t.markSkip}
                            </button>
                        ` : ''}

                        <button class="btn btn-secondary" onclick="window.remindersController.deleteMed('${med.id}')" title="Delete reminder" style="padding: 0.4rem 0.6rem; color: var(--danger); border-color: transparent;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    async updateStatus(id, newStatus) {
        try {
            await api.updateMedicineStatus(id, newStatus);
            window.showToast(`Medicine marked as ${newStatus}`, "success");
            this.loadMedicines();
            if (window.appController) window.appController.loadDashboard();
        } catch (err) {
            window.showToast(err.message, "error");
        }
    }

    async deleteMed(id) {
        if (!confirm("Are you sure you want to remove this medication reminder?")) return;
        try {
            await api.deleteMedicine(id);
            window.showToast("Medication reminder removed", "info");
            this.loadMedicines();
            if (window.appController) window.appController.loadDashboard();
        } catch (err) {
            window.showToast(err.message, "error");
        }
    }

    openModal() {
        if (this.addMedModal) this.addMedModal.classList.add('active');
    }

    closeModal() {
        if (this.addMedModal) this.addMedModal.classList.remove('active');
    }

    async submitAddMedicine() {
        const name = document.getElementById('new-med-name').value.trim();
        const dosage = document.getElementById('new-med-dosage').value.trim();
        const frequency = document.getElementById('new-med-freq').value;
        const time = document.getElementById('new-med-time').value;
        const relation = document.getElementById('new-med-relation').value;
        const notes = document.getElementById('new-med-notes').value.trim();

        if (!name || !dosage) {
            window.showToast("Please provide medicine name and dosage", "error");
            return;
        }

        try {
            await api.addMedicine({
                medicine_name: name,
                dosage: dosage,
                frequency: frequency,
                reminder_time: time,
                timing_relation: relation,
                notes: notes
            });

            this.closeModal();
            this.medForm.reset();
            window.showToast("Medicine reminder added successfully", "success");
            this.loadMedicines();
            if (window.appController) window.appController.loadDashboard();
        } catch (err) {
            window.showToast(err.message, "error");
        }
    }
}
