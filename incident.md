{% extends "base.html" %}

{% block title %}ड्यासबोर्ड - LEOC{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Header -->
    <div class="row mb-4">
        <div class="col-12">
            <h1 class="display-6 fw-bold mb-2">
                <i class="bi bi-graph-up"></i> राहात वितरण ड्यासबोर्ड
            </h1>
            <p class="text-muted">आपतकालीन राहत वितरणको अनुगमन र व्यवस्थापन</p>
        </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4 g-3">
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card stat-card shadow-sm h-100"
                style="background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%); color: white;">
                <div class="card-body text-center py-4">
                    <i class="bi bi-box-seam mb-2" style="font-size: 2rem;"></i>
                    <h2 class="display-6 fw-bold mb-0" id="total-distributions">0</h2>
                    <p class="mb-0 opacity-75">जम्मा वितरण (Total)</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card stat-card shadow-sm h-100"
                style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: #004d40;">
                <div class="card-body text-center py-4">
                    <i class="bi bi-bag-check mb-2" style="font-size: 2rem;"></i>
                    <h2 class="display-6 fw-bold mb-0" id="total-items">0</h2>
                    <p class="mb-0 opacity-75">जम्मा वस्तु (Items)</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card stat-card shadow-sm h-100"
                style="background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); color: #4a5568;">
                <div class="card-body text-center py-4">
                    <i class="bi bi-cash-coin mb-2" style="font-size: 2rem;"></i>
                    <h2 class="display-6 fw-bold mb-0" id="total-cash">₹0</h2>
                    <p class="mb-0 opacity-75">जम्मा रकम (Cash)</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card stat-card shadow-sm h-100"
                style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                <div class="card-body text-center py-4">
                    <i class="bi bi-people mb-2" style="font-size: 2rem;"></i>
                    <h2 class="display-6 fw-bold mb-0" id="total-beneficiaries">0</h2>
                    <p class="mb-0 opacity-75">लाभग्राहि (Users)</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts Row -->
    <div class="row mb-4">
        <div class="col-lg-4 mb-4">
            <div class="card chart-card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="bi bi-pie-chart"></i> सामाग्री वितरण</h5>
                </div>
                <div class="card-body">
                    <canvas id="itemsChart"></canvas>
                </div>
            </div>
        </div>
        <div class="col-lg-4 mb-4">
            <div class="card chart-card">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="bi bi-bar-chart"></i> वडा अनुसार विवरण</h5>
                </div>
                <div class="card-body">
                    <canvas id="wardsChart"></canvas>
                </div>
            </div>
        </div>
        <div class="col-lg-4 mb-4">
            <div class="card chart-card">
                <div class="card-header bg-warning text-white">
                    <h5 class="mb-0"><i class="bi bi-calendar"></i> आ.ब अनुसार विवरण</h5>
                </div>
                <div class="card-body">
                    <canvas id="fiscalYearChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- GIS Map Row -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card shadow-sm">
                <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-geo-alt"></i> विपद् र राहात GIS नक्सा</h5>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-light"
                            onclick="document.getElementById('map-iframe').src = '/map'">
                            <i class="bi bi-arrow-clockwise"></i> रिफ्रेस
                        </button>
                        <a href="/map" target="_blank" class="btn btn-sm btn-outline-info">
                            <i class="bi bi-arrows-fullscreen"></i> नक्सा ठूलो पार्नुहोस्
                        </a>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div class="map-container">
                        <iframe id="map-iframe" src="/map" width="100%" height="600px" frameborder="0"></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Recent Distributions Table -->

    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-list-check"></i> वितरण विवरण</h5>
                    <div class="d-flex gap-2">
                        <div class="dropdown">
                            <button class="btn btn-sm btn-success dropdown-toggle" type="button" id="exportDropdown"
                                data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="bi bi-download"></i> निर्यात गर्नुहोस्
                            </button>
                            <ul class="dropdown-menu" aria-labelledby="exportDropdown">
                                <li><a class="dropdown-item" href="#" onclick="exportFilteredData('xlsx')"><i
                                            class="bi bi-file-spreadsheet"></i> Excel (XLSX) मा</a></li>
                                <li><a class="dropdown-item" href="#" onclick="exportFilteredData('pdf')"><i
                                            class="bi bi-file-pdf"></i> PDF मा</a></li>
                            </ul>
                        </div>
                        <a href="/form" class="btn btn-sm btn-light">
                            <i class="bi bi-plus-circle"></i> नयाँ थप्नुहोस्
                        </a>
                    </div>
                </div>

                <!-- Filter Controls -->
                <div class="card-header bg-light py-2">
                    <div class="row g-2">
                        <div class="col-md-4">
                            <label class="form-label text-muted small mb-1">आर्थिक वर्ष</label>
                            <select id="fiscalYearFilter" class="form-select form-select-sm">
                                <option value="">सबै आर्थिक वर्ष</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label text-muted small mb-1">विपद्को प्रकार</label>
                            <select id="disasterTypeFilter" class="form-select form-select-sm">
                                <option value="">सबै प्रकार</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label text-muted small mb-1">वडा</label>
                            <select id="wardFilter" class="form-select form-select-sm">
                                <option value="">सबै वडाहरू</option>
                            </select>
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-12">
                            <button id="applyFiltersBtn" class="btn btn-sm btn-primary me-2">
                                <i class="bi bi-funnel"></i> फिल्टर लागू गर्नुहोस्
                            </button>
                            <button id="resetFiltersBtn" class="btn btn-sm btn-outline-secondary">
                                <i class="bi bi-x-circle"></i> रिसेट
                            </button>
                        </div>
                    </div>
                </div>

                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="d-flex align-items-center gap-2">
                            <label class="form-label text-muted small mb-0">देखाउनुहोस्</label>
                            <select id="perPageSelector" class="form-select form-select-sm" style="width: auto;">
                                <option value="10" selected>10</option>
                                <option value="25">25</option>
                                <option value="50">50</option>
                            </select>
                            <label class="form-label text-muted small mb-0">रेकर्डहरू</label>
                        </div>
                        <div id="tableInfo" class="text-muted small">
                            देखाउँदै: ० - ० को जम्मा ० रेकर्डहरू
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover" id="distributionsTable">
                            <thead class="table-light">
                                <tr>
                                    <th>लाभग्राहिको नाम थर</th>
                                    <th>ना.प्र.प्र.नं</th>
                                    <th>ठेगाना</th>
                                    <th>राहात सामाग्री</th>
                                    <th>रकम रु</th>
                                    <th>मिति</th>
                                    <th>स्थिति</th>
                                    <th>कार्य</th>
                                </tr>
                            </thead>
                            <tbody id="tableBody">
                                <tr class="text-center" id="emptyRow">
                                    <td colspan="8" class="py-4">
                                        <p class="text-muted mb-0">हालसम्म कुनै रेकर्ड फेला परेन। <a href="/form">नयाँ
                                                थप्नुहोस्</a></p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>

                        <!-- Pagination Controls -->
                        <nav aria-label="Table pagination" class="mt-3">
                            <ul class="pagination justify-content-center" id="paginationControls">
                                <!-- Pagination will be generated by JavaScript -->
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Edit Distribution Modal -->
<div class="modal fade" id="editModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title"><i class="bi bi-pencil-square"></i> विवरण सम्पादन गर्नुहोस्</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="editForm" enctype="multipart/form-data">
                    <input type="hidden" id="edit_id" name="edit_id">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label"><i class="bi bi-person"></i> लाभग्राहिको नाम थर</label>
                            <input type="text" class="form-control" id="edit_beneficiary_name"
                                placeholder="लाभग्राहिको नाम लेख्नुहोस्" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label"><i class="bi bi-telephone"></i> फोन नम्बर</label>
                            <input type="tel" class="form-control" id="edit_phone">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label"><i class="bi bi-geo-alt"></i> ठेगाना/स्थान</label>
                            <input type="text" class="form-control" id="edit_location" placeholder="स्थान लेख्नुहोस्"
                                required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label"><i class="bi bi-cash-coin"></i> प्राप्त नगद रकम</label>
                            <input type="number" class="form-control" id="edit_cash_received" step="0.01">
                        </div>
                    </div>
                    <div class="card border-info mb-3">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0"><i class="bi bi-bag"></i> राहात सामाग्री विवरण</h6>
                        </div>
                        <div class="card-body">
                            <div id="editItemsContainer"></div>
                            <button type="button" class="btn btn-sm btn-success mt-2" onclick="addEditItemRow()">
                                <i class="bi bi-plus-circle"></i> सामाग्री थप्नुहोस्
                            </button>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label"><i class="bi bi-check-circle"></i> स्थिति (Status)</label>
                        <select class="form-control" id="edit_status">
                            <option value="Distributed">वितरण गरियो</option>
                            <option value="Pending">बाँकी</option>
                            <option value="In Progress">प्रक्रियामा</option>
                            <option value="Delivered">पुर्याइयो</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label"><i class="bi bi-pencil-square"></i> थप टिप्पणी (Notes)</label>
                        <textarea class="form-control" id="edit_notes" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">रद्द गर्नुहोस्</button>
                <button type="button" class="btn btn-primary" onclick="saveEdit()">परिवर्तन सुरक्षित गर्नुहोस्</button>
            </div>
        </div>
    </div>
</div>

{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}

//MAP Feature
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disaster & Relief GIS Map - LEOC</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        #map {
            height: 100vh;
            width: 100%;
        }
        .legend {
            padding: 6px 8px;
            font: 14px Arial, Helvetica, sans-serif;
            background: white;
            background: rgba(255,255,255,0.8);
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 5px;
        }
        .legend i {
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.7;
        }
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            display: none;
        }
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        // Initialize the map
        const map = L.map('map', {
            minZoom: 10,  // Minimum zoom to prevent going beyond boundaries
            maxZoom: 18,
            worldCopyJump: false  // Prevents showing multiple worlds when zooming out
        }).setView([29.47, 81.0], 12);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Add Esri World Imagery as an alternative layer
        const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        });

        // Add layer control
        const baseLayers = {
            "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }),
            "Satellite View": esriSatellite
        };

        L.control.layers(baseLayers).addTo(map);

        // Variables to store boundary data
        let boundaryBounds = null;
        let municipalityBoundaryLayer = null;

        // Define marker clusters for better performance
        const distributionMarkers = L.layerGroup().addTo(map);
        const disasterMarkers = L.layerGroup().addTo(map);
        const wardBoundaries = L.layerGroup().addTo(map);
        const boundaryLayer = L.layerGroup();  // This is the layer group for municipality boundary (not added to map by default)

        // Add layer control for markers
        const overlays = {
            "Relief Distributions": distributionMarkers,
            "Disasters": disasterMarkers,
            "Wards": wardBoundaries,
            "Thalara Boundary": boundaryLayer
        };
        L.control.layers(null, overlays, {collapsed: false}).addTo(map);

        // Function to show loading overlay
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }

        // Function to hide loading overlay
        function hideLoading() {
            document.getElementById('loadingOverlay').style.display = 'none';
        }

        // Function to format tooltip content
        function formatDistributionTooltip(dist) {
            return `
                <div>
                    <h5 style="margin: 0 0 10px 0; color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 5px; font-size: 16px;">Relief Distribution</h5>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Disaster:</b> ${dist.disaster_type || 'N/A'} (${dist.disaster_date || 'N/A'})</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Beneficiary:</b> ${dist.beneficiary_name}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Location:</b> ${dist.location}, Ward ${dist.ward}</p>
                    <p style="margin: 5px 0; color: #198754; font-size: 14px;"><b>Relief Items:</b> ${dist.relief_items || 'N/A'}</p>
                    <p style="margin: 5px 0; color: #0d6efd; font-size: 14px;"><b>Cash:</b> ₹${dist.cash_received?.toFixed(2) || '0.00'}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Notes:</b> ${dist.notes || 'N/A'}</p>
                    <p style="margin: 5px 0; font-size: 12px;"><small>ID: ${dist.id}</small></p>
                </div>
            `;
        }

        function formatDisasterTooltip(disaster) {
            return `
                <div>
                    <h5 style="margin: 0 0 10px 0; color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 5px; font-size: 16px;">Disaster Record</h5>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Type:</b> ${disaster.disaster_type}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Date:</b> ${disaster.disaster_date}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Ward:</b> ${disaster.ward}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Affected Households:</b> ${disaster.affected_households}</p>
                    <p style="margin: 5px 0; font-size: 14px;"><b>Affected People:</b> ${disaster.affected_people}</p>
                </div>
            `;
        }

        // Function to load map data
        async function loadMapData() {
            showLoading();

            try {
                // Load map data (distributions and disasters)
                const mapResponse = await fetch('/api/map-data');
                const mapData = await mapResponse.json();

                if (mapData.success) {
                    // Clear existing markers
                    distributionMarkers.clearLayers();
                    disasterMarkers.clearLayers();

                    // Add distribution markers
                    mapData.distributions.forEach(dist => {
                        const marker = L.marker([dist.latitude, dist.longitude], {
                            icon: L.divIcon({
                                className: 'custom-div-icon',
                                html: "<div class='marker-pin' style='background-color:#dc3545; width: 32px; height: 32px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center;'><i class='bi bi-home' style='transform: rotate(45deg); color:white !important; font-size:18px; line-height:1;'></i></div>",
                                iconSize: [32, 32],
                                iconAnchor: [16, 32]
                            })
                        })
                        .bindTooltip(formatDistributionTooltip(dist), {
                            permanent: false,
                            direction: 'top',
                            className: 'custom-tooltip'
                        });

                        distributionMarkers.addLayer(marker);
                    });

                    // Add disaster markers
                    mapData.disasters.forEach(disaster => {
                        const marker = L.marker([disaster.latitude, disaster.longitude], {
                            icon: L.divIcon({
                                className: 'custom-div-icon',
                                html: "<div class='marker-pin' style='background-color:#0d6efd; width: 32px; height: 32px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center;'><i class='bi bi-home' style='transform: rotate(45deg); color:white !important; font-size:18px; line-height:1;'></i></div>",
                                iconSize: [30, 30],
                                iconAnchor: [15, 30]
                            })
                        })
                        .bindTooltip(formatDisasterTooltip(disaster), {
                            permanent: false,
                            direction: 'top',
                            className: 'custom-tooltip'
                        });

                        disasterMarkers.addLayer(marker);
                    });

                    // Fit bounds to show all markers if any exist
                    if (mapData.distributions.length > 0 || mapData.disasters.length > 0) {
                        const allCoords = [
                            ...mapData.distributions.map(d => [d.latitude, d.longitude]),
                            ...mapData.disasters.map(d => [d.latitude, d.longitude])
                        ];

                        if (allCoords.length > 0) {
                            const group = new L.featureGroup([
                                ...mapData.distributions.map(d => L.marker([d.latitude, d.longitude])),
                                ...mapData.disasters.map(d => L.marker([d.latitude, d.longitude]))
                            ]);
                            map.fitBounds(group.getBounds().pad(0.1));
                        }
                    }
                }

                // Load ward boundaries
                try {
                    const wardsResponse = await fetch('/thalara_wards.json');
                    if (wardsResponse.ok) {
                        const wardsData = await wardsResponse.json();

                        wardBoundaries.clearLayers();

                        L.geoJSON(wardsData, {
                            style: function(feature) {
                                return {
                                    fillColor: '#ffeb3b',
                                    color: '#fbc02d',
                                    weight: 1.5,
                                    fillOpacity: 0.15
                                };
                            },
                            onEachFeature: function(feature, layer) {
                                // Add tooltip
                                if (feature.properties && feature.properties.name) {
                                    layer.bindTooltip(`Ward: ${feature.properties.name}`, {
                                        sticky: false
                                    });

                                    // Add popup
                                    layer.bindPopup(`<b>Ward:</b> ${feature.properties.name}`);
                                }

                                // Highlight on mouseover
                                layer.on({
                                    mouseover: function(e) {
                                        this.setStyle({
                                            weight: 2.5,
                                            fillOpacity: 0.25
                                        });
                                    },
                                    mouseout: function(e) {
                                        this.setStyle({
                                            weight: 1.5,
                                            fillOpacity: 0.15
                                        });
                                    }
                                });
                            }
                        }).addTo(wardBoundaries);
                    }
                } catch (error) {
                    console.error('Error loading ward boundaries:', error);
                }

                // Load municipality boundary
                try {
                    const boundaryResponse = await fetch('/thalara_boundary.json');
                    if (boundaryResponse.ok) {
                        const boundaryData = await boundaryResponse.json();

                        // Create new boundary geojson layer
                        const newBoundaryLayer = L.geoJSON(boundaryData, {
                            style: function(feature) {
                                return {
                                    fillColor: 'transparent',
                                    color: '#0d6efd',
                                    weight: 3,
                                    opacity: 0.8
                                };
                            },
                            onEachFeature: function(feature, layer) {
                                layer.bindPopup('<b>Thalara Municipality Boundary</b>');
                            }
                        });

                        // Clear the existing boundary layer from the layer group
                        boundaryLayer.clearLayers();

                        // Add the new boundary to the layer group
                        newBoundaryLayer.eachLayer(layer => {
                            boundaryLayer.addLayer(layer);
                        });

                        // Calculate bounds from the boundary geometry
                        if (boundaryData && boundaryData.features && boundaryData.features.length > 0) {
                            const geom = boundaryData.features[0].geometry;
                            if (geom) {
                                // Calculate bounds from coordinates
                                let lats = [];
                                let lons = [];

                                function extractCoords(coords) {
                                    for (let c of coords) {
                                        if (typeof c[0] === 'number' && typeof c[1] === 'number') {
                                            lons.push(c[0]);
                                            lats.push(c[1]);
                                        } else {
                                            extractCoords(c);
                                        }
                                    }
                                }

                                if (geom.type === 'Polygon') {
                                    extractCoords(geom.coordinates[0]); // Exterior ring
                                } else if (geom.type === 'MultiPolygon') {
                                    for (let polygon of geom.coordinates) {
                                        extractCoords(polygon[0]); // Exterior ring of each polygon
                                    }
                                }

                                if (lats.length > 0 && lons.length > 0) {
                                    boundaryBounds = L.latLngBounds(
                                        [Math.min(...lats), Math.min(...lons)],
                                        [Math.max(...lats), Math.max(...lons)]
                                    );

                                    // Set maximum bounds to prevent panning outside boundary
                                    map.setMaxBounds(boundaryBounds.pad(0.1));

                                    // Fit map to boundary initially
                                    map.fitBounds(boundaryBounds);

                                    // Add event listener to enforce bounds
                                    map.on('moveend', function() {
                                        if (!boundaryBounds.contains(map.getBounds().getNorthWest()) ||
                                            !boundaryBounds.contains(map.getBounds().getSouthEast())) {
                                            map.fitBounds(boundaryBounds, { animate: false });
                                        }
                                    });
                                }
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error loading municipality boundary:', error);
                }

            } catch (error) {
                console.error('Error loading map data:', error);
            } finally {
                hideLoading();
            }
        }

        // Load data when map is ready
        map.whenReady(() => {
            loadMapData();

            // Refresh data every 30 seconds
            setInterval(loadMapData, 30000);
        });

        // Add zoom restriction to prevent zooming out too far
        map.on('zoomend', function() {
            if (map.getZoom() < 10) {
                map.setZoom(10);
            }
        });

        // Add custom CSS for tooltips
        const style = document.createElement('style');
        style.innerHTML = `
            .custom-tooltip {
                background: rgba(255, 255, 255, 0.95) !important;
                border: 2px solid #ddd !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
                padding: 10px !important;
                border-radius: 8px !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
                font-size: 14px !important;
                color: #333 !important;
                max-width: 350px !important;
            }
            .marker-pin {
                position: relative;
                overflow: visible;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            .marker-pin i {
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .marker-pin:after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid currentColor;
                filter: brightness(30%);
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>