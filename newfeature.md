# SIMPLE EMERGENCY OPERATIONS CENTRE (EOC) WAREHOUSE MANAGEMENT SYSTEM DESIGN GUIDE

## System Objective

The system is designed for a small Emergency Operations Centre warehouse used by government offices or local disaster management committees.

Its purpose is to:

* Maintain relief inventory
* Record stock receipts and issues
* Manage warehouse locations
* Record disaster incidents
* Process relief requests
* Dispatch relief materials
* Track beneficiary distributions
* Generate reports and dashboards

The system should be simple, fast, and easy to operate by non-technical staff.

---

# Overall Workflow

```
Settings
     │
     ▼
User & Roles
     │
     ▼
Warehouse
     │
     ▼
Categories
     │
     ▼
Items
     │
     ▼
Stock Receipt
     │
     ▼
Current Inventory
     │
     ▼
Incident (if disaster occurs)
     │
     ▼
Relief Request
     │
     ▼
Dispatch
     │
     ▼
Distribution
     │
     ▼
Reports & Dashboard
```

Everything revolves around the **Current Inventory** table.

---

# MODULE 1 : Settings

Stores organization-wide configuration.

Fields:

* Office Name
* Logo
* Address
* Phone
* Email
* Fiscal Year
* Default Language
* Report Header
* Report Footer

Every report uses these settings automatically.

---

# MODULE 2 : User Management

Purpose:

Control system access.

Roles:

* Administrator
* Warehouse Manager
* Data Entry
* Viewer

Permissions:

* Dashboard
* Warehouse
* Inventory
* Incident
* Dispatch
* Distribution
* Reports
* Settings

Every action records:

* User
* Date
* Time

---

# MODULE 3 : Warehouse

Normally there may only be one warehouse.

Example:

```
Central EOC Warehouse
```

Fields

* Warehouse Name
* Warehouse Code
* Address
* Contact Person
* Phone
* Capacity
* Remarks

If multiple warehouses exist later, the system should support them.

---

# MODULE 4 : Categories

Categories organize items.

Examples

Food

Medical

Shelter

Rescue

WASH

Communication

Construction

Fuel

Miscellaneous

Fields

* Category Name
* Description

Dropdown used in Item Form.

```
Category
      │
      ▼
Item
```

---

# MODULE 5 : Item Master

This is the master list of relief items.

Fields

* Item Code (Auto)
* Category (Dropdown)
* Item Name
* Unit

Examples:

Kg

Packet

Box

Piece

Bottle

Roll

* Minimum Stock
* Description

Example

```
Category

Food

↓

Rice

```

This module stores only item definitions.

No quantity is stored here.

---

# MODULE 6 : Stock Receipt

Used whenever goods arrive.

Sources may be:

* Government
* Donation
* NGO
* Transfer
* Purchase

Fields

Receipt No

Date

Warehouse (Dropdown)

Source Type (Dropdown)

Source Name

Item (Dropdown)

Unit (Auto)

Quantity

Remarks

After Save

Inventory automatically increases.

Example

```
Rice

+500

Inventory

500
```

No separate donation or procurement modules are required.

Everything enters through Stock Receipt.

---

# MODULE 7 : Inventory

This is the heart of the system.

Shows current available stock.

Displays

Item

Category

Warehouse

Available Quantity

Unit

Minimum Stock

Status

Status automatically becomes:

Green

Enough Stock

Yellow

Low Stock

Red

Out of Stock

Inventory updates automatically from:

* Stock Receipt
* Dispatch
* Manual Adjustment

Users cannot edit inventory directly.

Inventory is system-generated.

---

# MODULE 8 : Manual Adjustment

Used when:

* Damage
* Loss
* Physical Count
* Correction
* Expired

Fields

Adjustment No

Date

Warehouse

Item

Current Quantity

Adjustment Type

Increase

Decrease

Reason

Adjusted Quantity

Remarks

Inventory updates automatically.

---

# MODULE 9 : Incident Management

Create disaster events.

Examples

Flood 2026

Earthquake 2026

Fire at Ward 4

Fields

Incident ID

Incident Name

Incident Type

Province

District

Municipality

Ward

Start Date

Status

Description

Every relief request belongs to one Incident.

```
Incident

↓

Relief Request

```

---

# MODULE 10 : Relief Request

District or municipality requests relief.

Fields

Request Number

Request Date

Incident (Dropdown)

Organization

Requester Name

Phone

Priority

Low

Medium

High

Urgent

Remarks

Below add requested items.

Dynamic table

| Item | Unit | Requested Qty |

Item comes from Item Master.

Unit fills automatically.

---

# MODULE 11 : Dispatch

Warehouse approves and dispatches relief.

Fields

Dispatch Number

Date

Warehouse

Incident

Relief Request

Destination

Receiver

Phone

Remarks

Dynamic Item Table

| Item | Available Qty | Dispatch Qty | Unit |

Available Qty loads automatically.

Dispatch Qty cannot exceed Available Qty.

After Save

Inventory decreases automatically.

Request status updates:

Pending

Partial

Completed

---

# MODULE 12 : Distribution

Final distribution to beneficiaries.

Fields

Distribution Number

Dispatch Number (Dropdown)

Incident (Auto)

Location

Distribution Date

Officer

Remarks

Beneficiary Table

| Family Name | ID | Members | Item | Qty |

Item list loads from Dispatch.

Quantity cannot exceed dispatched quantity.

Distribution report is generated automatically.

---

# MODULE 13 : Dashboard

Displays live statistics.

Cards

Total Items

Current Stock

Low Stock

Out of Stock

Active Incidents

Pending Requests

Today's Dispatch

Today's Distribution

Charts

Stock by Category

Monthly Dispatch

Monthly Distribution

Low Stock Items

Recent Activities

Latest Receipts

Latest Dispatches

Latest Requests

---

# MODULE 14 : Reports

Inventory Report

Current Stock

Stock Receipt

Dispatch Report

Distribution Report

Incident Report

Request Report

Low Stock Report

Adjustment Report

Monthly Summary

Export

PDF

Excel

Print

---

# FORM RELATIONSHIPS

Warehouse Form

↓

Used in

Stock Receipt

Inventory

Dispatch

Adjustment

---

Category Form

↓

Used in

Item Master

---

Item Master

↓

Used in

Stock Receipt

Inventory

Adjustment

Relief Request

Dispatch

Distribution

---

Incident

↓

Used in

Relief Request

Dispatch

Distribution

Reports

---

Relief Request

↓

Used in

Dispatch

---

Dispatch

↓

Used in

Distribution

---

Stock Receipt

↓

Updates

Inventory

---

Adjustment

↓

Updates

Inventory

---

Dispatch

↓

Reduces

Inventory

---

Distribution

↓

Completes

Dispatch

---

# DATABASE RELATIONSHIP

```
Warehouse
      │
      ▼
Inventory
      ▲
      │
Item Master
      ▲
      │
Category

Incident
      │
      ▼
Relief Request
      │
      ▼
Dispatch
      │
      ▼
Distribution

Stock Receipt
      │
      ▼
Inventory

Adjustment
      │
      ▼
Inventory
```

---

# DYNAMIC DROPDOWN BEHAVIOR

Category

↓

Filters Item list

---

Warehouse

↓

Shows warehouse inventory

---

Item

↓

Automatically loads:

Unit

Current Stock

Minimum Stock

---

Incident

↓

Filters related Relief Requests

---

Relief Request

↓

Automatically loads requested items into Dispatch

---

Dispatch

↓

Automatically loads dispatch items into Distribution

---

Inventory updates automatically after every Receipt, Adjustment, or Dispatch without manual editing.

---

# DESIGN PRINCIPLE

The system should remain **simple, paper-register-like, and easy for government staff to use**. Users should only enter data once, with all related forms automatically populating dropdowns and linked information. The system should avoid duplicate data entry, maintain a single source of truth for inventory, and provide clear dashboards and reports for emergency decision-making.
