/**
 * ====================================================================
 * MediCare AI - Emergency Services & First Aid Controller
 * File: static/js/emergency.js
 * ====================================================================
 */

class EmergencyController {
    constructor() {
        this.contactsGrid = document.getElementById('emergency-contacts-grid');
        this.firstAidTabBtns = document.querySelectorAll('.first-aid-tab-btn');
        this.firstAidContent = document.getElementById('first-aid-content');

        this.firstAidGuides = {
            cpr: {
                title: "Adult CPR (Cardiopulmonary Resuscitation)",
                steps: [
                    "Call 108 or 112 immediately and ask for an AED (defibrillator).",
                    "Place the heel of one hand in the center of the person's chest. Place your other hand on top and interlock fingers.",
                    "Position shoulders directly over hands with arms straight.",
                    "Push hard and fast: Compress at least 2 inches (5 cm) deep at a rate of 100 to 120 beats per minute (e.g. to the beat of 'Stayin' Alive').",
                    "Allow the chest to fully recoil between each compression.",
                    "Continue uninterrupted compressions until emergency medical personnel arrive or the person begins breathing normally."
                ]
            },
            choking: {
                title: "Choking Relief (Heimlich Maneuver)",
                steps: [
                    "Confirm the person is choking (inability to speak, cough, or breathe; clutching throat).",
                    "Stand behind the person and wrap your arms around their waist.",
                    "Make a fist with one hand and place the thumb side just above the person's navel, well below the breastbone.",
                    "Grasp your fist with your other hand and give quick, upward thrusts into the abdomen.",
                    "Repeat thrusts until the blocking object is dislodged or the person becomes unresponsive.",
                    "If the person becomes unresponsive, lower them to the floor and initiate CPR."
                ]
            },
            bleeding: {
                title: "Severe Bleeding Control",
                steps: [
                    "Ensure scene safety and put on gloves if available.",
                    "Apply firm, direct pressure on the wound using a clean cloth, sterile gauze, or clothing.",
                    "Do not remove the cloth if it soaks through; add more layers on top and maintain constant pressure.",
                    "Keep the injured person lying down and elevate the bleeding limb above the level of the heart if possible.",
                    "If bleeding from an arm or leg does not stop with direct pressure, apply an approved tourniquet 2-3 inches above the wound."
                ]
            },
            stroke: {
                title: "Stroke Recognition - FAST Protocol",
                steps: [
                    "F (FACE DROOPING): Ask the person to smile. Does one side of the face droop or feel numb?",
                    "A (ARM WEAKNESS): Ask the person to raise both arms. Does one arm drift downward?",
                    "S (SPEECH DIFFICULTY): Ask the person to repeat a simple sentence. Is speech slurred or strange?",
                    "T (TIME TO CALL 108): If the person displays ANY of these signs, even if they disappear, call 108 immediately and note the time symptoms started."
                ]
            }
        };

        this.init();
    }

    init() {
        this.firstAidTabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.firstAidTabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const topic = btn.getAttribute('data-topic') || 'cpr';
                this.renderFirstAidGuide(topic);
            });
        });

        this.loadEmergencyContacts();
        this.renderFirstAidGuide('cpr');
    }

    async loadEmergencyContacts() {
        if (!this.contactsGrid) return;
        this.contactsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">Loading emergency contacts...</div>`;

        try {
            const lang = window.currentLanguage || 'en';
            const data = await api.getEmergency(lang);
            this.renderEmergencyContacts(data.contacts || []);
        } catch (err) {
            this.contactsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--danger);">Failed to load contacts: ${err.message}</div>`;
        }
    }

    renderEmergencyContacts(contacts) {
        if (!contacts || contacts.length === 0) return;

        this.contactsGrid.innerHTML = contacts.map(c => `
            <div class="emergency-contact-card">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted);">
                            ${c.badge_type === 'critical' ? '🚨 Primary Helpline' : 'National Helpline'}
                        </span>
                        ${c.is_national ? '<span class="vital-badge normal">All-India 24/7</span>' : ''}
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; margin-top: 0.35rem; color: var(--text-primary);">
                        ${c.title}
                    </div>
                    <div class="emergency-number">${c.phone_number}</div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        ${c.description}
                    </p>
                </div>
                <div style="margin-top: 1rem;">
                    <a href="tel:${c.phone_number}" class="btn btn-primary" style="width: 100%; text-decoration: none; background: #dc2626;">
                        📞 Call ${c.phone_number} Now
                    </a>
                </div>
            </div>
        `).join('');
    }

    renderFirstAidGuide(topic) {
        if (!this.firstAidContent) return;
        const guide = this.firstAidGuides[topic] || this.firstAidGuides.cpr;

        this.firstAidContent.innerHTML = `
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">
                ${guide.title}
            </h3>
            <div style="display: flex; flex-direction: column;">
                ${guide.steps.map((step, idx) => `
                    <div class="first-aid-step">
                        <div class="step-num">${idx + 1}</div>
                        <div style="font-size: 0.95rem; line-height: 1.6; color: var(--text-secondary);">
                            ${step}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}
