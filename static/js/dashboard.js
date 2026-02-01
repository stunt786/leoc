// ============================================
// LEOC Dashboard JavaScript
// ============================================

let itemsChart = null;
let wardsChart = null;
let fiscalYearChart = null;
const reliefItemOptions = [
    'Food Packages', 'Water Bottles', 'Medical Supplies', 'Blankets',
    'Clothing', 'Hygiene Kits', 'Shelter Materials', 'Baby Care', 'Other'
];

// Global variables for filtering and pagination
let currentDistributions = [];
let filteredDistributions = [];
let currentPage = 1;
let itemsPerPage = 10; // Default to 10 rows per page

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function () {
    loadDistributions();
    loadStatistics();

    // Set up event listeners for filter controls
    setupFilterEventListeners();

    // Refresh data every 15 seconds for more frequent updates
    setInterval(() => {
        loadDistributions();
        loadStatistics();
    }, 15000);
});

// Set up event listeners for filter controls
function setupFilterEventListeners() {
    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);

    // Add event listener for per page selector
    const perPageSelector = document.getElementById('perPageSelector');
    if (perPageSelector) {
        // Set initial value
        perPageSelector.value = itemsPerPage;
        perPageSelector.addEventListener('change', function () {
            itemsPerPage = parseInt(this.value);
            currentPage = 1; // Reset to first page
            loadDistributions();
        });
    }
}

// Load all distributions and populate table
async function loadDistributions() {
    try {
        // Save current filter values before refreshing data
        const fiscalYearFilter = document.getElementById('fiscalYearFilter').value;
        const disasterTypeFilter = document.getElementById('disasterTypeFilter').value;
        const wardFilter = document.getElementById('wardFilter').value;

        // Build query parameters
        const params = new URLSearchParams();
        if (fiscalYearFilter) params.append('fiscal_year', fiscalYearFilter);
        if (disasterTypeFilter) params.append('disaster_type', disasterTypeFilter);
        if (wardFilter) params.append('ward', wardFilter);
        params.append('page', currentPage);
        params.append('per_page', itemsPerPage);

        const response = await fetch(`/api/distributions?${params}`);

        // Check if the response is OK before proceeding
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        const newDistributions = result.distributions;
        const pagination = result.pagination;

        // Update the stored distributions
        currentDistributions = newDistributions;
        filteredDistributions = newDistributions; // Since we're applying filters server-side now

        // Store pagination info
        paginationInfo = pagination;

        // Populate filter dropdowns (this preserves existing options and adds new ones)
        populateFilterDropdowns([...currentDistributions]); // Use spread to avoid reference issues

        // Restore the previous filter selections
        document.getElementById('fiscalYearFilter').value = fiscalYearFilter;
        document.getElementById('disasterTypeFilter').value = disasterTypeFilter;
        document.getElementById('wardFilter').value = wardFilter;

        // Update pagination controls
        generatePaginationControls();
        renderTablePage();

    } catch (error) {
        console.error('Error loading distributions:', error);
        // Don't update the UI if there's an error, keep showing the current data
        const tableBody = document.getElementById('tableBody');
        if (tableBody && currentDistributions.length === 0) {
            // Only show error if there's no existing data
            tableBody.innerHTML = '<tr class="text-center"><td colspan="8" class="py-4"><div class="alert alert-danger mb-0">Error loading data. Please try again later.</div></td></tr>';
        }
    }
}

// Populate filter dropdowns with unique values
function populateFilterDropdowns(distributions) {
    const fiscalYearSelect = document.getElementById('fiscalYearFilter');
    const disasterTypeSelect = document.getElementById('disasterTypeFilter');
    const wardSelect = document.getElementById('wardFilter');

    // Clear existing options (except the first "All" option)
    fiscalYearSelect.innerHTML = '<option value="">All Fiscal Years</option>';
    disasterTypeSelect.innerHTML = '<option value="">All Disaster Types</option>';
    wardSelect.innerHTML = '<option value="">All Wards</option>';

    // Extract unique values
    const fiscalYears = [...new Set(distributions.map(d => d.fiscal_year).filter(year => year))];
    const disasterTypes = [...new Set(distributions.map(d => d.disaster_type).filter(type => type))];
    const wards = [...new Set(distributions.map(d => d.ward).filter(ward => ward))];

    // Add options to selects
    fiscalYears.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        fiscalYearSelect.appendChild(option);
    });

    disasterTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        disasterTypeSelect.appendChild(option);
    });

    wards.forEach(ward => {
        const option = document.createElement('option');
        option.value = ward;
        option.textContent = `Ward ${ward}`;
        wardSelect.appendChild(option);
    });
}

// Apply filters to the distributions
function applyFilters() {
    // Reload distributions with current filter values
    currentPage = 1; // Reset to first page when applying filters
    loadDistributions();
}

// Reset all filters
function resetFilters() {
    document.getElementById('fiscalYearFilter').value = '';
    document.getElementById('disasterTypeFilter').value = '';
    document.getElementById('wardFilter').value = '';

    // Reset to first page
    currentPage = 1;

    // Reload distributions without filters
    loadDistributions();
}

// Render the current page of the table
function renderTablePage() {
    const tableBody = document.getElementById('tableBody');
    const emptyRow = document.getElementById('emptyRow');

    if (filteredDistributions.length === 0) {
        if (emptyRow) emptyRow.style.display = '';
        if (tableBody) {
            tableBody.innerHTML = '<tr class="text-center" id="emptyRow"><td colspan="8" class="py-4"><p class="text-muted mb-0">No distributions match the selected filters. <a href="/form">Add one now</a></p></td></tr>';
        }
        // Also hide pagination controls if no results
        document.getElementById('paginationControls').innerHTML = '';
        return;
    }

    if (emptyRow) emptyRow.style.display = 'none';

    // Since we're using server-side pagination, we use the results from the API directly
    const pageDistributions = filteredDistributions;

    // Update table info
    const tableInfo = document.getElementById('tableInfo');
    if (tableInfo && paginationInfo) {
        const start = (paginationInfo.page - 1) * paginationInfo.per_page + 1;
        const end = Math.min(paginationInfo.page * paginationInfo.per_page, paginationInfo.total);
        tableInfo.textContent = `Showing ${start} - ${end} of ${paginationInfo.total} records`;
    }

    if (tableBody) {
        // Update the table with new data
        tableBody.innerHTML = pageDistributions
            .map(dist => {
                const itemsList = dist.relief_items.map(item => `${item.item} ${item.quantity} ${item.unit || 'units'}`).join(', ');
                return `
                    <tr>
                        <td>
                            <strong>${escapeHtml(dist.beneficiary_name)}</strong>
                            ${dist.phone ? `<br><small class="text-muted">${escapeHtml(dist.phone)}</small>` : ''}
                        </td>
                        <td><code>${escapeHtml(dist.beneficiary_id)}</code></td>
                        <td>${escapeHtml(dist.location)}</td>
                        <td><small>${escapeHtml(itemsList)}</small></td>
                        <td><strong>₹${dist.cash_received.toFixed(2)}</strong></td>
                        <td><small>${new Date(dist.distribution_date).toLocaleDateString()}</small></td>
                        <td>${getStatusBadge(dist.status)}</td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-info" onclick="viewDistribution(${dist.id})" title="View Details">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <button class="btn btn-outline-primary" onclick="openEditModal(${dist.id})" title="Edit" ${dist.is_locked ? 'disabled title="Record is locked"' : ''}>
                                    <i class="bi bi-pencil"></i>
                                </button>
                                ${dist.image_filename ? `<a href="/static/uploads/${escapeHtml(dist.image_filename)}" class="btn btn-outline-info" target="_blank" title="View Image">
                                    <i class="bi bi-image"></i>
                                </a>` : ''}
                                <button class="btn btn-outline-danger" onclick="deleteDistribution(${dist.id})" title="Delete" ${dist.is_locked ? 'disabled title="Record is locked"' : ''}>
                                    <i class="bi bi-trash"></i>
                                </button>
                                <button class="btn ${dist.is_locked ? 'btn-warning' : 'btn-secondary'}" onclick="toggleLock(${dist.id}, ${dist.is_locked})" title="${dist.is_locked ? 'Unlock record' : 'Lock record'}">
                                    <i class="bi bi-${dist.is_locked ? 'unlock-fill' : 'lock'}"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
    }

    // Generate pagination controls
    generatePaginationControls();
}

// Generate pagination controls (server-side pagination)
function generatePaginationControls() {
    const paginationContainer = document.getElementById('paginationControls');

    if (!paginationInfo.pages || paginationInfo.pages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    let paginationHTML = '';

    // Previous button
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${Math.max(1, currentPage - 1)})">Previous</a>
        </li>
    `;

    // Page numbers
    // Show first page
    if (paginationInfo.pages > 1) {
        paginationHTML += `
            <li class="page-item ${currentPage === 1 ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(1)">1</a>
            </li>
        `;
    }

    // Ellipsis if needed
    if (currentPage > 3) {
        paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
    }

    // Pages around current page
    const startPage = Math.max(2, currentPage - 1);
    const endPage = Math.min(paginationInfo.pages - 1, currentPage + 1);

    for (let i = startPage; i <= endPage; i++) {
        if (i !== 1 && i !== paginationInfo.pages) {
            paginationHTML += `
                <li class="page-item ${currentPage === i ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>
            `;
        }
    }

    // Ellipsis if needed
    if (currentPage < paginationInfo.pages - 2) {
        paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
    }

    // Last page
    if (paginationInfo.pages > 1) {
        paginationHTML += `
            <li class="page-item ${currentPage === paginationInfo.pages ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${paginationInfo.pages})">${paginationInfo.pages}</a>
            </li>
        `;
    }

    // Next button
    paginationHTML += `
        <li class="page-item ${currentPage === paginationInfo.pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${Math.min(paginationInfo.pages, currentPage + 1)})">Next</a>
        </li>
    `;

    paginationContainer.innerHTML = paginationHTML;
}

// Global variable to store pagination info
let paginationInfo = {};

// Change to a specific page
function changePage(page) {
    if (page < 1 || (paginationInfo.pages && page > paginationInfo.pages)) {
        return;
    }

    currentPage = page;
    loadDistributions(); // Reload with new page
}

// Helper function to compare arrays of distributions
function arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) return false;

    for (let i = 0; i < arr1.length; i++) {
        if (JSON.stringify(arr1[i]) !== JSON.stringify(arr2[i])) {
            return false;
        }
    }

    return true;
}

// Load and display statistics
async function loadStatistics() {
    try {
        // Get current filter values
        const fiscalYearFilter = document.getElementById('fiscalYearFilter').value;
        const disasterTypeFilter = document.getElementById('disasterTypeFilter').value;
        const wardFilter = document.getElementById('wardFilter').value;

        // Build query parameters
        const params = new URLSearchParams();
        if (fiscalYearFilter) params.append('fiscal_year', fiscalYearFilter);
        if (disasterTypeFilter) params.append('disaster_type', disasterTypeFilter);
        if (wardFilter) params.append('ward', wardFilter);

        const response = await fetch(`/api/statistics?${params}`);

        // Check if the response is OK before proceeding
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const stats = await response.json();

        // Update stat cards with smooth transition
        const totalDistEl = document.getElementById('total-distributions');
        const totalItemsEl = document.getElementById('total-items');
        const totalCashEl = document.getElementById('total-cash');
        const totalBenEl = document.getElementById('total-beneficiaries');

        if (totalDistEl && totalItemsEl && totalCashEl && totalBenEl) {
            // Add animation effect when values change
            animateValue(totalDistEl, parseInt(totalDistEl.textContent.replace(/,/g, '')), stats.total_distributions);
            animateValue(totalItemsEl, parseInt(totalItemsEl.textContent.replace(/,/g, '')), stats.total_items);
            animateValue(totalCashEl, parseFloat(totalCashEl.textContent.replace(/[₹,]/g, '')), Math.floor(stats.total_cash), 'currency');
            animateValue(totalBenEl, parseInt(totalBenEl.textContent.replace(/,/g, '')), stats.total_distributions);
        }

        // Update charts
        updateChartsData(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Helper function to animate value changes
function animateValue(element, start, end, type = 'number') {
    const duration = 1000; // Animation duration in ms
    const startTime = performance.now();

    function updateValue(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease-out function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 2);

        const currentValue = start + (end - start) * easeOut;

        if (type === 'currency') {
            element.textContent = '₹' + formatNumber(Math.floor(currentValue));
        } else {
            element.textContent = formatNumber(Math.floor(currentValue));
        }

        if (progress < 1) {
            requestAnimationFrame(updateValue);
        } else {
            // Ensure final value is displayed correctly
            if (type === 'currency') {
                element.textContent = '₹' + formatNumber(end);
            } else {
                element.textContent = formatNumber(end);
            }
        }
    }

    requestAnimationFrame(updateValue);
}

// Update or create charts
function updateChartsData(stats) {
    // Items Distribution Chart
    updateItemsChart(stats.items_distribution);

    // Ward Distribution Chart
    updateWardsChart(stats.ward_distribution || []);

    // Fiscal Year Distribution Chart
    updateFiscalYearChart(stats.fiscal_year_distribution || []);
}

// Update Items Distribution Chart
function updateItemsChart(itemsData) {
    const ctx = document.getElementById('itemsChart');
    if (!ctx) return;

    const labels = itemsData.map(d => d.item);
    const data = itemsData.map(d => d.quantity);
    const colors = generateColors(itemsData.length);

    if (itemsChart) {
        itemsChart.data.labels = labels;
        itemsChart.data.datasets[0].data = data;
        itemsChart.data.datasets[0].backgroundColor = colors;
        itemsChart.update();
    } else {
        itemsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#ffffff',
                    borderWidth: 3,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Changed to false to allow smaller size
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 10, weight: 'bold' }, // Smaller font
                            padding: 10,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 10,
                        titleFont: { size: 12, weight: 'bold' },
                        bodyFont: { size: 11 },
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Update Ward Distribution Chart
function updateWardsChart(wardData) {
    const ctx = document.getElementById('wardsChart');
    if (!ctx) return;

    const labels = wardData.map(d => d.ward);
    const data = wardData.map(d => d.count);
    const colors = generateColors(wardData.length);

    if (wardsChart) {
        wardsChart.data.labels = labels;
        wardsChart.data.datasets[0].data = data;
        wardsChart.data.datasets[0].backgroundColor = colors.slice(0, wardData.length);
        wardsChart.update();
    } else {
        wardsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Distributions',
                    data: data,
                    backgroundColor: colors.slice(0, wardData.length),
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: 'rgba(0, 0, 0, 0.2)'
                }]
            },
            options: {
                indexAxis: 'x', // Changed from 'y' to 'x' for vertical bars
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Hide legend for compactness
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 10,
                        titleFont: { size: 12, weight: 'bold' },
                        bodyFont: { size: 11 },
                        callbacks: {
                            label: function (context) {
                                return 'Distributions: ' + context.parsed.y;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: { size: 10, weight: '500' }
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: { size: 10 }
                        }
                    }
                }
            }
        });
    }
}

// Update Fiscal Year Distribution Chart
function updateFiscalYearChart(fiscalData) {
    const ctx = document.getElementById('fiscalYearChart');
    if (!ctx) return;

    const labels = fiscalData.map(d => d.fiscal_year);
    const data = fiscalData.map(d => d.count);
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];

    if (fiscalYearChart) {
        fiscalYearChart.data.labels = labels;
        fiscalYearChart.data.datasets[0].data = data;
        fiscalYearChart.data.datasets[0].backgroundColor = colors.slice(0, fiscalData.length);
        fiscalYearChart.update();
    } else {
        fiscalYearChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Distributions',
                    data: data,
                    backgroundColor: colors.slice(0, fiscalData.length),
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: 'rgba(0, 0, 0, 0.2)'
                }]
            },
            options: {
                indexAxis: 'x', // Changed from 'y' to 'x' for vertical bars
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Hide legend for compactness
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 10,
                        titleFont: { size: 12, weight: 'bold' },
                        bodyFont: { size: 11 },
                        callbacks: {
                            label: function (context) {
                                return 'Distributions: ' + context.parsed.y;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: { size: 10, weight: '500' }
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: { size: 10 }
                        }
                    }
                }
            }
        });
    }
}

// Delete a distribution record
async function deleteDistribution(id) {
    if (!confirm('Are you sure you want to delete this distribution record?')) {
        return;
    }

    try {
        const response = await fetch(`/api/distributions/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showNotification('success', 'Distribution deleted successfully');
            loadDistributions();
            loadStatistics();
        } else {
            showNotification('danger', 'Error: ' + data.message);
        }
    } catch (error) {
        showNotification('danger', 'Error: ' + error.message);
    }
}

// Utility Functions
function getStatusBadge(status) {
    const statusClass = {
        'Distributed': 'success',
        'Pending': 'warning',
        'In Progress': 'info',
        'Delivered': 'success'
    };

    const badgeClass = statusClass[status] || 'secondary';
    return `<span class="badge badge-${badgeClass}">${escapeHtml(status)}</span>`;
}

function generateColors(count) {
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
        '#fa709a', '#feca57', '#ff9ff3', '#a8edea', '#fed6e3',
        '#ffbe76', '#ff7675', '#74b9ff', '#a29bfe', '#6c5ce7'
    ];

    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(type, message) {
    const alertBox = document.createElement('div');
    alertBox.className = `alert alert-${type} alert-dismissible fade show`;
    alertBox.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertBox, container.firstChild);

    setTimeout(() => alertBox.remove(), 5000);
}

// ============================================
// Edit Functions
// ============================================

// Open distribution in edit form with all fields
async function openEditModal(id) {
    // Redirect to form page with edit ID to load and edit with full form
    window.location.href = `/form?edit=${id}`;
}

function addEditItemRow(item = null, quantity = null, unit = null) {
    const container = document.getElementById('editItemsContainer');
    const rowId = Date.now();

    const row = document.createElement('div');
    row.className = 'edit-item-row mb-3 p-3 border rounded bg-light';
    row.id = `edit-item-${rowId}`;
    row.innerHTML = `
        <div class="row">
            <div class="col-md-5">
                <label class="form-label">Relief Item</label>
                <select class="form-control edit-item-select" data-id="${rowId}" required>
                    <option value="">-- Select Item --</option>
                    ${reliefItemOptions.map(opt => `<option value="${opt}" ${item === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Quantity</label>
                <input type="number" class="form-control edit-item-qty" data-id="${rowId}" min="1" value="${quantity || 1}" required>
            </div>
            <div class="col-md-4">
                <label class="form-label">Unit</label>
                <input type="text" class="form-control edit-item-unit" data-id="${rowId}" value="${unit || ''}" placeholder="e.g., kg, liters, packets" required>
            </div>
        </div>
        <button type="button" class="btn btn-sm btn-danger mt-2" onclick="removeEditItemRow('${rowId}')">
            <i class="bi bi-trash"></i> Remove
        </button>
    `;

    container.appendChild(row);
}

function removeEditItemRow(rowId) {
    const row = document.getElementById(`edit-item-${rowId}`);
    if (row) {
        row.remove();
    }
}

function collectEditItems() {
    const items = [];
    document.querySelectorAll('.edit-item-row').forEach(row => {
        const select = row.querySelector('.edit-item-select');
        const qty = row.querySelector('.edit-item-qty');
        const unit = row.querySelector('.edit-item-unit');

        if (select.value && qty.value) {
            items.push({
                item: select.value,
                quantity: parseInt(qty.value),
                unit: unit.value || 'unit'
            });
        }
    });
    return items;
}

async function saveEdit() {
    const id = document.getElementById('edit_id').value;
    const items = collectEditItems();

    if (items.length === 0) {
        showNotification('warning', '<i class="bi bi-exclamation-triangle"></i> Please add at least one relief item');
        return;
    }

    const formData = new FormData();
    formData.append('beneficiary_name', document.getElementById('edit_beneficiary_name').value);
    formData.append('phone', document.getElementById('edit_phone').value);
    formData.append('location', document.getElementById('edit_location').value);
    formData.append('cash_received', document.getElementById('edit_cash_received').value);
    formData.append('status', document.getElementById('edit_status').value);
    formData.append('notes', document.getElementById('edit_notes').value);
    formData.append('relief_items_json', JSON.stringify(items));

    try {
        const response = await fetch(`/api/distributions/${id}`, {
            method: 'PUT',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showNotification('success', 'Distribution updated successfully');
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadDistributions();
            loadStatistics();
        } else {
            showNotification('danger', 'Error: ' + data.message);
        }
    } catch (error) {
        showNotification('danger', 'Error: ' + error.message);
    }
}

// Export filtered data to XLSX or PDF
function exportFilteredData(format) {
    // Get the filtered data that's currently displayed
    let exportData;

    // If there are filtered results, use them; otherwise, use all data
    if (filteredDistributions && filteredDistributions.length > 0) {
        exportData = filteredDistributions;
    } else {
        exportData = currentDistributions;
    }

    if (format === 'xlsx') {
        exportToXLSX(exportData);
    } else if (format === 'pdf') {
        exportToPDF(exportData);
    }
}

// Export data to XLSX format
function exportToXLSX(data) {
    // Check if SheetJS library is loaded
    if (typeof XLSX === 'undefined') {
        // Dynamically load SheetJS if not available
        loadSheetJS(() => {
            exportToXLSXInternal(data);
        });
        return;
    }

    exportToXLSXInternal(data);
}

// Internal function to export to XLSX
function exportToXLSXInternal(data) {
    // Prepare the data for export
    const exportRows = data.map(dist => {
        // Format relief items as a single string
        const itemsList = dist.relief_items.map(item => `${item.item} ${item.quantity} ${item.unit || 'units'}`).join('; ');

        return {
            'Beneficiary Name': dist.beneficiary_name,
            'Beneficiary ID': dist.beneficiary_id,
            'Father Name': dist.father_name || '',
            'Phone': dist.phone || '',
            'Disaster Date': dist.disaster_date || '',
            'Disaster Type': dist.disaster_type || '',
            'Fiscal Year': dist.fiscal_year || '',
            'Ward': dist.ward || '',
            'Tole': dist.tole || '',
            'Location': dist.location || '',
            'Latitude': dist.latitude || '',
            'Longitude': dist.longitude || '',
            'Current Shelter Location': dist.current_shelter_location || '',
            'Male Count': dist.male_count || 0,
            'Female Count': dist.female_count || 0,
            'Children Count': dist.children_count || 0,
            'Pregnant Mother Count': dist.pregnant_mother_count || 0,
            'Mother with Baby <2 Years': dist.mother_under_2_baby || 0,
            'Deaths During Disaster': dist.deaths_during_disaster || 0,
            'In Social Security Fund': dist.in_social_security_fund ? 'Yes' : 'No',
            'SSF Type': dist.ssf_type || '',
            'Poverty Card Holder': dist.poverty_card_holder ? 'Yes' : 'No',
            'Bank Account Holder Name': dist.bank_account_holder_name || '',
            'Bank Account Number': dist.bank_account_number || '',
            'Bank Name': dist.bank_name || '',
            'Relief Items': itemsList,
            'Cash Received': dist.cash_received || 0,
            'Distribution Date': dist.distribution_date || '',
            'Status': dist.status || '',
            'Notes': dist.notes || '',
            'Created At': dist.created_at || '',
            'Updated At': dist.updated_at || ''
        };
    });

    // Create worksheet and workbook
    const ws = XLSX.utils.json_to_sheet(exportRows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Relief Distributions");

    // Set column widths for better readability
    const colWidths = [
        { wch: 20 }, // Beneficiary Name
        { wch: 15 }, // Beneficiary ID
        { wch: 15 }, // Father Name
        { wch: 12 }, // Phone
        { wch: 12 }, // Disaster Date
        { wch: 15 }, // Disaster Type
        { wch: 12 }, // Fiscal Year
        { wch: 8 },  // Ward
        { wch: 15 }, // Tole
        { wch: 20 }, // Location
        { wch: 12 }, // Latitude
        { wch: 12 }, // Longitude
        { wch: 25 }, // Current Shelter Location
        { wch: 8 },  // Male Count
        { wch: 8 },  // Female Count
        { wch: 8 },  // Children Count
        { wch: 10 }, // Pregnant Mother Count
        { wch: 10 }, // Mother with Baby <2 Years
        { wch: 10 }, // Deaths During Disaster
        { wch: 8 },  // In Social Security Fund
        { wch: 12 }, // SSF Type
        { wch: 8 },  // Poverty Card Holder
        { wch: 20 }, // Bank Account Holder Name
        { wch: 15 }, // Bank Account Number
        { wch: 15 }, // Bank Name
        { wch: 30 }, // Relief Items
        { wch: 12 }, // Cash Received
        { wch: 15 }, // Distribution Date
        { wch: 12 }, // Status
        { wch: 30 }, // Notes
        { wch: 15 }, // Created At
        { wch: 15 }  // Updated At
    ];
    ws['!cols'] = colWidths;

    // Export the file
    const fileName = `Relief_Distributions_${new Date().toISOString().slice(0, 10)}.xlsx`;
    XLSX.writeFile(wb, fileName);
}

// Function to dynamically load SheetJS library
function loadSheetJS(callback) {
    if (window.XLSX) {
        callback();
        return;
    }

    const script = document.createElement('script');
    script.src = 'https://cdn.sheetjs.com/xlsx-0.20.0/package/dist/xlsx.full.min.js';
    script.onload = callback;
    document.head.appendChild(script);
}

// Export data to PDF format
function exportToPDF(data) {
    // Check if jsPDF library is loaded
    if (typeof jsPDF === 'undefined') {
        // Dynamically load jsPDF if not available
        loadJsPDF(() => {
            exportToPDFInternal(data);
        });
        return;
    }

    exportToPDFInternal(data);
}

// Internal function to export to PDF
function exportToPDFInternal(data) {
    const { jsPDF } = window.jspdf;

    // Create a new PDF document
    const doc = new jsPDF('l', 'mm', 'a4'); // Landscape orientation

    // Title
    doc.setFontSize(18);
    // Using splitTextToSize to handle Unicode characters better
    const title = 'Relief Distribution Report';
    const titleLines = doc.splitTextToSize(title, 180);
    doc.text(titleLines, 148, 15, null, null, 'center');

    // Subtitle with date
    doc.setFontSize(12);
    const subtitle = `Exported on: ${new Date().toLocaleDateString()}`;
    const subtitleLines = doc.splitTextToSize(subtitle, 180);
    doc.text(subtitleLines, 148, 22, null, null, 'center');

    // Prepare headers and data for the table - include more comprehensive data
    const headers = [
        'Beneficiary Name', 'ID', 'Father Name', 'Phone', 'Disaster Date', 'Disaster Type',
        'Fiscal Year', 'Ward', 'Tole', 'Location', 'Relief Items', 'Cash', 'Date', 'Status'
    ];

    const rows = data.map(dist => {
        // Format relief items as a string
        const itemsList = dist.relief_items.map(item => `${item.item} ${item.quantity} ${item.unit || 'units'}`).join('; ');

        return [
            dist.beneficiary_name,
            dist.beneficiary_id,
            dist.father_name || '',
            dist.phone || '',
            dist.disaster_date || '',
            dist.disaster_type || '',
            dist.fiscal_year || '',
            dist.ward || '',
            dist.tole || '',
            dist.location || '',
            itemsList,
            `Rs. ${dist.cash_received}`,
            new Date(dist.distribution_date).toLocaleDateString(),
            dist.status
        ];
    });

    // Add the table to the PDF with proper configuration for Unicode characters
    if (typeof doc.autoTable === 'function') {
        // If jspdf-autotable plugin is available
        doc.autoTable({
            head: [headers],
            body: rows,
            startY: 30,
            styles: {
                fontSize: 7, // Smaller font to fit more data
                cellPadding: 2,
                overflow: 'linebreak', // Handle text overflow
                cellWidth: 'wrap' // Auto-adjust cell width
            },
            headStyles: {
                fillColor: [66, 133, 244], // Google blue
                textColor: [255, 255, 255],
                fontSize: 8
            },
            bodyStyles: {
                fontSize: 7
            },
            alternateRowStyles: {
                fillColor: [245, 245, 245]
            },
            // Handle text wrapping for long content
            columnStyles: {
                0: { cellWidth: 30 }, // Beneficiary Name
                1: { cellWidth: 20 }, // ID
                2: { cellWidth: 25 }, // Father Name
                3: { cellWidth: 20 }, // Phone
                4: { cellWidth: 18 }, // Disaster Date
                5: { cellWidth: 20 }, // Disaster Type
                6: { cellWidth: 18 }, // Fiscal Year
                7: { cellWidth: 10 }, // Ward
                8: { cellWidth: 20 }, // Tole
                9: { cellWidth: 25 }, // Location
                10: { cellWidth: 40 }, // Relief Items
                11: { cellWidth: 15 }, // Cash
                12: { cellWidth: 18 }, // Date
                13: { cellWidth: 15 }  // Status
            },
            // Use hooks to handle text processing for Unicode characters
            didParseCell: function (data) {
                // Process cell content to handle special characters
                if (data.cell.section === 'body') {
                    // Ensure proper handling of Unicode characters
                    data.cell.styles.overflow = 'linebreak';
                }
            },
            // Hook to handle font for Devanagari characters
            willDrawCell: function (data) {
                // Attempt to set a font that supports Devanagari if available
                try {
                    // jsPDF has limited font support for Devanagari
                    // This is a workaround for better character rendering
                    doc.setFont("helvetica");
                } catch (e) {
                    console.warn("Could not set font for Devanagari characters:", e);
                }
            }
        });
    } else {
        // Fallback manual table creation if autoTable is not available
        createManualPDFTable(doc, headers, rows);
    }

    // Save the PDF
    doc.save(`Relief_Distributions_${new Date().toISOString().slice(0, 10)}.pdf`);
}

// Function to create a manual table in PDF if autoTable is not available
function createManualPDFTable(doc, headers, rows) {
    let yPosition = 35;
    const pageHeight = doc.internal.pageSize.height;
    const rowHeight = 10;
    const colWidths = [30, 20, 15, 30, 40, 20, 25, 20]; // Approximate column widths

    // Draw headers
    doc.setFont(undefined, 'bold');
    for (let i = 0; i < headers.length; i++) {
        doc.rect(10, yPosition - 6, colWidths[i], rowHeight, 'S');
        doc.text(headers[i], 12, yPosition, { maxWidth: colWidths[i] - 4 });
    }
    yPosition += rowHeight;

    // Draw data rows
    doc.setFont(undefined, 'normal');
    for (let i = 0; i < rows.length; i++) {
        // Check if we need a new page
        if (yPosition + rowHeight > pageHeight - 20) {
            doc.addPage();
            yPosition = 20;
        }

        const row = rows[i];
        for (let j = 0; j < row.length; j++) {
            doc.rect(10 + colWidths.slice(0, j).reduce((a, b) => a + b, 0), yPosition - 6,
                colWidths[j], rowHeight, 'S');
            doc.text(String(row[j]), 12 + colWidths.slice(0, j).reduce((a, b) => a + b, 0),
                yPosition, { maxWidth: colWidths[j] - 4 });
        }
        yPosition += rowHeight;
    }
}

// Function to dynamically load jsPDF library
function loadJsPDF(callback) {
    if (window.jspdf) {
        callback();
        return;
    }

    // Load jsPDF
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
    script.onload = () => {
        // Load jspdf autotable plugin
        const tableScript = document.createElement('script');
        tableScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.25/jspdf.plugin.autotable.min.js';
        tableScript.onload = callback;
        document.head.appendChild(tableScript);
    };
    document.head.appendChild(script);
}

// View distribution details
function viewDistribution(id) {
    window.location.href = `/view/${id}`;
}

// Toggle lock status for a distribution record
async function toggleLock(id, isCurrentlyLocked) {
    // Prompt for unlock key
    const unlockKey = prompt(`Enter unlock key to ${isCurrentlyLocked ? 'unlock' : 'lock'} this record:`);

    if (!unlockKey) {
        return; // User cancelled
    }

    try {
        const response = await fetch(`/api/distributions/${id}/lock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ unlock_key: unlockKey })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('success', `Record ${data.is_locked ? 'locked' : 'unlocked'} successfully`);
            // Reload the table to reflect the new lock status
            loadDistributions();
            loadStatistics();
        } else {
            showNotification('danger', 'Error: ' + data.message);
        }
    } catch (error) {
        showNotification('danger', 'Error: ' + error.message);
    }
}
