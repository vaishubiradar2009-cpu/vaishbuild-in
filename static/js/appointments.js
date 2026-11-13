/**
 * ====================================================================
 * MediCare AI - Doctor Appointments Controller
 * File: static/js/appointments.js
 * ====================================================================
 */

class AppointmentsController {
    constructor() {
        this.doctorsGrid = document.getElementById('doctors-grid');
        this.filterContainer = document.getElementById('specialty-filters');
        this.bookingModal = document.getElementById('booking-modal');
        this.bookingForm = document.getElementById('booking-form');
        this.closeModalBtn = document.getElementById('modal-close-btn');
        this.cancelModalBtn = document.getElementById('modal-cancel-btn');
        this.selectedDoctor = null;
        this.currentSpecialty = 'All';

        this.init();
    }

    init() {
        // Filter pills click
        if (this.filterContainer) {
            this.filterContainer.addEventListener('click', (e) => {
                const pill = e.target.closest('.filter-pill');
                if (pill) {
                    this.filterContainer.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                    pill.classList.add('active');
                    this.currentSpecialty = pill.getAttribute('data-specialty') || 'All';
                    this.loadDoctors();
                }
            });
        }

        // Modal close listeners
        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeBookingModal());
        }
        if (this.cancelModalBtn) {
            this.cancelModalBtn.addEventListener('click', () => this.closeBookingModal());
        }

        // Booking form submit
        if (this.bookingForm) {
            this.bookingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitBooking();
            });
        }

        // Initial load
        this.loadDoctors();
    }

    async loadDoctors() {
        if (!this.doctorsGrid) return;
        this.doctorsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">Loading doctors...</div>`;

        try {
            const data = await api.getDoctors(this.currentSpecialty);
            this.renderDoctors(data.doctors || []);
        } catch (err) {
            this.doctorsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--danger);">Failed to load doctors: ${err.message}</div>`;
        }
    }

    renderDoctors(doctors) {
        if (!doctors || doctors.length === 0) {
            this.doctorsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">No doctors found for this medical specialty.</div>`;
            return;
        }

        const lang = window.currentLanguage || 'en';
        const t = translations[lang] || translations.en;

        this.doctorsGrid.innerHTML = doctors.map(doc => `
            <div class="doctor-card">
                <div class="doctor-header">
                    <img src="${doc.image_url || 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300&h=300&fit=crop'}" alt="${doc.name}" class="doctor-avatar">
                    <div class="doctor-meta">
                        <div class="doctor-name">${doc.name}</div>
                        <div class="doctor-specialty">${doc.specialty}</div>
                        <div class="doctor-hospital">${doc.hospital}, ${doc.city}</div>
                        <div style="margin-top: 0.3rem; display: flex; align-items: center; gap: 0.3rem; font-size: 0.8rem; font-weight: bold; color: #b45309;">
                            ★ ${doc.rating || 4.8} / 5.0
                        </div>
                    </div>
                </div>

                <div class="doctor-details">
                    <div>
                        <div class="doctor-info-row">
                            <span style="color: var(--text-muted);">${t.doctorExp}</span>
                            <span style="font-weight: 600;">${doc.experience_years} years</span>
                        </div>
                        <div class="doctor-info-row">
                            <span style="color: var(--text-muted);">Qualifications</span>
                            <span style="font-weight: 500; font-size: 0.8rem;">${doc.qualifications}</span>
                        </div>
                        <div class="doctor-info-row">
                            <span style="color: var(--text-muted);">Days Available</span>
                            <span style="font-weight: 600; color: var(--secondary);">${doc.available_days}</span>
                        </div>
                    </div>
                </div>

                <div class="doctor-footer">
                    <div>
                        <div style="font-size: 0.75rem; color: var(--text-muted);">${t.doctorFee}</div>
                        <div class="doctor-fee">₹${doc.consultation_fee}</div>
                    </div>
                    <button class="btn btn-primary" onclick="window.appointmentsController.openBookingModal('${doc.id}')" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
                        ${t.bookDoctorBtn}
                    </button>
                </div>
            </div>
        `).join('');
    }

    openBookingModal(doctorId) {
        // Fetch doctor info
        api.getDoctors('All').then(data => {
            const doc = data.doctors.find(d => d.id === doctorId);
            if (!doc) return;

            this.selectedDoctor = doc;
            const docSummary = document.getElementById('modal-doctor-summary');
            if (docSummary) {
                docSummary.innerHTML = `
                    <div style="display: flex; gap: 1rem; align-items: center; padding: 0.85rem; background: var(--primary-subtle); border-radius: var(--radius-md); border: 1px solid #bae6fd; margin-bottom: 1.25rem;">
                        <img src="${doc.image_url}" alt="${doc.name}" style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;">
                        <div>
                            <div style="font-weight: 700; color: var(--primary-dark);">${doc.name}</div>
                            <div style="font-size: 0.85rem; color: var(--secondary-dark); font-weight: 600;">${doc.specialty} • ${doc.hospital}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">Fee: ₹${doc.consultation_fee}</div>
                        </div>
                    </div>
                `;
            }

            // Populate slots
            const slotSelect = document.getElementById('modal-time-slot');
            if (slotSelect) {
                const slots = doc.available_time_slots.split(',').map(s => s.trim());
                slotSelect.innerHTML = slots.map(s => `<option value="${s}">${s}</option>`).join('');
            }

            // Set min date to today
            const dateInput = document.getElementById('modal-appt-date');
            if (dateInput) {
                const today = new Date().toISOString().split('T')[0];
                dateInput.min = today;
                dateInput.value = today;
            }

            this.bookingModal.classList.add('active');
        });
    }

    closeBookingModal() {
        if (this.bookingModal) {
            this.bookingModal.classList.remove('active');
        }
    }

    async submitBooking() {
        if (!this.selectedDoctor) return;

        const patientName = document.getElementById('modal-patient-name').value.trim();
        const patientPhone = document.getElementById('modal-patient-phone').value.trim();
        const patientEmail = document.getElementById('modal-patient-email').value.trim();
        const apptDate = document.getElementById('modal-appt-date').value;
        const timeSlot = document.getElementById('modal-time-slot').value;
        const reason = document.getElementById('modal-appt-reason').value.trim() || 'General Consultation';

        if (!patientName || !patientPhone || !apptDate || !timeSlot) {
            window.showToast("Please fill all required fields", "error");
            return;
        }

        try {
            await api.bookAppointment({
                doctor_id: this.selectedDoctor.id,
                patient_name: patientName,
                patient_phone: patientPhone,
                patient_email: patientEmail,
                appointment_date: apptDate,
                time_slot: timeSlot,
                reason: reason
            });

            this.closeBookingModal();
            window.showToast(`Consultation successfully booked with ${this.selectedDoctor.name}!`, "success");
            
            // Refresh dashboard
            if (window.appController) {
                window.appController.loadDashboard();
            }
        } catch (err) {
            window.showToast(err.message, "error");
        }
    }

    selectSpecialty(specialty) {
        this.currentSpecialty = specialty;
        if (this.filterContainer) {
            const pills = this.filterContainer.querySelectorAll('.filter-pill');
            pills.forEach(p => {
                if (p.getAttribute('data-specialty') === specialty) {
                    p.classList.add('active');
                } else {
                    p.classList.remove('active');
                }
            });
        }
        this.loadDoctors();
    }
}
