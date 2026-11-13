/**
 * ====================================================================
 * MediCare AI - Main Application Controller
 * File: static/js/app.js
 * ====================================================================
 */

window.currentLanguage = localStorage.getItem('medicare_language') || 'en';

// Global Toast System
window.showToast = function(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

class AppController {
    constructor() {
        this.navTabs = document.querySelectorAll('.nav-tab-btn');
        this.tabPanes = document.querySelectorAll('.tab-pane');
        this.langSelect = document.getElementById('language-select');
        this.vitalsModal = document.getElementById('vitals-modal');
        this.vitalsForm = document.getElementById('vitals-form');

        this.init();
    }

    init() {
        // Tab switching
        this.navTabs.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-tab');
                this.switchTab(targetTab);
            });
        });

        // Language toggle
        if (this.langSelect) {
            this.langSelect.value = window.currentLanguage;
            this.langSelect.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }

        // Vitals modal setup
        const openVitalsBtn = document.getElementById('open-vitals-modal-btn');
        const closeVitalsBtn = document.getElementById('close-vitals-modal-btn');
        const cancelVitalsBtn = document.getElementById('cancel-vitals-modal-btn');

        if (openVitalsBtn) openVitalsBtn.addEventListener('click', () => this.openVitalsModal());
        if (closeVitalsBtn) closeVitalsBtn.addEventListener('click', () => this.closeVitalsModal());
        if (cancelVitalsBtn) cancelVitalsBtn.addEventListener('click', () => this.closeVitalsModal());

        if (this.vitalsForm) {
            this.vitalsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitVitals();
            });
        }

        // Apply initial language
        this.applyLanguage();

        // Load dashboard
        this.loadDashboard();
    }

    switchTab(tabId) {
        this.navTabs.forEach(btn => {
            if (btn.getAttribute('data-tab') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        this.tabPanes.forEach(pane => {
            if (pane.id === `tab-${tabId}`) {
                pane.classList.add('active');
            } else {
                pane.classList.remove('active');
            }
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    navigateToAppointments(specialty = 'All') {
        this.switchTab('appointments');
        if (window.appointmentsController) {
            window.appointmentsController.selectSpecialty(specialty);
        }
    }

    setLanguage(lang) {
        if (!['en', 'hi', 'kn'].includes(lang)) lang = 'en';
        window.currentLanguage = lang;
        localStorage.setItem('medicare_language', lang);
        this.applyLanguage();

        // Refresh language-dependent controllers
        if (window.articlesController) window.articlesController.loadArticles();
        if (window.emergencyController) window.emergencyController.loadEmergencyContacts();
        if (window.chatbotController && window.chatbotController.messagesContainer.children.length <= 1) {
            window.chatbotController.clearChat();
        }

        const langName = lang === 'hi' ? 'हिंदी (Hindi)' : (lang === 'kn' ? 'ಕನ್ನಡ (Kannada)' : 'English');
        window.showToast(`Language switched to ${langName}`, "info");
    }

    applyLanguage() {
        const lang = window.currentLanguage || 'en';
        const dict = translations[lang] || translations.en;

        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = dict[key];
                } else {
                    el.innerText = dict[key];
                }
            }
        });
    }

    async loadDashboard() {
        try {
            const data = await api.getDashboard();
            this.renderDashboard(data);
        } catch (err) {
            console.error("Dashboard error:", err);
        }
    }

    renderDashboard(data) {
        const lang = window.currentLanguage || 'en';
        const t = translations[lang] || translations.en;

        // Vitals
        const vitals = data.vitals || {};
        const bpEl = document.getElementById('dash-vital-bp');
        const hrEl = document.getElementById('dash-vital-hr');
        const sugarEl = document.getElementById('dash-vital-sugar');
        const bmiEl = document.getElementById('dash-vital-bmi');

        if (bpEl) bpEl.innerText = `${vitals.blood_pressure_systolic || 120}/${vitals.blood_pressure_diastolic || 80} mmHg`;
        if (hrEl) hrEl.innerText = `${vitals.heart_rate || 72} bpm`;
        if (sugarEl) sugarEl.innerText = `${vitals.blood_sugar || 95} mg/dL`;
        
        if (bmiEl && vitals.weight_kg && vitals.height_cm) {
            const hMeters = vitals.height_cm / 100;
            const bmi = (vitals.weight_kg / (hMeters * hMeters)).toFixed(1);
            bmiEl.innerText = `${vitals.weight_kg} kg (BMI ${bmi})`;
        }

        // Compliance Card
        const compEl = document.getElementById('dash-compliance-value');
        if (compEl) {
            compEl.innerText = `${data.medication_compliance || 100}%`;
        }

        // Active Reminders Count
        const activeMedsEl = document.getElementById('dash-active-meds-count');
        if (activeMedsEl) {
            activeMedsEl.innerText = data.medicines_total_today || 0;
        }

        // Next Appointment
        const nextApptEl = document.getElementById('dash-next-appt-summary');
        if (nextApptEl) {
            const upcomings = data.upcoming_appointments || [];
            if (upcomings.length > 0) {
                const next = upcomings[0];
                nextApptEl.innerText = `${next.doctor_name || 'Specialist'} • ${next.appointment_date}`;
            } else {
                nextApptEl.innerText = t.noAppts;
            }
        }

        // Recent Symptom Check
        const recentSymptomEl = document.getElementById('dash-recent-symptom-summary');
        if (recentSymptomEl) {
            const syms = data.recent_symptoms || [];
            if (syms.length > 0) {
                const latest = syms[0];
                recentSymptomEl.innerText = `${latest.urgency_level} Priority • ${latest.recommended_specialty}`;
            } else {
                recentSymptomEl.innerText = "No recent checks recorded";
            }
        }

        // Render Dashboard Appointments List
        const apptContainer = document.getElementById('dash-upcoming-appts-list');
        if (apptContainer) {
            const upcomings = data.upcoming_appointments || [];
            if (upcomings.length === 0) {
                apptContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">${t.noAppts}</p>`;
            } else {
                apptContainer.innerHTML = upcomings.map(a => `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem; background: #f8fafc; border-radius: var(--radius-md); border: 1px solid var(--border); margin-bottom: 0.75rem;">
                        <div>
                            <div style="font-weight: 700; color: var(--text-primary);">${a.doctor_name || 'Specialist Consultation'}</div>
                            <div style="font-size: 0.825rem; color: var(--secondary-dark); font-weight: 600;">${a.doctor_specialty || 'General'} • ${a.doctor_hospital || 'Clinic'}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">📅 ${a.appointment_date} at ⏰ ${a.time_slot}</div>
                        </div>
                        <button class="btn btn-secondary" onclick="window.appController.cancelAppointment('${a.id}')" style="padding: 0.35rem 0.75rem; font-size: 0.75rem; color: var(--danger);">
                            Cancel
                        </button>
                    </div>
                `).join('');
            }
        }

        // Render Dashboard Today's Medicines
        const medsContainer = document.getElementById('dash-today-meds-list');
        if (medsContainer) {
            const meds = data.active_medicines || [];
            if (meds.length === 0) {
                medsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">${t.noMeds}</p>`;
            } else {
                medsContainer.innerHTML = meds.map(m => `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid #f1f5f9;">
                        <div>
                            <span style="font-weight: 700;">${m.medicine_name}</span> <span style="font-size: 0.8rem; color: var(--text-muted);">(${m.dosage})</span>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">⏰ ${m.reminder_time} • ${m.frequency}</div>
                        </div>
                        <span class="med-status-badge ${m.status_today || 'pending'}">
                            ${m.status_today === 'taken' ? '✓ Taken' : 'Pending'}
                        </span>
                    </div>
                `).join('');
            }
        }
    }

    async cancelAppointment(id) {
        if (!confirm("Are you sure you want to cancel this appointment?")) return;
        try {
            await api.cancelAppointment(id);
            window.showToast("Appointment cancelled", "info");
            this.loadDashboard();
        } catch (err) {
            window.showToast(err.message, "error");
        }
    }

    openVitalsModal() {
        if (this.vitalsModal) this.vitalsModal.classList.add('active');
    }

    closeVitalsModal() {
        if (this.vitalsModal) this.vitalsModal.classList.remove('active');
    }

    async submitVitals() {
        const bpSys = parseInt(document.getElementById('vital-input-sys').value) || 120;
        const bpDia = parseInt(document.getElementById('vital-input-dia').value) || 80;
        const hr = parseInt(document.getElementById('vital-input-hr').value) || 72;
        const sugar = parseFloat(document.getElementById('vital-input-sugar').value) || 95.0;
        const weight = parseFloat(document.getElementById('vital-input-weight').value) || 65.0;
        const height = parseFloat(document.getElementById('vital-input-height').value) || 165.0;

        try {
            await api.updateVitals({
                bp_systolic: bpSys,
                bp_diastolic: bpDia,
                heart_rate: hr,
                blood_sugar: sugar,
                weight_kg: weight,
                height_cm: height
            });

            this.closeVitalsModal();
            window.showToast("Personal health vitals updated successfully", "success");
            this.loadDashboard();
        } catch (err) {
            window.showToast(err.message, "error");
        }
    }
}

// Global bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.appController = new AppController();
    window.chatbotController = new ChatbotController();
    window.symptomCheckerController = new SymptomCheckerController();
    window.appointmentsController = new AppointmentsController();
    window.remindersController = new RemindersController();
    window.articlesController = new ArticlesController();
    window.emergencyController = new EmergencyController();
});
