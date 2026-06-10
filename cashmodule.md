# FINANCE / CASH ASSISTANCE MODULE

## Purpose

The Finance Module manages disaster relief funds that are distributed directly to beneficiaries or local governments.

The module is **not a full accounting system**. It is designed only for tracking relief cash allocations, approvals, disbursements, balances, and reports.

Cash assistance should follow the same workflow as material assistance.

---

# CASH WORKFLOW

```text
Budget Allocation
        │
        ▼
Cash Fund
        │
        ▼
Incident
        │
        ▼
Cash Request
        │
        ▼
Approval
        │
        ▼
Cash Distribution
        │
        ▼
Beneficiary
        │
        ▼
Reports
```

---

# MODULE : CASH FUND

Stores available disaster response funds.

Fields

Fund ID

Fund Name

Fiscal Year

Funding Source

Examples

* Federal Government
* Provincial Government
* Municipality
* Disaster Relief Fund
* Donor Agency
* NGO

Allocated Amount

Current Balance

Description

Status

Active

Closed

Audit Fields

Created Date

Updated Date

Created By

---

# MODULE : CASH RECEIPT

Used when new funds become available.

Fields

Receipt Number

Receipt Date

Fund (Dropdown)

Funding Source

Reference Number

Voucher Number

Bank Transaction Number

Amount Received

Received By

Remarks

Document Upload

Allocation Letter

Bank Voucher

PDF

Image

After Save

Fund Balance automatically increases.

---

# MODULE : CASH REQUEST

Cash requests are linked to disaster incidents.

Fields

Request Number

Request Date

Incident (Dropdown)

Requesting Office

Requester Name

Phone

Priority

Low

Medium

High

Urgent

Requested Amount

Purpose

Examples

Medical Support

Immediate Relief

Temporary Shelter

Funeral Support

Food Assistance

Livelihood Support

Other

Remarks

Status

Pending

Approved

Rejected

Partial

Completed

---

# MODULE : CASH DISTRIBUTION

Used after approval.

Fields

Distribution Number

Distribution Date

Fund (Dropdown)

Incident (Dropdown)

Cash Request (Dropdown)

Distribution Type

Individual

Family

Community

Local Government

Organization

Total Amount

Officer

Remarks

Beneficiary Table

| Beneficiary Name | National ID | Address | Phone | Amount |

Amount cannot exceed approved amount.

After Save

Fund Balance decreases automatically.

Cash Request status updates automatically.

Pending

Partial

Completed

---

# MODULE : BENEFICIARY

The same Beneficiary table should be used for both:

* Material Distribution
* Cash Distribution

Fields

Beneficiary ID

Name

National ID

Phone

Address

Municipality

Ward

Family Members

Bank Account (Optional)

Mobile Wallet (Optional)

Remarks

History should show:

* Materials Received
* Cash Received

This prevents duplicate assistance.

---

# DASHBOARD ADDITIONS

Display:

Available Cash Balance

Total Cash Distributed

Today's Cash Distribution

Pending Cash Requests

Cash Distributed This Month

Cash by Incident

Cash by Funding Source

---

# REPORTS

Generate

Cash Balance Report

Cash Receipt Report

Cash Request Report

Cash Distribution Report

Cash by Incident

Cash by Municipality

Cash by Beneficiary

Cash by Funding Source

Monthly Cash Report

Yearly Cash Report

Export

PDF

Excel

Print

---

# FORM RELATIONSHIPS

Fund

↓

Cash Receipt

Cash Distribution

---

Incident

↓

Cash Request

Cash Distribution

Reports

---

Cash Request

↓

Cash Distribution

---

Beneficiary

↓

Material Distribution

Cash Distribution

History

---

Cash Receipt

↓

Fund Balance increases

---

Cash Distribution

↓

Fund Balance decreases

---

Cash Distribution

↓

Beneficiary History updates

---

Cash Distribution

↓

Reports

---

# DATABASE RELATIONSHIP

```text
Cash Fund
      │
      ▼
Cash Receipt
      │
      ▼
Available Balance

Incident
      │
      ▼
Cash Request
      │
      ▼
Cash Distribution
      │
      ▼
Beneficiary
```

---

# UNIFIED RELIEF DISTRIBUTION MODEL

The system should support **two parallel types of assistance**:

### Material Assistance

Stock Receipt

↓

Inventory

↓

Dispatch

↓

Distribution

↓

Beneficiary

---

### Cash Assistance

Cash Receipt

↓

Cash Fund

↓

Cash Request

↓

Cash Distribution

↓

Beneficiary

---

Both workflows should share the same:

* Incident
* Beneficiary Database
* Dashboard
* Reports
* Audit Log
* User Permissions

This allows an affected family to receive **both relief materials (food, tents, blankets, medicine)** and **cash assistance** while maintaining a complete assistance history under a single beneficiary record.

The Dashboard should therefore summarize:

* Current Warehouse Inventory
* Current Cash Fund Balance
* Active Incidents
* Pending Material Requests
* Pending Cash Requests
* Material Distributed
* Cash Distributed
* Total Beneficiaries Assisted

This unified design keeps the application simple for district or municipal Emergency Operations Centres while covering both inventory-based and cash-based disaster response operations without requiring a full financial accounting system.
