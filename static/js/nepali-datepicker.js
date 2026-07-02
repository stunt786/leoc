/**
 * Nepali Date (Bikram Sambat) Picker - Lightweight Vanilla JS
 * Provides BS date text inputs with a popup calendar
 * No external dependencies required
 */
(function () {
    'use strict';

    const BS_MONTHS = ['बैशाख', 'जेठ', 'असार', 'साउन', 'भदौ', 'असोज', 'कात्तिक', 'मंसिर', 'पुस', 'माघ', 'फागुन', 'चैत'];
    const BS_DAYS = ['आइत', 'सोम', 'मंगल', 'बुध', 'बिही', 'शुक्र', 'शनि'];
    const BS_MONTHS_DAYS = { 1: 31, 2: 31, 3: 31, 4: 32, 5: 31, 6: 31, 7: 30, 8: 30, 9: 29, 10: 29, 11: 30, 12: 30 };

    const BS_YEAR_START = window.BS_YEAR_START || {
        2000: [1943, 4, 14], 2001: [1944, 4, 13], 2002: [1945, 4, 14],
        2003: [1946, 4, 14], 2004: [1947, 4, 14], 2005: [1948, 4, 13],
        2006: [1949, 4, 14], 2007: [1950, 4, 14], 2008: [1951, 4, 14],
        2009: [1952, 4, 13], 2010: [1953, 4, 14], 2011: [1954, 4, 14],
        2012: [1955, 4, 14], 2013: [1956, 4, 13], 2014: [1957, 4, 14],
        2015: [1958, 4, 14], 2016: [1959, 4, 14], 2017: [1960, 4, 13],
        2018: [1961, 4, 14], 2019: [1962, 4, 14], 2020: [1963, 4, 14],
        2021: [1964, 4, 13], 2022: [1965, 4, 14], 2023: [1966, 4, 14],
        2024: [1967, 4, 14], 2025: [1968, 4, 13], 2026: [1969, 4, 14],
        2027: [1970, 4, 14], 2028: [1971, 4, 14], 2029: [1972, 4, 13],
        2030: [1973, 4, 14], 2031: [1974, 4, 14], 2032: [1975, 4, 14],
        2033: [1976, 4, 13], 2034: [1977, 4, 14], 2035: [1978, 4, 14],
        2036: [1979, 4, 14], 2037: [1980, 4, 13], 2038: [1981, 4, 14],
        2039: [1982, 4, 14], 2040: [1983, 4, 14], 2041: [1984, 4, 13],
        2042: [1985, 4, 14], 2043: [1986, 4, 14], 2044: [1987, 4, 14],
        2045: [1988, 4, 13], 2046: [1989, 4, 14], 2047: [1990, 4, 14],
        2048: [1991, 4, 14], 2049: [1992, 4, 13], 2050: [1993, 4, 14],
        2051: [1994, 4, 14], 2052: [1995, 4, 14], 2053: [1996, 4, 13],
        2054: [1997, 4, 14], 2055: [1998, 4, 14], 2056: [1999, 4, 14],
        2057: [2000, 4, 13], 2058: [2001, 4, 14], 2059: [2002, 4, 14],
        2060: [2003, 4, 14], 2061: [2004, 4, 13], 2062: [2005, 4, 14],
        2063: [2006, 4, 14], 2064: [2007, 4, 14], 2065: [2008, 4, 13],
        2066: [2009, 4, 14], 2067: [2010, 4, 14], 2068: [2011, 4, 14],
        2069: [2012, 4, 13], 2070: [2013, 4, 14], 2071: [2014, 4, 14],
        2072: [2015, 4, 14], 2073: [2016, 4, 13], 2074: [2017, 4, 14],
        2075: [2018, 4, 14], 2076: [2019, 4, 14], 2077: [2020, 4, 13],
        2078: [2021, 4, 14], 2079: [2022, 4, 14], 2080: [2023, 4, 14],
        2081: [2024, 4, 13], 2082: [2025, 4, 14], 2083: [2026, 4, 14],
        2084: [2027, 4, 14], 2085: [2028, 4, 13], 2086: [2029, 4, 14],
        2087: [2030, 4, 14], 2088: [2031, 4, 14], 2089: [2032, 4, 13],
        2090: [2033, 4, 14], 2091: [2034, 4, 14], 2092: [2035, 4, 14],
        2093: [2036, 4, 13], 2094: [2037, 4, 14], 2095: [2038, 4, 14],
        2096: [2039, 4, 14], 2097: [2040, 4, 13], 2098: [2041, 4, 14],
        2099: [2042, 4, 14], 2100: [2043, 4, 14],
    };

    function getADStart(bsYear) {
        const s = BS_YEAR_START[bsYear];
        return s ? new Date(s[0], s[1] - 1, s[2]) : null;
    }

    function isValidBS(bsDateStr) {
        return /^\d{4}-\d{2}-\d{2}$/.test(bsDateStr);
    }

    function bsToAD(bsDateStr) {
        if (!isValidBS(bsDateStr)) return null;
        const parts = bsDateStr.split('-');
        const yr = parseInt(parts[0]), mo = parseInt(parts[1]), dy = parseInt(parts[2]);
        const start = getADStart(yr);
        if (!start) return null;
        let daysToAdd = 0;
        for (let m = 1; m < mo; m++) daysToAdd += (BS_MONTHS_DAYS[m] || 30);
        daysToAdd += (dy - 1);
        const d = new Date(start.getTime() + daysToAdd * 86400000);
        return d;
    }

    function adToBS(date) {
        const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        const years = Object.keys(BS_YEAR_START).map(Number).sort((a, b) => a - b);
        let bsYear = null;
        for (const y of years) {
            const s = getADStart(y);
            if (d >= s) bsYear = y;
            else break;
        }
        if (!bsYear) bsYear = 2082;
        const start = getADStart(bsYear);
        const diff = Math.floor((d.getTime() - start.getTime()) / 86400000);
        let remaining = diff, bsMonth = 1, bsDay = 1;
        for (let m = 1; m <= 12; m++) {
            const dim = BS_MONTHS_DAYS[m] || 30;
            if (remaining < dim) { bsMonth = m; bsDay = remaining + 1; break; }
            remaining -= dim;
        }
        if (bsMonth > 12) { bsYear++; bsMonth = 1; bsDay = remaining + 1; }
        return `${bsYear}-${String(bsMonth).padStart(2, '0')}-${String(bsDay).padStart(2, '0')}`;
    }

    function getTodayBS() {
        if (typeof today_bs !== 'undefined' && today_bs) return today_bs;
        return adToBS(new Date());
    }

    function getDaysInMonth(bsYear, bsMonth) {
        return BS_MONTHS_DAYS[bsMonth] || 30;
    }

    function getMonthStartDay(bsYear, bsMonth) {
        const start = getADStart(bsYear);
        if (!start) return 0;
        let daysToAdd = 0;
        for (let m = 1; m < bsMonth; m++) daysToAdd += getDaysInMonth(bsYear, m);
        const d = new Date(start.getTime() + daysToAdd * 86400000);
        return d.getDay();
    }

    function parseBS(bsStr) {
        const parts = bsStr.split('-');
        return { year: parseInt(parts[0]), month: parseInt(parts[1]), day: parseInt(parts[2]) };
    }

    function formatBS(year, month, day) {
        return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    }

    let activePicker = null;

    function createPicker(input) {
        if (activePicker) activePicker.remove();

        const wrapper = document.createElement('div');
        wrapper.className = 'nepali-datepicker-dropdown';
        wrapper.style.cssText = `
            position: absolute; z-index: 9999; background: var(--bs-body-bg, #fff);
            border: 1px solid var(--bs-border-color, #dee2e6); border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15); padding: 12px; width: 290px;
            font-family: 'Noto Sans Devanagari', sans-serif;
        `;

        let bsDate = input.value && isValidBS(input.value) ? input.value : getTodayBS();
        let { year, month, day } = parseBS(bsDate);

        function render() {
            const daysInMonth = getDaysInMonth(year, month);
            const startDay = getMonthStartDay(year, month);
            let html = `
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                    <button type="button" class="btn btn-sm btn-outline-secondary np-prev-year" style="padding:2px 6px">&laquo;&laquo;</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary np-prev-month" style="padding:2px 6px">&laquo;</button>
                    <span style="font-weight:600;font-size:14px">
                        <select class="np-year-select form-select form-select-sm d-inline-block" style="width:auto;display:inline!important;width:80px!important;margin-right:4px">
                            ${(() => {
                                const yrs = Object.keys(BS_YEAR_START).map(Number).sort((a, b) => a - b);
                                return yrs.map(y => `<option value="${y}" ${y === year ? 'selected' : ''}>${y}</option>`).join('');
                            })()}
                        </select>
                        <select class="np-month-select form-select form-select-sm d-inline-block" style="width:auto;display:inline!important;width:auto!important">
                            ${BS_MONTHS.map((m, i) => `<option value="${i+1}" ${i+1 === month ? 'selected' : ''}>${m}</option>`).join('')}
                        </select>
                    </span>
                    <button type="button" class="btn btn-sm btn-outline-secondary np-next-month" style="padding:2px 6px">&raquo;</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary np-next-year" style="padding:2px 6px">&raquo;&raquo;</button>
                </div>
                <table style="width:100%;border-collapse:collapse;text-align:center">
                    <thead><tr>
                        ${BS_DAYS.map(d => `<th style="font-size:11px;padding:3px;color:var(--bs-secondary-color,#6c757d);font-weight:600">${d}</th>`).join('')}
                    </tr></thead>
                    <tbody>`;
            let dayCount = 1;
            const todayBS = getTodayBS();
            const isCurrentMonth = todayBS.startsWith(`${year}-${String(month).padStart(2, '0')}`);
            const todayDay = isCurrentMonth ? parseInt(todayBS.split('-')[2]) : -1;
            for (let r = 0; r < 6; r++) {
                if (dayCount > daysInMonth) break;
                html += '<tr>';
                for (let c = 0; c < 7; c++) {
                    if ((r === 0 && c < startDay) || dayCount > daysInMonth) {
                        html += '<td style="padding:2px"></td>';
                    } else {
                        const isToday = dayCount === todayDay && isCurrentMonth;
                        const isSelected = dayCount === day;
                        html += `<td style="padding:2px">
                            <button type="button" class="np-day-btn btn btn-sm ${isSelected ? 'btn-primary' : isToday ? 'btn-outline-primary' : 'btn-light'}"
                                data-day="${dayCount}"
                                style="width:32px;height:32px;padding:0;font-size:13px;border-radius:50%;${isSelected?'':''}">${dayCount}</button>
                        </td>`;
                        dayCount++;
                    }
                }
                html += '</tr>';
            }
            html += `</tbody></table>
                <div style="display:flex;justify-content:space-between;margin-top:8px">
                    <button type="button" class="btn btn-sm btn-outline-secondary np-today-btn">Today: ${getTodayBS()}</button>
                    <button type="button" class="btn btn-sm btn-close np-close-btn" style="font-size:12px"></button>
                </div>`;
            wrapper.innerHTML = html;

            wrapper.querySelector('.np-prev-year').onclick = () => { year--; render(); };
            wrapper.querySelector('.np-next-year').onclick = () => { year++; render(); };
            wrapper.querySelector('.np-prev-month').onclick = () => { month--; if (month < 1) { month = 12; year--; } render(); };
            wrapper.querySelector('.np-next-month').onclick = () => { month++; if (month > 12) { month = 1; year++; } render(); };
            wrapper.querySelector('.np-year-select').onchange = (e) => { year = parseInt(e.target.value); render(); };
            wrapper.querySelector('.np-month-select').onchange = (e) => { month = parseInt(e.target.value); render(); };
            wrapper.querySelector('.np-today-btn').onclick = () => {
                const t = getTodayBS();
                const p = parseBS(t);
                input.value = t;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                wrapper.remove();
                activePicker = null;
            };
            wrapper.querySelector('.np-close-btn').onclick = () => {
                wrapper.remove();
                activePicker = null;
            };
            wrapper.querySelectorAll('.np-day-btn').forEach(btn => {
                if (btn.dataset.day) {
                    btn.onclick = () => {
                        const d = parseInt(btn.dataset.day);
                        day = d;
                        const val = formatBS(year, month, day);
                        input.value = val;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        wrapper.remove();
                        activePicker = null;
                    };
                }
            });
        }

        render();

        const rect = input.getBoundingClientRect();
        wrapper.style.top = rect.bottom + window.scrollY + 4 + 'px';
        wrapper.style.left = rect.left + window.scrollX + 'px';
        document.body.appendChild(wrapper);
        activePicker = wrapper;
    }

    function initNepaliDatepicker() {
        document.querySelectorAll('.nepali-date').forEach(input => {
            if (input.dataset.nepaliDatepicker === 'initialized') return;
            input.dataset.nepaliDatepicker = 'initialized';
            input.autocomplete = 'off';
            input.placeholder = input.placeholder || 'YYYY-MM-DD';

            if (!input.value) {
                input.value = getTodayBS();
            }

            const icon = document.createElement('span');
            icon.className = 'nepali-date-icon';
            icon.innerHTML = '📅';
            icon.style.cssText = 'cursor:pointer;position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:16px;z-index:5';
            input.style.cssText = (input.style.cssText || '') + ';padding-right:35px';

            const wrap = document.createElement('div');
            wrap.style.cssText = 'position:relative;display:inline-block;width:100%';
            input.parentNode.insertBefore(wrap, input);
            wrap.appendChild(input);
            wrap.appendChild(icon);

            const showPicker = (e) => {
                e.preventDefault();
                e.stopPropagation();
                createPicker(input);
            };

            icon.onclick = showPicker;
            input.onfocus = showPicker;

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    if (activePicker) { activePicker.remove(); activePicker = null; }
                }
            });
        });

        document.addEventListener('click', (e) => {
            if (activePicker && !e.target.closest('.nepali-datepicker-dropdown') && !e.target.closest('.nepali-date') && !e.target.closest('.nepali-date-icon')) {
                activePicker.remove();
                activePicker = null;
            }
        });
    }

    window.getTodayBS = getTodayBS;
    window.adToBS = adToBS;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNepaliDatepicker);
    } else {
        initNepaliDatepicker();
    }

    document.addEventListener('DOMContentLoaded', function () {
        const observer = new MutationObserver(function () {
            initNepaliDatepicker();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });

})();
