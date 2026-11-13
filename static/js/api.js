/**
 * ====================================================================
 * MediCare AI - Centralized API Service
 * File: static/js/api.js
 * ====================================================================
 */

const API_BASE = '/api';

const api = {
    // 1. Dashboard & Vitals
    async getDashboard() {
        const res = await fetch(`${API_BASE}/dashboard`);
        if (!res.ok) throw new Error("Failed to load dashboard data");
        return await res.json();
    },

    async updateVitals(data) {
        const res = await fetch(`${API_BASE}/vitals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Failed to record vitals");
        return await res.json();
    },

    // 2. Chatbot
    async sendChatMessage(message, sessionId, language = 'en') {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId, language })
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || "Failed to communicate with AI health assistant");
        }
        return await res.json();
    },

    async getChatHistory(sessionId) {
        const res = await fetch(`${API_BASE}/chat/history/${sessionId}`);
        if (!res.ok) return { messages: [] };
        return await res.json();
    },

    // 3. Symptom Checker
    async checkSymptoms(data) {
        const res = await fetch(`${API_BASE}/symptoms/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || "Failed to analyze symptoms");
        }
        return await res.json();
    },

    // 4. Doctors & Appointments
    async getDoctors(specialty = 'All') {
        let url = `${API_BASE}/doctors`;
        if (specialty && specialty !== 'All') {
            url += `?specialty=${encodeURIComponent(specialty)}`;
        }
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to load doctors");
        return await res.json();
    },

    async bookAppointment(data) {
        const res = await fetch(`${API_BASE}/appointments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || "Failed to schedule appointment");
        }
        return await res.json();
    },

    async getAppointments() {
        const res = await fetch(`${API_BASE}/appointments`);
        if (!res.ok) throw new Error("Failed to load appointments");
        return await res.json();
    },

    async cancelAppointment(appointmentId) {
        const res = await fetch(`${API_BASE}/appointments/${appointmentId}/cancel`, {
            method: 'POST'
        });
        if (!res.ok) throw new Error("Failed to cancel appointment");
        return await res.json();
    },

    // 5. Medicine Reminders
    async getMedicines() {
        const res = await fetch(`${API_BASE}/medicines`);
        if (!res.ok) throw new Error("Failed to load medicines");
        return await res.json();
    },

    async addMedicine(data) {
        const res = await fetch(`${API_BASE}/medicines`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || "Failed to save medicine reminder");
        }
        return await res.json();
    },

    async updateMedicineStatus(medicineId, status) {
        const res = await fetch(`${API_BASE}/medicines/${medicineId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (!res.ok) throw new Error("Failed to update status");
        return await res.json();
    },

    async deleteMedicine(medicineId) {
        const res = await fetch(`${API_BASE}/medicines/${medicineId}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error("Failed to delete reminder");
        return await res.json();
    },

    // 6. Health Awareness Articles
    async getArticles(category = 'All', lang = 'en') {
        let url = `${API_BASE}/articles?lang=${lang}`;
        if (category && category !== 'All') {
            url += `&category=${encodeURIComponent(category)}`;
        }
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to load articles");
        return await res.json();
    },

    async getArticle(articleId, lang = 'en') {
        const res = await fetch(`${API_BASE}/articles/${articleId}?lang=${lang}`);
        if (!res.ok) throw new Error("Failed to load article detail");
        return await res.json();
    },

    // 7. Emergency Contacts
    async getEmergency(lang = 'en') {
        const res = await fetch(`${API_BASE}/emergency?lang=${lang}`);
        if (!res.ok) throw new Error("Failed to load emergency contacts");
        return await res.json();
    }
};
