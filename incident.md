**Update 'Beneficaries' page form and add following fields in reference form and match fields to existing forrm fields 
{% extends "base.html" %}

{% block title %}नयाँ राहात वितरण - LEOC{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">
                        <i class="bi bi-clipboard-plus"></i> राहात वितरण फारम
                    </h4>
                    <button class="btn btn-warning btn-sm" id="unlockFormBtn" onclick="unlockForm()">
                        <i class="bi bi-unlock-fill"></i> विवरण भर्नका लागि अनलक गर्नुहोस्
                    </button>
                </div>
                <div class="card-body p-4">
                    <form id="distributionForm" enctype="multipart/form-data">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
                        <!-- BENEFICIARY INFORMATION -->
                        <div class="card border-primary mb-4">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-person-vcard"></i> लाभग्राहि विवरण</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <!-- Beneficiary Name -->
                                    <div class="col-md-6 mb-3">
                                        <label for="beneficiary_name" class="form-label">
                                            <i class="bi bi-person"></i> लाभग्राहि नाम थर *
                                        </label>
                                        <input type="text" class="form-control" id="beneficiary_name"
                                            name="beneficiary_name" required placeholder="नाम थर लेख्नुहोस्"
                                            minlength="3" oninput="validateField('beneficiary_name')">
                                        <small class="text-muted">लाभग्राहिको पूरा नाम (कम्तिमा ३ अक्षर)</small>
                                        <div id="beneficiary_name_error" class="invalid-feedback d-block"></div>
                                    </div>

                                    <!-- Beneficiary ID -->
                                    <div class="col-md-6 mb-3">
                                        <label for="beneficiary_id" class="form-label">
                                            <i class="bi bi-card-list"></i> लाभग्राहि ना.प्र.प्र नं *
                                        </label>
                                        <input type="text" class="form-control" id="beneficiary_id"
                                            name="beneficiary_id" required placeholder="उदा: BEN-001" minlength="2"
                                            oninput="validateField('beneficiary_id')">
                                        <small class="text-muted">लाभग्राहिको विशिष्ट पहिचान नम्बर (कम्तिमा २
                                            अक्षर)</small>
                                        <div id="beneficiary_id_error" class="invalid-feedback d-block"></div>
                                    </div>
                                </div>

                                <div class="row">
                                    <!-- Father's Name -->
                                    <div class="col-md-6 mb-3">
                                        <label for="father_name" class="form-label">
                                            <i class="bi bi-person-fill"></i> बुवाको नाम थर
                                        </label>
                                        <input type="text" class="form-control" id="father_name" name="father_name"
                                            placeholder="बुवाको नाम थर लेख्नुहोस्">
                                        <small class="text-muted">पहिचानका लागि बुवाको नाम थर</small>
                                    </div>

                                    <!-- Phone -->
                                    <div class="col-md-6 mb-3">
                                        <label for="phone" class="form-label">
                                            <i class="bi bi-telephone"></i> फोन नम्बर *
                                        </label>
                                        <input type="tel" class="form-control" id="phone" name="phone"
                                            placeholder="९८४१००००००" minlength="7" oninput="validateField('phone')">
                                        <small class="text-muted">लाभग्राहिको सम्पर्क नम्बर (कम्तिमा १० अंक)</small>
                                        <div id="phone_error" class="invalid-feedback d-block"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- DISASTER INFORMATION -->
                        <div class="card border-danger mb-4">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-exclamation-triangle"></i> विपद् घटना सम्बन्धी विवरण
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <!-- Disaster Date (Nepali Calendar) -->
                                    <div class="col-md-6 mb-3">
                                        <label for="disaster_date" class="form-label">
                                            <i class="bi bi-calendar"></i> घटना घट्टेको मिति (BS) *
                                        </label>
                                        <input type="text" class="form-control" id="disaster_date" name="disaster_date"
                                            required placeholder="२०८०-१०-१५" pattern="\d{4}-\d{2}-\d{2}"
                                            oninput="validateField('disaster_date')">
                                        <small class="text-muted">नेपाली मिति ढाँचा: वर्ष-महिना-गते (उदा:
                                            २०८०-१०-१५)</small>
                                        <div id="disaster_date_error" class="invalid-feedback d-block"></div>
                                        <div id="nepaliDateHelper" class="mt-2">
                                            <a href="#" onclick="openNepaliCalendar(); return false;"
                                                class="btn btn-sm btn-outline-primary">
                                                <i class="bi bi-calendar2-event"></i> मिति छानौट गर्नुहोस्
                                            </a>
                                        </div>
                                    </div>

                                    <!-- Disaster Type -->
                                    <div class="col-md-6 mb-3">
                                        <label for="disaster_type" class="form-label">
                                            <i class="bi bi-bookmark"></i> विपद्को प्रकार *
                                        </label>
                                        <select class="form-control" id="disaster_type" name="disaster_type" required
                                            onchange="validateField('disaster_type')">
                                            <option value="">-- Loading --</option>
                                        </select>
                                        <small class="text-muted">विपद्को मुख्य प्रकार</small>
                                    </div>
                                </div>

                                <div class="row">
                                    <!-- Fiscal Year -->
                                    <div class="col-md-4 mb-3">
                                        <label for="fiscal_year" class="form-label">
                                            <i class="bi bi-calendar2"></i> आर्थिक वर्ष *
                                        </label>
                                        <select class="form-control" id="fiscal_year" name="fiscal_year">
                                            <option value="">-- Loading --</option>
                                        </select>
                                        <small class="text-muted">चालु आर्थिक वर्ष (उदा: २०८०/८१)</small>
                                    </div>

                                    <!-- Ward -->
                                    <div class="col-md-4 mb-3">
                                        <label for="ward" class="form-label">
                                            <i class="bi bi-map"></i> वडा नं *
                                        </label>
                                        <select class="form-control" id="ward" name="ward" required>
                                            <option value="">-- वडा छान्नुहोस् --</option>
                                            <option value="1">वडा नं १</option>
                                            <option value="2">वडा नं २</option>
                                            <option value="3">वडा नं ३</option>
                                            <option value="4">वडा नं ४</option>
                                            <option value="5">वडा नं ५</option>
                                            <option value="6">वडा नं ६</option>
                                            <option value="7">वडा नं ७</option>
                                            <option value="8">वडा नं ८</option>
                                            <option value="9">वडा नं ९</option>
                                        </select>
                                        <small class="text-muted">प्रशासकीय वडा नम्बर (१-९)</small>
                                    </div>

                                    <!-- Tole -->
                                    <div class="col-md-4 mb-3">
                                        <label for="tole" class="form-label">
                                            <i class="bi bi-signpost"></i> टोल
                                        </label>
                                        <input type="text" class="form-control" id="tole" name="tole"
                                            placeholder="टोलको नाम">
                                        <small class="text-muted">गाउँ वा टोलको नाम</small>
                                    </div>
                                </div>

                                <div class="row">
                                    <!-- Location/Building -->
                                    <div class="col-md-6 mb-3">
                                        <label for="location" class="form-label">
                                            <i class="bi bi-building"></i> स्थायी बसोबास ठेगाना *
                                        </label>
                                        <input type="text" class="form-control" id="location" name="location" required
                                            placeholder="उदा: थलारा-१, पिठाकोट" minlength="3"
                                            oninput="validateField('location')">
                                        <small class="text-muted">स्थायी ठेगाना वा घर नम्बर (कम्तिमा ३ अक्षर)</small>
                                        <div id="location_error" class="invalid-feedback d-block"></div>
                                    </div>

                                    <!-- Current Shelter Location -->
                                    <div class="col-md-6 mb-3">
                                        <label for="current_shelter_location" class="form-label">
                                            <i class="bi bi-house"></i> हाल बसोबास स्थान
                                        </label>
                                        <input type="text" class="form-control" id="current_shelter_location"
                                            name="current_shelter_location" placeholder="अहिले कहाँ बसिरहनुभएको छ?">
                                        <small class="text-muted">विस्थापित भएको भए हालको बसाइ स्थान</small>
                                    </div>
                                </div>

                                <div class="row">
                                    <!-- Latitude -->
                                    <div class="col-md-6 mb-3">
                                        <label for="latitude" class="form-label">
                                            <i class="bi bi-geo-alt"></i> आक्षांश (Latitude)
                                        </label>
                                        <input type="number" class="form-control" id="latitude" name="latitude"
                                            step="0.000001" placeholder="उदा: २७.७१७२४५" min="-90" max="90"
                                            oninput="validateField('latitude')">
                                        <small class="text-muted">भौगोलिक आक्षांश (-९० देखि ९० सम्म)</small>
                                        <div id="latitude_error" class="invalid-feedback d-block"></div>
                                    </div>

                                    <!-- Longitude -->
                                    <div class="col-md-6 mb-3">
                                        <label for="longitude" class="form-label">
                                            <i class="bi bi-geo-alt"></i> देशान्तर (Longitude)
                                        </label>
                                        <input type="number" class="form-control" id="longitude" name="longitude"
                                            step="0.000001" placeholder="उदा: ८५.३२४०२१" min="-180" max="180"
                                            oninput="validateField('longitude')">
                                        <small class="text-muted">भौगोलिक देशान्तर (-१८० देखि १८० सम्म)</small>
                                        <div id="longitude_error" class="invalid-feedback d-block"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- FAMILY DETAILS -->
                        <div class="card border-success mb-4">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-people"></i> पारिवारिक विवरण</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <!-- Male Count -->
                                    <div class="col-md-3 mb-3">
                                        <label for="male_count" class="form-label">
                                            <i class="bi bi-person"></i> पुरुष संख्या
                                        </label>
                                        <input type="number" class="form-control" id="male_count" name="male_count"
                                            min="0" value="0">
                                        <small class="text-muted">परिवारमा रहेका पुरुषको संख्या</small>
                                    </div>

                                    <!-- Female Count -->
                                    <div class="col-md-3 mb-3">
                                        <label for="female_count" class="form-label">
                                            <i class="bi bi-person-fill"></i> महिला संख्या
                                        </label>
                                        <input type="number" class="form-control" id="female_count" name="female_count"
                                            min="0" value="0">
                                        <small class="text-muted">परिवारमा रहेका महिलाको संख्या</small>
                                    </div>

                                    <!-- Children Count -->
                                    <div class="col-md-3 mb-3">
                                        <label for="children_count" class="form-label">
                                            <i class="bi bi-person-check"></i> बालबालिका संख्या
                                        </label>
                                        <input type="number" class="form-control" id="children_count"
                                            name="children_count" min="0" value="0">
                                        <small class="text-muted">१८ वर्ष मुनिका बालबालिका संख्या</small>
                                    </div>

                                    <!-- Deaths -->
                                    <div class="col-md-3 mb-3">
                                        <label for="deaths_during_disaster" class="form-label">
                                            <i class="bi bi-exclamation-lg"></i> विपद्बाट मृतक संख्या
                                        </label>
                                        <input type="number" class="form-control" id="deaths_during_disaster"
                                            name="deaths_during_disaster" min="0" value="0">
                                        <small class="text-muted">विपद्का कारण ज्यान गुमाउनेको संख्या</small>
                                    </div>
                                </div>

                                <div class="row">
                                    <!-- Pregnant Mother Count -->
                                    <div class="col-md-6 mb-3">
                                        <label for="pregnant_mother_count" class="form-label">
                                            <i class="bi bi-heart"></i> सुत्केरी महिला
                                        </label>
                                        <input type="number" class="form-control" id="pregnant_mother_count"
                                            name="pregnant_mother_count" min="0" value="0">
                                        <small class="text-muted">परिवारमा रहेका गर्भवती वा सुत्केरीको संख्या</small>
                                    </div>

                                    <!-- Mother with Under 2 Baby -->
                                    <div class="col-md-6 mb-3">
                                        <label for="mother_under_2_baby" class="form-label">
                                            <i class="bi bi-stars"></i> स्तनपान गर्दै गरेको बच्चा भएको आमा
                                        </label>
                                        <input type="number" class="form-control" id="mother_under_2_baby"
                                            name="mother_under_2_baby" min="0" value="0">
                                        <small class="text-muted">२ वर्ष मुनिका बच्चा भएका आमाहरूको संख्या</small>
                                    </div>
                                </div>

                                <!-- Detailed Family Members -->
                                <div class="mb-3">
                                    <label class="form-label"><i class="bi bi-list-ul"></i> परिवार सदस्य विवरण</label>
                                    <div id="familyMembersContainer"></div>
                                    <button type="button" class="btn btn-success btn-sm mt-2"
                                        onclick="addFamilyMember()">
                                        <i class="bi bi-plus-circle"></i> परिवार सदस्य थप
                                    </button>
                                    <input type="hidden" id="family_members_json" name="family_members_json" value="[]">
                                </div>
                            </div>
                        </div>

                        <!-- SOCIAL SECURITY & POVERTY -->
                        <div class="card border-warning mb-4">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-shield-check"></i> सामाजिक सुरक्षा र स्थिति</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <!-- Social Security Fund -->
                                    <div class="col-md-4 mb-3">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="in_social_security_fund"
                                                name="in_social_security_fund">
                                            <label class="form-check-label" for="in_social_security_fund">
                                                सामाजिक सुरक्षा कोषमा आबद्ध छ/छैन
                                            </label>
                                        </div>
                                        <small class="text-muted">के लाभग्राहि सामाजिक सुरक्षा योजनामा
                                            हुनुहुन्छ?</small>
                                    </div>

                                    <!-- SSF Type -->
                                    <div class="col-md-4 mb-3" id="ssf_type_div" style="display:none;">
                                        <label for="ssf_type" class="form-label">सा.सु प्रकार</label>
                                        <select class="form-control" id="ssf_type" name="ssf_type">
                                            <option value="">-- छान्नुहोस् --</option>
                                            <!-- Options will be populated dynamically -->
                                        </select>
                                        <script>
                                            // Dynamically populate SSF types from backend settings
                                            async function populateSSFTypes() {
                                                try {
                                                    const response = await fetch('/api/settings/ssf_types');
                                                    const result = await response.json();
                                                    if (result.success && Array.isArray(result.value)) {
                                                        const select = document.getElementById('ssf_type');
                                                        // Remove all except the first option
                                                        while (select.options.length > 1) select.remove(1);
                                                        result.value.forEach(type => {
                                                            const opt = document.createElement('option');
                                                            opt.value = type;
                                                            opt.textContent = type;
                                                            select.appendChild(opt);
                                                        });
                                                    }
                                                } catch (e) {
                                                    // Optionally handle error
                                                }
                                            }
                                            // Call on page load
                                            document.addEventListener('DOMContentLoaded', populateSSFTypes);
                                        </script>
                                    </div>

                                    <!-- Poverty Card Holder -->
                                    <div class="col-md-4 mb-3">
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="poverty_card_holder"
                                                name="poverty_card_holder">
                                            <label class="form-check-label" for="poverty_card_holder">
                                                गरिब परिचयपत्र छ/छैन
                                            </label>
                                        </div>
                                        <small class="text-muted">के लाभग्राहिसँग गरिब परिचयपत्र छ?</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- HARMS/DAMAGES -->
                        <div class="card border-danger mb-4">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-bandaid"></i> हानि र क्षति</h5>
                            </div>
                            <div class="card-body">
                                <label class="form-label">हानिको विवरण</label>
                                <div id="harmsContainer"></div>
                                <button type="button" class="btn btn-danger btn-sm mt-2" onclick="addHarmRow()">
                                    <i class="bi bi-plus-circle"></i> हानि थप्नुहोस्
                                </button>
                                <input type="hidden" id="harms_json" name="harms_json" value="[]">
                            </div>
                        </div>

                        <!-- BANK ACCOUNT DETAILS -->
                        <div class="card border-info mb-4">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-bank"></i> बैंक खाता विवरण</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <!-- Account Holder Name -->
                                    <div class="col-md-6 mb-3">
                                        <label for="bank_account_holder_name" class="form-label">
                                            <i class="bi bi-person"></i> खाताबालाको नाम अङ्रेजिमा
                                        </label>
                                        <input type="text" class="form-control" id="bank_account_holder_name"
                                            placeholder="बैंक खातामा भएको नाम (English मा)">
                                        <small class="text-muted">बैंक खातामा उल्लेखित नाम</small>
                                    </div>

                                    <!-- Account Number -->
                                    <div class="col-md-6 mb-3">
                                        <label for="bank_account_number" class="form-label">
                                            <i class="bi bi-credit-card"></i> खाता नंम्बर
                                        </label>
                                        <input type="text" class="form-control" id="bank_account_number"
                                            name="bank_account_number" placeholder="बैंक खाता नम्बर लेख्नुहोस्">
                                        <small class="text-muted">बैंकको खाता नम्बर</small>
                                    </div>
                                </div>

                                <div class="row">
                                    <!-- Bank Name -->
                                    <div class="col-md-12 mb-3">
                                        <label for="bank_name" class="form-label">
                                            <i class="bi bi-bank2"></i> बैंकको नाम
                                        </label>
                                        <input type="text" class="form-control" id="bank_name" name="bank_name"
                                            placeholder="उदा: राष्ट्रिय वाणिज्य बैंक लिमिटेड">
                                        <small class="text-muted">बैंकको पूरा नाम</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                       
                        <div class="row">
                            <!-- Image Upload -->
                            <div class="col-md-6 mb-3">
                                <label for="image" class="form-label">
                                    <i class="bi bi-image"></i> प्रमाण फोटो
                                </label>
                                <input type="file" class="form-control" id="image" name="image" accept="image/*">
                                <small class="text-muted">प्रमाण स्वरूप फोटो (ऐच्छिक)</small>
                            </div>

                            <!-- Documents Upload -->
                            <div class="col-md-6 mb-3">
                                <label for="documents" class="form-label">
                                    <i class="bi bi-file-earmark"></i> सम्बन्धित कागजातहरू
                                </label>
                                <input type="file" class="form-control" id="documents" name="documents" multiple
                                    accept=".pdf,.doc,.docx,.jpg,.png">
                                <small class="text-muted">भरपाई, नागरिकता, फोटो आदि</small>
                            </div>
                        </div>

                        <!-- Image Preview -->
                        <div id="imagePreview" class="mb-3" style="display: none;">
                            <img id="previewImage" src="" alt="Preview" class="img-fluid rounded"
                                style="max-height: 200px;">
                        </div>

                       

                </div>
            </div>

            <!-- Alert Box -->
            <div id="alertBox" class="mt-3" style="display: none;"></div>
        </div>
    </div>
</div>
{% endblock %}


** After adding form, match the data with it's corresponding other pages like Distribution...
** Don't mess existing functionality.
** DOn't add Fields that are auto poplated like current fiscal_year,