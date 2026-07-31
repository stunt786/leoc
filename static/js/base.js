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

    // ============ COLLAPSIBLE SUB-MENUS ============
    document.querySelectorAll('.nav-parent').forEach(function(parent) {
        parent.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-target');
            const subMenu = document.getElementById(targetId);
            if (subMenu) {
                this.classList.toggle('open');
                subMenu.classList.toggle('open');
            }
        });
    });

    // Auto-expand section containing active sub-item
    document.querySelectorAll('.sub-menu').forEach(function(sub) {
        if (sub.querySelector('.nav-item.active')) {
            const parent = sub.closest('.nav-section')?.querySelector('.nav-parent');
            if (parent) {
                parent.classList.add('open');
                sub.classList.add('open');
            }
        }
    });

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
    const HIGH_ALERT_PRIORITIES = new Set(['High', 'Urgent']);
    const NOTIFICATION_ICONS = {
        stock_receipt: 'bi-clipboard-check-fill text-primary',
        stock_transfer: 'bi-arrow-left-right text-info',
        adjustment: 'bi-sliders text-warning',
        low_stock: 'bi-exclamation-triangle-fill text-warning',
        expiry: 'bi-calendar-exclamation-fill text-danger',
        incident: 'bi-lightning-charge-fill text-danger',
        relief_request: 'bi-send-fill text-primary',
        dispatch: 'bi-truck-front-fill text-info',
        distribution: 'bi-people-fill text-success',
        cash_receipt: 'bi-cash-coin text-success',
        cash_request: 'bi-send-exclamation-fill text-warning',
        cash_distribution: 'bi-cash-stack text-danger',
        default: 'bi-bell-fill text-secondary'
    };

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatNotificationTime(dateValue) {
        const date = new Date(dateValue);
        if (Number.isNaN(date.getTime())) return '';
        try {
            return new Intl.DateTimeFormat('en-GB', {
                timeZone: 'Asia/Kathmandu',
                dateStyle: 'medium',
                timeStyle: 'short',
            }).format(date);
        } catch (e) {
            return date.toLocaleString();
        }
    }

    function getNotificationIcon(notification) {
        return NOTIFICATION_ICONS[notification.type] || NOTIFICATION_ICONS.default;
    }

    function getNotificationGroup(notification) {
        const type = notification.type || '';
        if (['low_stock', 'expiry'].includes(type)) return 'Inventory';
        if (['cash_receipt', 'cash_request', 'cash_distribution'].includes(type)) return 'Finance';
        if (['incident', 'relief_request'].includes(type)) return 'Incidents';
        return 'System';
    }

    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    async function clearNotification(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/clear`, {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()},
            });
            if (!response.ok) return false;
            const data = await response.json();
            return !!(data && data.success);
        } catch (e) {
            console.error('Failed to clear notification:', e);
            return false;
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
        const clearBtn = document.getElementById('clearAllNotifications');
        if (clearBtn) clearBtn.style.display = count > 0 ? 'inline-block' : 'none';
    }

    function renderHighAlerts(notifications) {
        const container = document.getElementById('highAlertContainer');
        if (!container) return;
        const alerts = notifications.filter(function(n) {
            return !n.cleared && HIGH_ALERT_PRIORITIES.has(n.priority);
        });
        if (alerts.length === 0) {
            container.innerHTML = '';
            return;
        }
        container.innerHTML = alerts.map(function(notification) {
            const icon = getNotificationIcon(notification);
            const timeLabel = notification.created_at_formatted || formatNotificationTime(notification.created_at);
            return `
                <div class="high-alert-card" data-notification-id="${notification.id}">
                    <button type="button" class="high-alert-close" aria-label="Dismiss notification" data-notification-id="${notification.id}">
                        <i class="bi bi-x-lg"></i>
                    </button>
                    <div class="high-alert-icon"><i class="bi ${icon}"></i></div>
                    <div class="high-alert-body">
                        <div class="high-alert-top">
                            <div>
                                <div class="high-alert-title">${escapeHtml(notification.title)}</div>
                                <div class="high-alert-meta">${escapeHtml(notification.priority)} alert · ${escapeHtml(getNotificationGroup(notification))}</div>
                            </div>
                            <span class="high-alert-badge">${escapeHtml(notification.type || 'alert')}</span>
                        </div>
                        <div class="high-alert-message">${escapeHtml(notification.message)}</div>
                        <div class="high-alert-footer">
                            <small>${escapeHtml(timeLabel)}</small>
                            ${notification.url ? `<a href="${notification.url}" class="high-alert-link">Open</a>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.high-alert-close').forEach(function(button) {
            button.addEventListener('click', async function() {
                const notificationId = this.getAttribute('data-notification-id');
                const card = this.closest('.high-alert-card');
                if (card) {
                    card.classList.add('is-dismissing');
                }
                const cleared = await clearNotification(notificationId);
                if (cleared && card) {
                    setTimeout(function() {
                        card.remove();
                    }, 220);
                }
                if (!cleared && card) {
                    card.classList.remove('is-dismissing');
                }
            });
        });
    }

    function renderNotifications(notifications) {
        const container = document.getElementById('notificationList');
        if (!container) {
            renderHighAlerts(notifications);
            return;
        }
        const activeNotifications = notifications.filter(function(notification) {
            return !notification.cleared;
        });
        updateNotificationBadge(activeNotifications.length);
        renderHighAlerts(activeNotifications);
        if (activeNotifications.length === 0) {
            container.innerHTML = '<div class="p-4 text-center text-muted"><i class="bi bi-bell-slash d-block mb-2" style="font-size:2rem"></i><small>No notifications</small></div>';
            return;
        }
        let html = '';
        activeNotifications.slice(0, 10).forEach(function(notification) {
            const icon = getNotificationIcon(notification);
            const timeLabel = notification.created_at_formatted || formatNotificationTime(notification.created_at);
            html += `
                <a class="dropdown-item notification-item d-flex align-items-start gap-3 py-3 px-3" href="${notification.url || '#'}">
                    <div class="notification-item-icon">
                        <i class="bi ${icon}"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start gap-2">
                            <strong>${escapeHtml(notification.title)}</strong>
                            <span class="notification-pill">${escapeHtml(notification.priority || 'Medium')}</span>
                        </div>
                        <div class="small text-muted mt-1">${escapeHtml(notification.message)}</div>
                        <div class="small text-muted mt-1">${escapeHtml(timeLabel)}</div>
                    </div>
                </a>
            `;
        });
        container.innerHTML = html;
    }

    async function loadNotifications() {
        try {
            const response = await fetch('/api/notifications?include_cleared=0', { cache: 'no-cache' });
            if (!response.ok) return;
            const data = await response.json();
            if (data.success && data.notifications) {
                renderNotifications(data.notifications);
            }
        } catch (e) {
            console.error('Failed to load notifications:', e);
        }
    }

    async function clearAllNotifications() {
        try {
            const response = await fetch('/api/notifications/clear', {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()},
            });
            if (!response.ok) return;
            const data = await response.json();
            if (data && data.success) {
                const container = document.getElementById('notificationList');
                if (container) {
                    container.innerHTML = '<div class="p-4 text-center text-muted"><i class="bi bi-bell-slash d-block mb-2" style="font-size:2rem"></i><small>No notifications</small></div>';
                }
                const alertContainer = document.getElementById('highAlertContainer');
                if (alertContainer) alertContainer.innerHTML = '';
                updateNotificationBadge(0);
            }
        } catch (e) {
            console.error('Failed to clear all notifications:', e);
        }
    }

    const clearAllBtn = document.getElementById('clearAllNotifications');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            clearAllNotifications();
        });
    }

    const notifToggle = document.getElementById('notificationToggle');
    if (notifToggle) {
        notifToggle.addEventListener('click', function() {
            loadNotifications();
        });
    }

    // Load notifications on page load
    if (document.getElementById('notificationList') || document.getElementById('highAlertContainer')) {
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
