

# ITEM MASTER

The Item Master contains the permanent list of warehouse items.

Each item should only be created once.

Do NOT store quantity in the Item Master.

Fields:

* Item ID (Auto Increment)
* UUID
* Item Code (Auto Generated)
* Barcode (Optional)
* QR Code (Optional)
* Category (Dropdown)
* Item Name
* Local Name (Optional)
* Description
* Unit (Dropdown)

Examples:

* Kg
* Gram
* Packet
* Piece
* Box
* Bottle
* Roll
* Set
* Carton
* Bundle
* Litre

Additional Information

* Minimum Stock Level
* Maximum Stock Level (Optional)
* Default Storage Life (Days)
* Requires Expiry Tracking (Yes/No)
* Requires Batch Tracking (Yes/No)
* Requires Serial Number Tracking (Yes/No)
* Is Consumable (Yes/No)

Storage Requirements

* Normal
* Dry Storage
* Cold Storage
* Refrigerated
* Hazardous

Optional Photo Upload

Status

* Active
* Inactive

Audit Fields

* Created By
* Created Date
* Updated By
* Updated Date

---

# STOCK RECEIPT

Every incoming stock must be recorded through the Stock Receipt module.

No stock should be inserted directly into Inventory.

Inventory is automatically calculated.

Fields

Receipt Number (Auto)

Receipt Date

Warehouse (Dropdown)

Source Type (Dropdown)

* Government Supply
* Donation
* NGO
* Local Government
* Purchase
* Transfer
* Other

Source Organization

Source Contact Person

Phone Number

Email (Optional)

Address (Optional)

Reference Number (Optional)

Invoice Number

Invoice Date

Delivery Note Number

Vehicle Number (Optional)

Received By (System User)

Verified By (Optional)

Remarks

---

# STOCK ITEM DETAILS

A single receipt can contain multiple items.

Display as a dynamic table.

| Item | Description | Batch No | Serial No | Manufacture Date | Expiry Date | Quantity | Unit | Unit Cost | Total Cost |

Item Dropdown

Loads from Item Master.

Description loads automatically but remains editable.

Unit loads automatically.

Quantity must be positive.

Total Cost = Quantity × Unit Cost.

---

# OPTIONAL TRACKING INFORMATION

Each stock item may store:

Batch Number

Lot Number

Serial Number

Manufacture Date

Expiry Date

Shelf Life

Country of Origin

Manufacturer

Supplier Name

Package Type

Examples:

* Sack
* Box
* Bottle
* Packet
* Carton

Package Size

Examples:

50 Kg

10 Litre

500 ml

20 Pieces

Storage Location

Remarks

Photo Upload

---

# DOCUMENT ATTACHMENTS

Allow upload of:

Invoice

Delivery Note

Waybill

Donation Letter

Approval Letter

Photos

Inspection Report

Accepted file types:

PDF

JPG

PNG

Maximum file size configurable.

---

# INVENTORY CALCULATION

Current Inventory must NOT be manually editable.

Inventory is calculated from:

Total Received

Minus

Total Dispatched

Minus

Damage

Minus

Expired

Plus

Adjustments

Inventory should always display:

Item

Warehouse

Available Quantity

Reserved Quantity

Minimum Stock

Unit

Last Updated

Status

Status:

Green

Available

Yellow

Low Stock

Red

Out of Stock

---

# MANUAL ADJUSTMENT

Purpose

Correction after physical counting.

Damage

Loss

Expiry

Miscount

Increase

Decrease

Fields

Adjustment Number

Date

Warehouse

Item

Current Quantity

Adjustment Type

Increase

Decrease

Damage

Expired

Lost

Correction

Adjustment Quantity

Reason

Remarks

Approval User

Inventory updates automatically.

---

# DISPATCH MODULE

Items should only be dispatched from current Inventory.

Fields

Dispatch Number

Dispatch Date

Warehouse

Incident

Relief Request

Destination

Receiver Name

Receiver Contact

Remarks

Dynamic Item Table

| Item | Batch No | Expiry Date | Available Qty | Dispatch Qty | Unit |

Rules

Dispatch Quantity cannot exceed Available Quantity.

If batch tracking is enabled, select the batch.

If expiry tracking is enabled, dispatch the earliest expiry first.

After saving, Inventory updates automatically.

---

# DISTRIBUTION MODULE

Distribution should use dispatched items.

Fields

Distribution Number

Distribution Date

Dispatch Number

Incident

Location

Officer

Remarks

Beneficiary Table

| Family/Organization | ID | Members | Item | Quantity |

Items load automatically from Dispatch.

Inventory should not change here because stock already left the warehouse during Dispatch.

---

# LOW STOCK ALERT

Automatically notify when:

Available Quantity ≤ Minimum Stock Level

Display:

Yellow Warning

Red Critical Warning

Dashboard should list all low stock items.

---

# EXPIRY ALERT

For items with expiry tracking enabled:

Show warning when expiry is within:

180 Days

90 Days

30 Days

7 Days

Expired

Display warning colors automatically.

---

# SEARCH AND FILTER

Allow searching by:

Item Code

Item Name

Barcode

QR Code

Batch Number

Invoice Number

Receipt Number

Serial Number

Supplier

Source Organization

Warehouse

Category

Expiry Date

Manufacture Date

---

# HISTORY TAB

Each item should have a History page showing:

Receipt History

Adjustment History

Dispatch History

Distribution History

Current Stock

Total Received

Total Issued

Total Adjusted

Total Damaged

Total Expired

Remaining Stock

The history should be displayed in chronological order for full traceability.

---

# DESIGN PRINCIPLE

The Item and Stock Tracking system should follow a **single-source inventory model**:

* Item Master defines the item.
* Stock Receipt adds inventory.
* Manual Adjustment corrects inventory.
* Dispatch reduces inventory.
* Distribution records the final recipient.
* Inventory is always calculated automatically and should never be edited directly.

All forms should use linked dropdowns and auto-filled fields wherever possible to minimize duplicate data entry and simplify operation for warehouse staff.
