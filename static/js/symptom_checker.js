/**
 * ====================================================================
 * MediCare AI - Symptom Information Checker Controller
 * File: static/js/symptom_checker.js
 * ====================================================================
 */

class SymptomCheckerController {
    constructor() {
        this.form = document.getElementById('symptom-form');
        this.symptomsInput = document.getElementById('symptom-desc');
        this.durationSelect = document.getElementById('symptom-duration');
        this.severitySelect = document.getElementById('symptom-severity');
        this.ageGroupSelect = document.getElementById('symptom-age');
        this.submitBtn = document.getElementById('symptom-submit-btn');
        this.resultsCard = document.getElementById('symptom-results-container');
        this.loadingState = document.getElementById('symptom-loading');

        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.analyzeSymptoms();
            });
        }
    }

    async analyzeSymptoms() {
        const text = this.symptomsInput.value.trim();
        if (!text) {
            window.showToast("Please enter a description of your symptoms", "error");
            this.symptomsInput.focus();
            return;
        }

        const duration = this.durationSelect.value;
        const severity = this.severitySelect.value;
        const ageGroup = this.ageGroupSelect.value;
        const lang = window.currentLanguage || 'en';

        // Toggle UI loading
        this.submitBtn.disabled = true;
        this.loadingState.style.display = 'block';
        this.resultsCard.style.display = 'none';

        try {
            const data = await api.checkSymptoms({
                symptoms_text: text,
                duration: duration,
                severity: severity,
                age_group: ageGroup,
                language: lang
            });

            this.renderAssessmentResults(data);
            window.showToast("Symptom evaluation completed", "success");
        } catch (err) {
            window.showToast(err.message, "error");
        } finally {
            this.submitBtn.disabled = false;
            this.loadingState.style.display = 'none';
        }
    }

    renderAssessmentResults(data) {
        this.resultsCard.style.display = 'block';

        const urgency = (data.urgency_level || 'Low').toLowerCase();
        const urgencyClass = ['low', 'moderate', 'high', 'emergency'].includes(urgency) ? urgency : 'low';

        // Get language localized labels
        const lang = window.currentLanguage || 'en';
        const t = translations[lang] || translations.en;

        const specialty = data.recommended_specialty || "General Medicine";

        let html = `
            <div class="card-header" style="border-radius: var(--radius-lg) var(--radius-lg) 0 0;">
                <div class="card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    ${t.symptomResultsTitle}
                </div>
                <span class="urgency-badge ${urgencyClass}">
                    ● ${t.urgencyTitle}: ${data.urgency_level}
                </span>
            </div>

            <div class="card-body">
                <p style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.25rem;">
                    ${data.summary_explanation || ''}
                </p>

                <div class="vital-tile" style="margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; text-align: left; background: var(--secondary-subtle); border-color: var(--secondary-light);">
                    <div>
                        <div style="font-size: 0.8rem; font-weight: bold; color: var(--secondary-dark); text-transform: uppercase;">
                            ${t.recommendedDoctor}
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-primary); margin-top: 0.2rem;">
                            ${specialty}
                        </div>
                    </div>
                    <button class="btn btn-teal" onclick="window.appController.navigateToAppointments('${specialty}')" style="padding: 0.5rem 1rem; font-size: 0.85rem;">
                        ${t.bookRecommendedDoctor} &rarr;
                    </button>
                </div>

                <div class="assessment-section">
                    <div class="assessment-section-title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                        ${t.possibleConsiderations}
                    </div>
                    <ul class="assessment-list">
                        ${(data.potential_considerations || []).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>

                <div class="assessment-section">
                    <div class="assessment-section-title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--secondary)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        ${t.homeCareTitle}
                    </div>
                    <ul class="assessment-list">
                        ${(data.home_care_measures || []).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>

                <div class="assessment-section">
                    <div class="assessment-section-title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                        ${t.questionsDoctorTitle}
                    </div>
                    <ul class="assessment-list">
                        ${(data.questions_for_doctor || []).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>

                ${data.red_flags && data.red_flags.length > 0 ? `
                <div class="assessment-section" style="background: #fff5f5; border: 1px solid #fecaca; border-radius: var(--radius-md); padding: 1rem; margin-top: 1.25rem;">
                    <div class="assessment-section-title" style="color: var(--danger);">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                        ${t.redFlagsTitle}
                    </div>
                    <ul class="assessment-list" style="margin-bottom: 0;">
                        ${data.red_flags.map(item => `<li style="color: #991b1b;">${item}</li>`).join('')}
                    </ul>
                </div>` : ''}

                <div style="margin-top: 1.5rem; padding: 0.85rem; background: #f8fafc; border-radius: var(--radius-md); border: 1px solid var(--border); font-size: 0.78rem; color: var(--text-muted); line-height: 1.5;">
                    ${data.disclaimer || t.chatDisclaimer}
                </div>
            </div>
        `;

        this.resultsCard.innerHTML = html;
        this.resultsCard.scrollIntoView({ behavior: 'smooth' });
    }
}
