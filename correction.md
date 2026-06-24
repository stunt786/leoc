**validation for Supplier form for phone, email and duplication entry based on phone, email or name match
**Validation in incident form: Total affected people=male+female, death,injured and injured male/female should not be higher total no. of Male affected and female affected
Validation on Affected Households: House destroyed and house damaged shouldn't be higer than affected households
**Validation on benefaciries based on ID of family members too, already member of another family. And check ID within family members and other members and families, no duplicate entry based in ID check
**'Cash Request' from Relief module not dynamically updated to cash request module, sometimes work and sometimes not. Also if Incident status is not activem cash request incident dropdown should be disabled i.e only distribution for active incidents is allowed.
**Cash Distribution: cash request via relief distribution shows form error no beneficary found on cash distribution form.(selected cash request has no beneficary). And **Relief Distribution displays beneficary already have got cash in this fiscal year. Both cash distribution and relief distribution with has dynamic verifaction problem.
Validation bypass in distribution when cash is also requested and "Cash Fund' has lower fund than asked, gives error but saved successfully though cash is not updated. Fix this
//Relief distribution working mechanism: a beneficary can get cash or items or cash+items in a single fiscal year at once for single incident.

**Daily Bulletin saved success message but not not actually saved. Also increase nextupdatetime field size while making weather_status and incident_reporting_status fields smaller
**Reports: Data not fetched from db and showing empty data for 'Incident report'
**Validation on Settings page: Add validation for fiscal Year, Disaster types, SSF Types, Wards if the fields are used in other forms like incident, beneficary, etc.
**Validation in Cash request: Make compulsory fields, Incident, Beneficary, Purpose
**Dispatch form: For Dispatched items section decrease the field size for 'Items' and adjust size of other fields for better visibility. Currently other fields likerequested, available, dispatched quantity are too small to type and see text in it. also Batch no. and expiry not updated dynamically in dispatch Items list form. Also **update Relief Request selection field not to show completed relief requests.
**Distribution: In distribution page and in form field Dispatches selection, Only list dispatches whose distribution is not yet done. Don't show dispatches whose distribution is already completed. Also for some distribution creation I got this type of error for non duplicate beneficary,(Duplicate beneficiary "Mohan Sharma" in the same distribution request). This happens after clicking Reset button. It also deletes old distributions from list.
**Benefeciries Form: In benefecaries form, increase field size for cash amount, photo and document and decrease for ID Number. Also fix document upload not working. And if there are multiple beneficary photo is also uploading for single beneficary.
**Batch Tracking and Serial tracking: How are they implemented?

#Alert/Notification system: Add alert and notification system and update below information. Alert and notification should be viewable for details in another notification page and add clear notification button to clear all existing ones and ready for new ones. Add some animated flash notifications for high alert notifications. Check status 24 hrs and re-show notifications for low stocks, expired items, active incidents. Show until they are updated. 
**All stock receipts notification and also update in logs
**All Stock transfer and adjustments also in logs
**All Stock Items low, expiry status, status
**All Incidents 
**All Relief Requests
**All Dispatches
**All Distributions
**All cash request and distributions