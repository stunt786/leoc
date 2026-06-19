# Disaster Reports → Daily Bulletin — UI Update Complete ✅

## Changes Made

### 1. `templates/disaster_reports.html` — Complete UI Redesign
- Renamed page from "Disaster Reports" to **"Daily Bulletin"**
- **Removed** the old disaster assessment form (human impact, property damage, livestock, infrastructure sections)
- **Kept** the incident selection concept — rebuilt as a checkbox table with:
  - Filters by ward, disaster type, and search
  - Select All / Clear buttons
  - Live stats sidebar showing totals for selected incidents
- **Added new form fields:**
  - Public Notice Title (required)
  - Public Notice Description
  - Priority (Low / Medium / High / Critical)
  - Valid Date From / To (BS calendar)
  - Today's Weather Status (dropdown: Sunny, Cloudy, Rainy, etc.)
  - Incidents Reporting Status (dropdown)
  - Next Update (date + time inputs)
  - Situation Summary & Resources Deployed textareas
- **Action bar** at top right with:
  - Print Preview → opens `/daily-report-preview` with date params
  - PDF Download → opens `/api/generate-daily-report` with date params
  - Save Bulletin → POSTs to `/api/daily-bulletins`
- **Right sidebar** with:
  - Selected incidents live stats
  - Priority guide
  - Recent bulletins list (placeholder)

### 2. `templates/daily_report_print.html` — Full Print Template (851 lines)
- Replaced with full reference design matching `incident.md` specification
- **Disaster Type Summary** now has all 14 columns (matching reference):
  - विपद्, जम्मा, मृत्यु पुरुष, मृत्यु महिला, बेपत्ता, घाइते पुरुष, घाइते महिला
  - प्रभावित परिवार, घर आं.क्षति, घर पूर्ण.क्षति, सा.भवन आं.क्षति, सा.भवन पुर्ण.क्षति, पशु, अ.क्षति
  - Empty state: "कुनै घटना रिपोर्ट गरिएको छैन" row when no data
- Other sections matching reference:
  - Nepali-language header with LEOC branding, emblem
  - "दैनिक विपद् बुलेटीन" title, Sit-Rep number box
  - Date filter selector (fixed, no-print) + Print & PDF buttons
  - Public notice section (conditional)
  - 6-card stats row with gradient backgrounds
  - Ward-wise incident table with infrastructure icons
  - Infrastructure status grid
  - Situation report summary
  - **Recent Events / Event Logs** table (conditional)
  - **Public Advisories** section (conditional)
  - Footer with generation timestamp
  - Full A4 print CSS (@page, @media print)

### 3. `app.py` — Route Updates
- `daily_report_preview()` now passes additional context vars:
  - `weather_status`, `notice_title`, `notice_description`, `notice_priority`
  - `incident_reporting_status`, `situation_summary`, `resources_deployed`, `next_update`
- Added stub `POST /api/daily-bulletins` route (returns success, no DB write yet)

## Next Step: Database Integration
When ready, implement:
1. `DailyBulletin` model in SQLAlchemy
2. Update `POST /api/daily-bulletins` to persist bulletin + linked incidents
3. Update `/daily-report-preview` to load from DB instead of query params
4. Add GET list endpoint for recent bulletins sidebar
5. Add edit/delete functionality for saved bulletins
