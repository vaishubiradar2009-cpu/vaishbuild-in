/**
 * ====================================================================
 * MediCare AI - Health Awareness Articles Controller
 * File: static/js/articles.js
 * ====================================================================
 */

class ArticlesController {
    constructor() {
        this.articlesGrid = document.getElementById('articles-grid');
        this.categoryPills = document.getElementById('article-categories');
        this.searchInput = document.getElementById('article-search-input');
        this.articleModal = document.getElementById('article-detail-modal');
        this.modalClose = document.getElementById('article-modal-close');
        this.modalBody = document.getElementById('article-modal-body');
        
        this.currentCategory = 'All';
        this.articlesData = [];

        this.init();
    }

    init() {
        if (this.categoryPills) {
            this.categoryPills.addEventListener('click', (e) => {
                const pill = e.target.closest('.filter-pill');
                if (pill) {
                    this.categoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                    pill.classList.add('active');
                    this.currentCategory = pill.getAttribute('data-category') || 'All';
                    this.loadArticles();
                }
            });
        }

        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => this.filterArticlesLocally());
        }

        if (this.modalClose) {
            this.modalClose.addEventListener('click', () => this.closeModal());
        }

        this.loadArticles();
    }

    async loadArticles() {
        if (!this.articlesGrid) return;
        this.articlesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">Loading health articles...</div>`;

        try {
            const lang = window.currentLanguage || 'en';
            const data = await api.getArticles(this.currentCategory, lang);
            this.articlesData = data.articles || [];
            this.renderArticles(this.articlesData);
        } catch (err) {
            this.articlesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--danger);">Failed to load articles: ${err.message}</div>`;
        }
    }

    filterArticlesLocally() {
        const query = this.searchInput.value.toLowerCase().trim();
        if (!query) {
            this.renderArticles(this.articlesData);
            return;
        }

        const filtered = this.articlesData.filter(a => 
            (a.title && a.title.toLowerCase().includes(query)) ||
            (a.summary && a.summary.toLowerCase().includes(query)) ||
            (a.category && a.category.toLowerCase().includes(query))
        );
        this.renderArticles(filtered);
    }

    renderArticles(articles) {
        if (!articles || articles.length === 0) {
            this.articlesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">No health articles found matching your criteria.</div>`;
            return;
        }

        const lang = window.currentLanguage || 'en';
        const t = translations[lang] || translations.en;

        this.articlesGrid.innerHTML = articles.map(art => `
            <div class="article-card">
                <img src="${art.image_url || 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&h=350&fit=crop'}" alt="${art.title}" class="article-img">
                <div class="article-body">
                    <div class="article-category">${art.category}</div>
                    <div class="article-title">${art.title}</div>
                    <div class="article-summary">${art.summary}</div>
                    <div class="article-footer">
                        <span>🕒 ${art.read_time_minutes || 4} ${t.readTime}</span>
                        <button class="btn btn-secondary" onclick="window.articlesController.openArticleModal('${art.id}')" style="padding: 0.35rem 0.85rem; font-size: 0.8rem;">
                            ${t.readMore} &rarr;
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async openArticleModal(articleId) {
        try {
            const lang = window.currentLanguage || 'en';
            const data = await api.getArticle(articleId, lang);
            const art = data.article;
            if (!art) return;

            const modalTitle = document.getElementById('article-modal-title');
            if (modalTitle) modalTitle.innerText = art.title;

            if (this.modalBody) {
                // Format article content with paragraphs
                const formattedContent = art.content
                    .split('\n\n')
                    .map(para => `<p style="margin-bottom: 1rem; line-height: 1.7; color: var(--text-secondary);">${para.replace(/\n/g, '<br>')}</p>`)
                    .join('');

                this.modalBody.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <span class="vital-badge normal">${art.category}</span>
                        <span style="font-size: 0.85rem; color: var(--text-muted); margin-left: 0.75rem;">By ${art.author}</span>
                    </div>
                    <img src="${art.image_url}" alt="${art.title}" style="width: 100%; height: 240px; object-fit: cover; border-radius: var(--radius-md); margin-bottom: 1.25rem;">
                    <div style="font-size: 0.95rem;">
                        ${formattedContent}
                    </div>
                `;
            }

            if (this.articleModal) this.articleModal.classList.add('active');
        } catch (err) {
            window.showToast("Could not load article detail", "error");
        }
    }

    closeModal() {
        if (this.articleModal) this.articleModal.classList.remove('active');
    }
}
