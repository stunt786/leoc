class Paginator {
    constructor(options) {
        this.currentPage = options.page || 1;
        this.perPage = options.perPage || 50;
        this.totalItems = options.totalItems || 0;
        this.totalPages = 0;
        this.paginationId = options.paginationId || 'pagination';
        this.infoId = options.infoId || 'tableInfo';
        this.maxVisible = options.maxVisible || 7;
        this.onPageChange = options.onPageChange || null;
        this._id = 'paginator_' + Math.random().toString(36).substr(2, 9);
        window[this._id] = this;
        this.update(this.totalItems);
    }

    update(totalItems) {
        this.totalItems = totalItems;
        this.totalPages = Math.ceil(totalItems / this.perPage) || 1;
        if (this.currentPage > this.totalPages) this.currentPage = 1;
        this.render();
    }

    getPageData(data) {
        const start = (this.currentPage - 1) * this.perPage;
        return data.slice(start, start + this.perPage);
    }

    goToPage(page) {
        if (page < 1 || page > this.totalPages || page === this.currentPage) return;
        this.currentPage = page;
        this.render();
        if (typeof this.onPageChange === 'function') this.onPageChange();
    }

    render() {
        const infoEl = document.getElementById(this.infoId);
        if (infoEl) {
            if (this.totalItems === 0) {
                infoEl.textContent = '0 records';
            } else {
                const start = (this.currentPage - 1) * this.perPage + 1;
                const end = Math.min(this.currentPage * this.perPage, this.totalItems);
                infoEl.textContent = `Showing ${start} - ${end} of ${this.totalItems} records`;
            }
        }

        const ul = document.getElementById(this.paginationId);
        if (!ul) return;
        if (this.totalPages <= 1) { ul.innerHTML = ''; return; }

        const paginatorId = this._id;
        let html = '';
        const prevPage = Math.max(1, this.currentPage - 1);
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="event.preventDefault();window['${paginatorId}'].goToPage(${prevPage})">&laquo;</a></li>`;

        const maxVis = this.maxVisible;
        let startPage, endPage;
        if (this.totalPages <= maxVis) {
            startPage = 1; endPage = this.totalPages;
        } else {
            const half = Math.floor(maxVis / 2);
            if (this.currentPage <= half + 1) {
                startPage = 1; endPage = maxVis;
            } else if (this.currentPage >= this.totalPages - half) {
                startPage = this.totalPages - maxVis + 1; endPage = this.totalPages;
            } else {
                startPage = this.currentPage - half; endPage = this.currentPage + half;
            }
        }

        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="event.preventDefault();window['${paginatorId}'].goToPage(1)">1</a></li>`;
            if (startPage > 2) html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === this.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="event.preventDefault();window['${paginatorId}'].goToPage(${i})">${i}</a></li>`;
        }

        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            html += `<li class="page-item"><a class="page-link" href="#" onclick="event.preventDefault();window['${paginatorId}'].goToPage(${this.totalPages})">${this.totalPages}</a></li>`;
        }

        const nextPage = Math.min(this.totalPages, this.currentPage + 1);
        html += `<li class="page-item ${this.currentPage === this.totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="event.preventDefault();window['${paginatorId}'].goToPage(${nextPage})">&raquo;</a></li>`;

        ul.innerHTML = html;
    }
}
