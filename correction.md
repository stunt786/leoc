

#Alert/Notification system: Add alert and notification system and update below information. Alert and notification should be viewable for details in another notification page and add clear notification button to clear all existing ones and ready for new ones. Add some animated flash notifications for high alert notifications. Check status 24 hrs and re-show notifications for low stocks, expired items, active incidents. Show until they are updated. 
**All stock receipts notification and also update in logs
**All Stock transfer and adjustments also in logs
**All Stock Items low, expiry status, status
**All Incidents 
**All Relief Requests
**All Dispatches
**All Distributions
**All cash request and distributions

Implementation Plan - Alert Notification System
This document outlines the design and integration plan for implementing the persistent Alert and Notification system for the LEOC project.

User Review Required
IMPORTANT

The database schema changes require adding a new table notification. This will be auto-created at start-up by the application's existing init_db() call which runs db.create_all().

All active incidents, low-stock items, expired/expiring items, and creation events (receipts, transfers, adjustments, relief requests, dispatches, distributions, cash requests) will generate persistent DB-backed notifications.

High-priority notifications will display on all pages as floating, animated, pulsing banners. Dismissing them will clear them from the DB, ensuring they do not annoy the user.

Proposed Changes
We will introduce a database-backed notification model, refactor the existing /api/notifications API endpoint, add endpoints to clear single/all notifications, add a dedicated View All Notifications page, and implement animated high-alert components.

Backend Components
[MODIFY] 
app.py
Add Notification Model: Create a SQL-Alchemy model class Notification:

id: Integer primary key
title: String
message: Text
type: String (e.g. low_stock, expiry, incident, stock_receipt, etc.)
priority: String (Low, Medium, High, Urgent)
resource_id: String (used for persistent status tracking/matching)
url: String (path to detail/management page)
cleared: Boolean (default False)
created_at: DateTime
cleared_at: DateTime
to_dict() helper.
Add Status-Checking & Re-surfacing Helpers:

check_time_elapsed(cleared_at): Safely checks if 24 hours have elapsed since a notification was cleared, handling timezone-aware/naive datetimes.
check_and_update_persistent_notifications(): Evaluates active system state (Active Incidents, Low stock items, Out of stock items, Expired / Expiring items). Creates notifications if they don't exist. Re-surfaces them if they were cleared > 24 hours ago. Automatically clears notifications if the underlying status is resolved.
create_notification(...): Helper to write arbitrary system notifications (like creation of transfers, receipts, etc.).
Hook Notifications into Entity Creation Endpoints:

handle_stock_receipts(): Call create_notification() on successful POST.
handle_stock_transfers(): Call create_notification() on successful POST.
handle_adjustments(): Call create_notification() on successful POST.
handle_incidents(): Call create_notification() on successful POST (using incident severity for priority).
handle_relief_requests(): Call create_notification() on successful POST (and also trigger cash request notification if cash request is auto-created).
handle_dispatches(): Call create_notification() on successful POST.
handle_distributions(): Call create_notification() on successful POST.
handle_cash_requests(): Call create_notification() on successful POST.
handle_cash_distributions(): Call create_notification() on successful POST.
Update Notification Endpoints & Add Page Endpoint:

Refactor get_notifications(): Execute check_and_update_persistent_notifications() and return active uncleared notifications.
Add /api/notifications/<int:id>/clear (POST) to clear a single notification.
Add /api/notifications/clear (POST) to clear all notifications.
Add /notifications route rendering notifications.html.
Frontend Components
[NEW] 
notifications.html
A dedicated, premium page displaying all notifications:

Display layout: Filters (All, System, Inventory, Finance, Incidents) + "Clear All" action button.
Cards showing notification detail, timestamp (Nepalese formatted), link/button to view source resource, and a "Clear" button to archive the alert.
[MODIFY] 
base.html
Append a global floating container <div class="high-alert-container" id="highAlertContainer"></div> for animated overlays.
Update header notification dropdown footer to link to /notifications.
[MODIFY] 
base.js
Refactor loadNotifications and renderNotifications to show the DB-backed alerts.
Extract priority === 'High' or priority === 'Urgent' alerts to render them as floating animated cards inside #highAlertContainer.
Manage high alert card lifecycle (slide-in, pulsing border, fade-out on close button click, and making a POST to clear them from DB).
[MODIFY] 
style.css
Add style definitions for .high-alert-container, .high-alert-card, .high-alert-icon, and animations (slideInRight, fadeOutRight, pulseBorder, pulseIcon).
Add styling for the dedicated /notifications page cards and filter controls.
Verification Plan
Automated Tests
Run existing integration tests to ensure current app functionality is intact: pytest tests/test_05_auth_rbac.py
Create a new integration test script tests/test_notifications.py to test creation, clearing, status-checking, and 24h resurfacing of notifications.
Manual Verification
Open the browser and log in to the application.
Verify that creating a stock receipt, transfer, incident, relief request, etc. generates notifications in the dropdown dropdown immediately.
Visit the dedicated /notifications page, select different categories, clear one alert, and check that it is archived.
Click "Clear All" and verify the list is cleared.
Create a high severity incident and verify the red floating flash alert card appears with animations.
Verify responsive layout on mobile/tablet viewports.