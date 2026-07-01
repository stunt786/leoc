Enhance the existing Local Emergency Operations Centre (LEOC) Management Information System by adding the following disaster management modules. The system already contains incident management, warehouse management, relief management, reporting, dashboard, user management and other core LEOC features. Develop only the following additional modules and integrate them with the existing architecture. Add new Menu with sub menuin the sidebar for following new modules and features

GENERAL REQUIREMENTS

* Responsive web application
* PostgreSQL database
* GIS-enabled architecture
* GPS coordinate support wherever applicable
* OpenStreetMap + Leaflet integration-use existing
* Role-based access control
* Audit logs
* File attachment support
* Photo upload support
* Excel import/export
* PDF reporting
* Nepali and English language support
* Dashboard widgets and analytics
* Search, filtering and advanced reporting

=================================================
MODULE 1: CRITICAL INFRASTRUCTURE REGISTRY
==========================================

Purpose:
Maintain GIS-based inventory of critical infrastructure assets used during emergencies.

Fields:

Basic Information

* Infrastructure ID
* Infrastructure Name
* Infrastructure Type
* Description
* Ward
* Settlement/Tole

GIS Information

* Latitude
* Longitude
* Elevation
* GIS Point Location

Infrastructure Categories

* Municipality Office
* Ward Office
* Hospital
* Health Post
* Primary Health Centre
* School
* Police Office
* Armed Police Office
* Army Barrack
* Fire Station
* Communication Tower
* Power Substation
* Water Supply Facility
* Irrigation Facility
* Bridge
* Government Building
* Community Building
* Market Centre
* Fuel Station
* Bank
* Other Critical Infrastructure

Operational Information

* Capacity
* Current Status
* Contact Person
* Contact Number
* Accessibility Status
* Available Facilities

Attachments

* Photos
* Documents

GIS Features

* Map visualization
* Infrastructure layer
* Infrastructure search
* Distance calculation from incident location

=================================================
MODULE 2: EMERGENCY FACILITIES REGISTRY
=======================================

Purpose:
Maintain all emergency facilities available within municipality.

Facility Types

* Helipad
* Safe Shelter
* Evacuation Centre
* Open Space
* Relief Distribution Centre
* Emergency Warehouse
* Emergency Operations Centre
* Temporary Camp Site

Fields

* Facility Name
* Facility Type
* Ward
* Location Description

GIS Information

* Latitude
* Longitude
* Polygon Boundary (optional)

Capacity Information

* Maximum Capacity
* Current Occupancy
* Water Availability
* Electricity Availability
* Toilet Availability
* Kitchen Availability
* Internet Availability
* Accessibility for Persons with Disabilities

Management Information

* Managing Organization
* Focal Person
* Contact Number

GIS Features

* Emergency facility map layer
* Nearest facility finder
* Route visualization

=================================================
MODULE 3: RISK LAYER MANAGEMENT
===============================

Purpose:
Maintain disaster risk zones and visualize them on GIS maps.

Risk Categories

* Flood Risk Zone
* Landslide Risk Zone
* Fire Risk Zone
* Earthquake Risk Zone
* River Cutting Zone
* Forest Fire Risk Zone
* Drought Risk Zone
* Avalanche Risk Zone
* Windstorm Risk Zone
* Lightning Risk Zone

Fields

* Risk Layer Name
* Risk Type
* Risk Level

Risk Levels

* Low
* Moderate
* High
* Very High

GIS Information

* Polygon Boundary
* Latitude
* Longitude
* Area Coverage
* Affected Settlements
* Affected Households
* Population at Risk

GIS Features

* Layer control
* Risk heat map
* Overlay with population
* Overlay with infrastructure
* Overlay with shelters

=================================================
MODULE 4: EMERGENCY CONTACT DIRECTORY
=====================================

Purpose:
Centralized emergency contact management.

Categories

Government

* Mayor/Chairperson
* Vice Chairperson
* Chief Administrative Officer
* Ward Chairperson

Security

* Nepal Police
* Armed Police Force
* Nepal Army

Health

* Hospital
* Ambulance
* Blood Bank

Emergency Services

* Fire Service
* Rescue Team

Utilities

* Electricity
* Drinking Water
* Telecommunications

NGO/INGO

* Nepal Red Cross
* Humanitarian Organizations

Fields

* Organization Name
* Contact Person
* Designation
* Mobile Number
* Alternative Number
* Email
* Address
* Ward
* Latitude
* Longitude
* Availability Status
* Service Area

Features

* One-click dialing
* Quick search
* GIS visualization
* Emergency contact dashboard

=================================================
MODULE 5: CLUSTER COORDINATION MANAGEMENT
=========================================

Purpose:
Manage humanitarian cluster coordination.

Clusters

* Search and Rescue
* Health
* Shelter
* WASH
* Food Security
* Protection
* Logistics
* Education
* Communication

Fields

* Cluster Name
* Lead Organization
* Focal Person
* Contact Details
* Resource Capacity
* Available Equipment
* Coverage Area
* GIS Coverage Boundary

Cluster Members

* Organization Name
* Representative
* Contact Number
* Designation

Features

* Cluster resource mapping
* Cluster meeting records
* Deployment records
* GIS coverage visualization

=================================================
MODULE 6: VULNERABLE POPULATION REGISTRY
========================================

Purpose:
Identify vulnerable households requiring priority support.

Categories

* Senior Citizens
* Single Women
* Social Security Beneficiaries
* Child Headed Households
* Marginalized Families
* Economically Vulnerable Households

Fields

* Household ID
* Head of Household
* Family Size
* Category
* Ward
* Settlement
* Contact Number

GIS Information

* Latitude
* Longitude
* House Location

Risk Information

* Disaster Exposure
* Evacuation Priority Level

Features

* GIS vulnerable household mapping
* Priority support lists
* Ward-wise reports

=================================================
MODULE 7: DIFFERENTLY ABLED PERSONS REGISTRY
============================================

Fields

* Person Name
* Gender
* Age
* Ward
* Settlement
* Contact Number

Disability Information

* Physical Disability
* Visual Disability
* Hearing Disability
* Intellectual Disability
* Multiple Disability

Support Information

* Caregiver Name
* Caregiver Contact
* Mobility Requirement
* Medical Requirement
* Evacuation Requirement

GIS Information

* Latitude
* Longitude

Features

* Disability GIS mapping
* Emergency evacuation support list
* Ward-wise reporting

=================================================
MODULE 8: HIGH RISK POPULATION REGISTRY
=======================================

Categories

* Pregnant Women
* Lactating Mothers
* Infants
* Chronic Patients
* Dialysis Patients
* Oxygen Dependent Patients
* Bedridden Persons

Fields

* Person Name
* Age
* Gender
* Category
* Contact Number
* Ward
* Settlement

Medical Information

* Health Condition
* Health Facility Linked
* Emergency Contact

GIS Information

* Latitude
* Longitude

Features

* Emergency evacuation prioritization
* GIS mapping
* Health support reporting

=================================================
MODULE 9: VOLUNTEER MANAGEMENT
==============================

Fields

Personal Information

* Volunteer ID
* Name
* Gender
* Age
* Ward
* Contact Number
* Email

Skills

* First Aid
* Search and Rescue
* Fire Fighting
* Logistics
* Communication
* Medical Support

Training

* Training Name
* Training Date
* Certification Status

Availability

* Available
* On Duty
* Unavailable

GIS Information

* Home Latitude
* Home Longitude

Features

* Volunteer deployment
* Volunteer GIS map
* Skill-based filtering

=================================================
MODULE 10: RAPID RESPONSE TEAM (RRT)
====================================

Fields

* Team Name
* Team Type
* Coverage Area
* Team Leader
* Contact Number

Members

* Name
* Designation
* Skill
* Contact Number

Resources

* Equipment Assigned
* Vehicles Assigned

GIS Information

* Base Location Latitude
* Base Location Longitude

Features

* Team deployment
* Incident assignment
* Response tracking

=================================================
MODULE 11: DISASTER MANAGEMENT COMMITTEE
========================================

Committee Types

* Municipal Disaster Management Committee
* Ward Disaster Management Committee

Fields

* Committee Name
* Committee Type
* Formation Date
* Tenure

Members

* Name
* Position
* Organization
* Contact Number

Meetings

* Meeting Date
* Agenda
* Decisions
* Action Items

Features

* Committee directory
* Meeting history
* Decision tracking

=================================================
MODULE 12: VEHICLE MANAGEMENT
=============================

Vehicle Types

* Ambulance
* Fire Engine
* Backhule Loader
* Tractor
* Pickup
* Truck
* Jeep
* Motorcycle
* Van

Fields

* Vehicle Number
* Vehicle Type
* Owner Organization
* Driver Name
* Driver Contact

Status

* Available
* Deployed
* Under Maintenance

GIS Information

* Current Latitude
* Current Longitude

Operational Information

* Fuel Status
* Capacity
* Last Service Date

Features

* Vehicle tracking
* Nearest vehicle identification
* Deployment history

=================================================
MODULE 13: SHELTER AND EVACUATION MANAGEMENT
============================================

Shelter Information

* Shelter Name
* Shelter Type
* Ward
* Location

GIS Information

* Latitude
* Longitude
* Boundary Polygon

Capacity

* Total Capacity
* Male Capacity
* Female Capacity
* Children Capacity

Facilities

* Water
* Toilet
* Electricity
* Kitchen
* Medical Support
* Accessibility Support

Occupancy

* Current Occupancy
* Available Space

Management

* Shelter Manager
* Contact Number

Evacuation Planning

* Evacuation Routes
* Assembly Points
* Linked Risk Zones
* Linked Vulnerable Households

GIS Features

* Shelter mapping
* Evacuation route visualization
* Nearest shelter recommendation
* Shelter occupancy dashboard

=================================================
GIS ANALYTICS AND INTEGRATION
=============================

Create a unified GIS dashboard showing:

* Critical Infrastructure Layer
* Emergency Facility Layer
* Risk Zone Layer
* Shelter Layer
* Volunteer Layer
* Vehicle Layer
* Vulnerable Population Layer
* Differently Abled Persons Layer
* High Risk Population Layer
* RRT Base Locations

Provide GIS tools for:

* Buffer Analysis
* Distance Analysis
* Nearest Facility Search
* Incident Impact Analysis
* Population Exposure Analysis
* Shelter Coverage Analysis
* Emergency Resource Mapping
* Evacuation Planning Support
