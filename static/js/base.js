(function() {
    'use strict';

    // ============ SIDEBAR TOGGLE ============
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
        });

        if (localStorage.getItem('sidebar_collapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }

        // Mobile sidebar toggle
        const mobileToggle = document.getElementById('mobileToggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', function() {
                sidebar.classList.toggle('mobile-show');
            });

            document.addEventListener('click', function(e) {
                if (window.innerWidth <= 992 &&
                    !sidebar.contains(e.target) &&
                    !mobileToggle.contains(e.target)) {
                    sidebar.classList.remove('mobile-show');
                }
            });
        }
    }

    // ============ THEME TOGGLE ============
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        updateThemeIcon(currentTheme);

        themeToggle.addEventListener('click', function() {
            const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const icon = themeToggle?.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
        }
    }

    // ============ GLOBAL SEARCH ============
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                const query = searchInput.value.trim();
                if (query.length >= 2) {
                    performGlobalSearch(query);
                }
            }, 400);
        });

        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = searchInput.value.trim();
                if (query) performGlobalSearch(query);
            }
        });
    }

    async function performGlobalSearch(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) return;
            const data = await response.json();
            showSearchResults(data, query);
        } catch (e) {
            console.error('Search error:', e);
        }
    }

    function showSearchResults(data, query) {
        const resultsDiv = document.getElementById('searchResults');
        if (!resultsDiv) return;
        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = `<div class="p-3 text-center text-muted"><small>No results for "${query}"</small></div>`;
            resultsDiv.style.display = 'block';
            return;
        }
        let html = '<div class="list-group list-group-flush">';
        data.results.forEach(function(r) {
            html += `<a href="${r.url}" class="list-group-item list-group-item-action d-flex align-items-center gap-3 py-2 px-3">
                <i class="${r.icon || 'bi bi-file-text'} text-primary"></i>
                <div><strong>${r.title}</strong><br><small class="text-muted">${r.subtitle || ''}</small></div>
            </a>`;
        });
        html += '</div>';
        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
    }

    document.addEventListener('click', function(e) {
        const resultsDiv = document.getElementById('searchResults');
        if (resultsDiv && !e.target.closest('.header-search')) {
            resultsDiv.style.display = 'none';
        }
    });

    // ============ NOTIFICATIONS ============
    async function loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (!response.ok) return;
            const data = await response.json();
            if (data.success && data.notifications) {
                updateNotificationBadge(data.notifications.length);
                renderNotifications(data.notifications);
            }
        } catch (e) {
            console.error('Failed to load notifications:', e);
        }
    }

    function updateNotificationBadge(count) {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
        const dot = document.querySelector('.notification-dot');
        if (dot) dot.style.display = count > 0 ? 'block' : 'none';
    }

    function renderNotifications(notifications) {
        const container = document.getElementById('notificationList');
        if (!container) return;
        if (notifications.length === 0) {
            container.innerHTML = '<div class="p-4 text-center text-muted"><i class="bi bi-bell-slash d-block mb-2" style="font-size:2rem"></i><small>No notifications</small></div>';
            return;
        }
        let html = '';
        notifications.slice(0, 10).forEach(function(n) {
            const timeAgo = getTimeAgo(new Date(n.created_at));
            const icons = {
                'low_stock': 'bi bi-exclamation-triangle text-warning',
                'expiry': 'bi bi-calendar-exclamation text-danger',
                'dispatch': 'bi bi-truck text-info',
                'incident': 'bi bi-lightning-charge text-danger',
                'request': 'bi bi-inbox text-primary',
                'default': 'bi bi-bell text-secondary'
            };
            const icon = icons[n.type] || icons.default;
            html += `<a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3" href="${n.url || '#'}">
                <i class="${icon} mt-1"></i>
                <div><strong>${n.title}</strong><br><small class="text-muted">${n.message}</small><br><small class="text-muted">${timeAgo}</small></div>
            </a>`;
        });
        container.innerHTML = html;
    }

    function getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        if (seconds < 60) return 'Just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return minutes + 'm ago';
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return hours + 'h ago';
        const days = Math.floor(hours / 24);
        return days + 'd ago';
    }

    const notifToggle = document.getElementById('notificationToggle');
    if (notifToggle) {
        notifToggle.addEventListener('click', function() {
            loadNotifications();
        });
    }

    // Load notifications on page load
    if (document.getElementById('notificationList')) {
        loadNotifications();
        setInterval(loadNotifications, 60000);
    }

    // ============ AUTO-HIDE FLASH MESSAGES ============
    document.querySelectorAll('.alert-dismissible').forEach(function(el) {
        setTimeout(function() {
            el.classList.remove('show');
            setTimeout(function() { el.remove(); }, 300);
        }, 5000);
    });

    // ============ TOAST NOTIFICATION HELPER ============
    window.showToast = function(type, message) {
        const icons = {
            success: 'bi-check-circle-fill text-success',
            danger: 'bi-x-circle-fill text-danger',
            warning: 'bi-exclamation-triangle-fill text-warning',
            info: 'bi-info-circle-fill text-info'
        };
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center border-0 show';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `<div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="${icons[type] || icons.info}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
        container.appendChild(toast);
        setTimeout(function() {
            toast.remove();
        }, 5000);
    };

})();
