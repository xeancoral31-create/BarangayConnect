/* BarangayConnect — Institutional Client Script */
document.addEventListener('DOMContentLoaded', function () {

    // ─── Philippine Standard Time (PST / UTC+8) Live Clock ─────────────────
    // Mandated in Philippine Government portals under Republic Act No. 10535
    function initPSTClock() {
        const topbars = document.querySelectorAll('.topbar');
        topbars.forEach(function (topbar) {
            if (!topbar.querySelector('.topbar-pst')) {
                const actionsContainer = topbar.querySelector('.topbar-actions') || topbar.querySelector('.topbar-right');
                const pstContainer = document.createElement('div');
                pstContainer.className = 'topbar-pst d-none d-lg-flex align-items-center me-3';
                pstContainer.innerHTML = `
                    <span class="pst-badge"><i class="bi bi-clock-history me-1"></i>PST</span>
                    <span class="pst-clock-display ms-2"></span>
                `;
                if (actionsContainer) {
                    topbar.insertBefore(pstContainer, actionsContainer);
                } else {
                    topbar.appendChild(pstContainer);
                }
            }
        });

        function updateClock() {
            const now = new Date();
            const options = {
                timeZone: 'Asia/Manila',
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            };

            let datePart = '';
            let timePart = '';

            try {
                const formatter = new Intl.DateTimeFormat('en-PH', options);
                const parts = formatter.formatToParts(now);
                const weekday = parts.find(p => p.type === 'weekday')?.value || '';
                const month = parts.find(p => p.type === 'month')?.value || '';
                const day = parts.find(p => p.type === 'day')?.value || '';
                const year = parts.find(p => p.type === 'year')?.value || '';
                const hour = parts.find(p => p.type === 'hour')?.value || '';
                const minute = parts.find(p => p.type === 'minute')?.value || '';
                const second = parts.find(p => p.type === 'second')?.value || '';
                const dayPeriod = parts.find(p => p.type === 'dayPeriod')?.value?.toUpperCase() || '';

                datePart = `${weekday}, ${month} ${day}, ${year}`;
                timePart = `${hour}:${minute}:${second} ${dayPeriod}`;
            } catch (e) {
                datePart = now.toDateString();
                timePart = now.toLocaleTimeString();
            }

            const displays = document.querySelectorAll('.pst-clock-display, #pstClock');
            displays.forEach(function (el) {
                el.innerHTML = `<span>${datePart}</span> <span class="mx-1 opacity-50">•</span> <strong>${timePart}</strong> <span class="pst-zone ms-1">(UTC+8)</span>`;
            });
        }

        updateClock();
        setInterval(updateClock, 1000);
    }

    initPSTClock();

    // ─── Sidebar Toggle & Collapsed State ────────────────────────────────
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent') || document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const topbar = document.querySelector('.topbar');
    
    // Create overlay for mobile drawer
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            const isMobile = window.innerWidth <= 992;
            if (isMobile) {
                sidebar.classList.toggle('show');
                overlay.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                if (mainContent) mainContent.classList.toggle('collapsed');
                if (topbar) topbar.classList.toggle('collapsed');
                document.body.classList.toggle('has-collapsed-sidebar');
                
                const isCollapsed = sidebar.classList.contains('collapsed');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            }
        });

        overlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });

        // Restore sidebar state on desktop
        if (window.innerWidth > 992) {
            const wasCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            if (wasCollapsed) {
                sidebar.classList.add('collapsed');
                if (mainContent) mainContent.classList.add('collapsed');
                if (topbar) topbar.classList.add('collapsed');
                document.body.classList.add('has-collapsed-sidebar');
            }
        }
    }

    // ─── Auto-dismiss Bootstrap Toasts ────────────────────────────────────
    const toastEls = document.querySelectorAll('.toast');
    toastEls.forEach(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', function () {
            toastEl.remove();
        });
    });

    // ─── Confirm Action Dialogs ──────────────────────────────────────────
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // ─── Image / File Input Preview ──────────────────────────────────────
    document.querySelectorAll('input[type="file"][data-preview]').forEach(function (input) {
        input.addEventListener('change', function () {
            const previewId = input.dataset.preview;
            const preview = document.getElementById(previewId);
            if (preview && input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) { preview.src = e.target.result; };
                reader.readAsDataURL(input.files[0]);
            }
        });
    });

    // ─── Search Auto-Submit on Select Filter Change ───────────────────────
    document.querySelectorAll('[data-auto-submit]').forEach(function (el) {
        el.addEventListener('change', function () {
            el.closest('form').submit();
        });
    });

    // ─── Active Nav Highlight Fallback ───────────────────────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath === href) {
            link.classList.add('active');
        }
    });

    // ─── Password Visibility Toggle Support ──────────────────────────────
    document.querySelectorAll('[data-toggle-password]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const targetId = btn.dataset.togglePassword;
            const input = document.getElementById(targetId);
            const icon = btn.querySelector('i');
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) icon.className = 'bi bi-eye-slash';
                } else {
                    input.type = 'password';
                    if (icon) icon.className = 'bi bi-eye';
                }
            }
        });
    });

});
