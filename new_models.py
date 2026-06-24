from shared import db, utc_now

# ============================================
# MODULE 1: CRITICAL INFRASTRUCTURE REGISTRY
# ============================================

INFRASTRUCTURE_TYPES = [
    'Municipality Office', 'Ward Office', 'Hospital', 'Health Post',
    'Primary Health Centre', 'School', 'Police Office', 'Armed Police Office',
    'Army Barrack', 'Fire Station', 'Communication Tower', 'Power Substation',
    'Water Supply Facility', 'Irrigation Facility', 'Bridge', 'Government Building',
    'Community Building', 'Market Centre', 'Fuel Station', 'Bank',
    'Other Critical Infrastructure'
]

class CriticalInfrastructure(db.Model):
    __tablename__ = 'critical_infrastructure'
    id = db.Column(db.Integer, primary_key=True)
    infrastructure_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(300), nullable=False)
    infrastructure_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    settlement = db.Column(db.String(200))
    coordinates = db.Column(db.String(100))
    elevation = db.Column(db.Float)
    capacity = db.Column(db.String(100))
    current_status = db.Column(db.String(50), default='Operational')
    contact_person = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    accessibility_status = db.Column(db.String(50), default='Accessible')
    available_facilities = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='infrastructures', lazy=True)
    photos = db.relationship('InfrastructurePhoto', backref='infrastructure', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('InfrastructureDocument', backref='infrastructure', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'infrastructure_id': self.infrastructure_id,
            'name': self.name,
            'infrastructure_type': self.infrastructure_type,
            'description': self.description,
            'ward_id': self.ward_id,
            'ward_name': self.ward.name if self.ward else None,
            'settlement': self.settlement,
            'coordinates': self.coordinates,
            'elevation': self.elevation,
            'capacity': self.capacity,
            'current_status': self.current_status,
            'contact_person': self.contact_person,
            'contact_number': self.contact_number,
            'accessibility_status': self.accessibility_status,
            'available_facilities': self.available_facilities,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class InfrastructurePhoto(db.Model):
    __tablename__ = 'infrastructure_photo'
    id = db.Column(db.Integer, primary_key=True)
    infrastructure_id = db.Column(db.Integer, db.ForeignKey('critical_infrastructure.id'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=utc_now)

class InfrastructureDocument(db.Model):
    __tablename__ = 'infrastructure_document'
    id = db.Column(db.Integer, primary_key=True)
    infrastructure_id = db.Column(db.Integer, db.ForeignKey('critical_infrastructure.id'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=utc_now)


# ============================================
# MODULE 2: EMERGENCY FACILITIES REGISTRY
# ============================================

FACILITY_TYPES = [
    'Helipad', 'Safe Shelter', 'Evacuation Centre', 'Open Space',
    'Relief Distribution Centre', 'Emergency Warehouse',
    'Emergency Operations Centre', 'Temporary Camp Site'
]

class EmergencyFacility(db.Model):
    __tablename__ = 'emergency_facility'
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(300), nullable=False)
    facility_type = db.Column(db.String(100), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    location_description = db.Column(db.Text)
    coordinates = db.Column(db.String(100))
    polygon_boundary = db.Column(db.Text)
    max_capacity = db.Column(db.Integer)
    current_occupancy = db.Column(db.Integer, default=0)
    water_availability = db.Column(db.Boolean, default=False)
    electricity_availability = db.Column(db.Boolean, default=False)
    toilet_availability = db.Column(db.Boolean, default=False)
    kitchen_availability = db.Column(db.Boolean, default=False)
    internet_availability = db.Column(db.Boolean, default=False)
    accessibility_disabled = db.Column(db.Boolean, default=False)
    managing_organization = db.Column(db.String(300))
    focal_person = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='emergency_facilities', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'facility_name': self.facility_name,
            'facility_type': self.facility_type,
            'ward_id': self.ward_id,
            'ward_name': self.ward.name if self.ward else None,
            'location_description': self.location_description,
            'coordinates': self.coordinates,
            'polygon_boundary': self.polygon_boundary,
            'max_capacity': self.max_capacity,
            'current_occupancy': self.current_occupancy,
            'water_availability': self.water_availability,
            'electricity_availability': self.electricity_availability,
            'toilet_availability': self.toilet_availability,
            'kitchen_availability': self.kitchen_availability,
            'internet_availability': self.internet_availability,
            'accessibility_disabled': self.accessibility_disabled,
            'managing_organization': self.managing_organization,
            'focal_person': self.focal_person,
            'contact_number': self.contact_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 3: RISK LAYER MANAGEMENT
# ============================================

RISK_TYPES = [
    'Flood Risk Zone', 'Landslide Risk Zone', 'Fire Risk Zone',
    'Earthquake Risk Zone', 'River Cutting Zone', 'Forest Fire Risk Zone',
    'Drought Risk Zone', 'Avalanche Risk Zone', 'Windstorm Risk Zone',
    'Lightning Risk Zone'
]

RISK_LEVELS = ['Low', 'Moderate', 'High', 'Very High']

class RiskLayer(db.Model):
    __tablename__ = 'risk_layer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    risk_type = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    polygon_boundary = db.Column(db.Text)
    coordinates = db.Column(db.String(100))
    area_coverage = db.Column(db.Float)
    affected_settlements = db.Column(db.Text)
    affected_households = db.Column(db.Integer)
    population_at_risk = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'risk_type': self.risk_type,
            'risk_level': self.risk_level,
            'polygon_boundary': self.polygon_boundary,
            'coordinates': self.coordinates,
            'area_coverage': self.area_coverage,
            'affected_settlements': self.affected_settlements,
            'affected_households': self.affected_households,
            'population_at_risk': self.population_at_risk,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 4: EMERGENCY CONTACT DIRECTORY
# ============================================

CONTACT_CATEGORIES = [
    'Government', 'Security', 'Health', 'Emergency Services', 'Utilities', 'NGO/INGO'
]

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contact'
    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.String(300), nullable=False)
    contact_person = db.Column(db.String(200))
    designation = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(100))
    mobile_number = db.Column(db.String(50), nullable=False)
    alternative_number = db.Column(db.String(50))
    email = db.Column(db.String(200))
    address = db.Column(db.String(300))
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    coordinates = db.Column(db.String(100))
    availability_status = db.Column(db.String(20), default='Available')
    service_area = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='emergency_contacts', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_name': self.organization_name,
            'contact_person': self.contact_person,
            'designation': self.designation,
            'category': self.category,
            'sub_category': self.sub_category,
            'mobile_number': self.mobile_number,
            'alternative_number': self.alternative_number,
            'email': self.email,
            'address': self.address,
            'ward_id': self.ward_id,
            'ward_name': self.ward.name if self.ward else None,
            'coordinates': self.coordinates,
            'availability_status': self.availability_status,
            'service_area': self.service_area,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 5: CLUSTER COORDINATION MANAGEMENT
# ============================================

class Cluster(db.Model):
    __tablename__ = 'cluster'
    id = db.Column(db.Integer, primary_key=True)
    cluster_name = db.Column(db.String(100), nullable=False, unique=True)
    lead_organization = db.Column(db.String(300))
    focal_person = db.Column(db.String(200))
    contact_details = db.Column(db.String(500))
    resource_capacity = db.Column(db.String(500))
    available_equipment = db.Column(db.Text)
    coverage_area = db.Column(db.String(300))
    gis_coverage_boundary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    members = db.relationship('ClusterMember', backref='cluster', lazy=True, cascade='all, delete-orphan')
    meetings = db.relationship('ClusterMeeting', backref='cluster', lazy=True, cascade='all, delete-orphan')
    deployments = db.relationship('ClusterDeployment', backref='cluster', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'cluster_name': self.cluster_name,
            'lead_organization': self.lead_organization,
            'focal_person': self.focal_person,
            'contact_details': self.contact_details,
            'resource_capacity': self.resource_capacity,
            'available_equipment': self.available_equipment,
            'coverage_area': self.coverage_area,
            'gis_coverage_boundary': self.gis_coverage_boundary,
            'members': [m.to_dict() for m in self.members],
            'meetings': [m.to_dict() for m in self.meetings],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class ClusterMember(db.Model):
    __tablename__ = 'cluster_member'
    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'), nullable=False)
    organization_name = db.Column(db.String(300), nullable=False)
    representative = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    designation = db.Column(db.String(200))

    def to_dict(self):
        return {'id': self.id, 'cluster_id': self.cluster_id, 'organization_name': self.organization_name, 'representative': self.representative, 'contact_number': self.contact_number, 'designation': self.designation}

class ClusterMeeting(db.Model):
    __tablename__ = 'cluster_meeting'
    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    agenda = db.Column(db.Text)
    decisions = db.Column(db.Text)
    action_items = db.Column(db.Text)

    def to_dict(self):
        return {'id': self.id, 'cluster_id': self.cluster_id, 'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None, 'agenda': self.agenda, 'decisions': self.decisions, 'action_items': self.action_items}

class ClusterDeployment(db.Model):
    __tablename__ = 'cluster_deployment'
    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'), nullable=False)
    deployment_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(300))
    details = db.Column(db.Text)
    status = db.Column(db.String(50), default='Active')

    def to_dict(self):
        return {'id': self.id, 'cluster_id': self.cluster_id, 'deployment_date': self.deployment_date.isoformat() if self.deployment_date else None, 'location': self.location, 'details': self.details, 'status': self.status}


# ============================================
# MODULE 6: VULNERABLE POPULATION REGISTRY
# ============================================

VULNERABLE_CATEGORIES = [
    'Senior Citizens', 'Single Women', 'Social Security Beneficiaries',
    'Child Headed Households', 'Marginalized Families', 'Economically Vulnerable Households'
]

class VulnerableHousehold(db.Model):
    __tablename__ = 'vulnerable_household'
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    head_of_household = db.Column(db.String(200), nullable=False)
    family_size = db.Column(db.Integer)
    category = db.Column(db.String(100), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    settlement = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    coordinates = db.Column(db.String(100))
    disaster_exposure = db.Column(db.String(300))
    evacuation_priority = db.Column(db.String(20), default='Normal')
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='vulnerable_households', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'household_id': self.household_id, 'head_of_household': self.head_of_household,
            'family_size': self.family_size, 'category': self.category, 'ward_id': self.ward_id,
            'ward_name': self.ward.name if self.ward else None, 'settlement': self.settlement,
            'contact_number': self.contact_number, 'coordinates': self.coordinates,
            'disaster_exposure': self.disaster_exposure, 'evacuation_priority': self.evacuation_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 7: DIFFERENTLY ABLED PERSONS REGISTRY
# ============================================

class DisabledPerson(db.Model):
    __tablename__ = 'disabled_person'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    settlement = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    physical_disability = db.Column(db.Boolean, default=False)
    visual_disability = db.Column(db.Boolean, default=False)
    hearing_disability = db.Column(db.Boolean, default=False)
    intellectual_disability = db.Column(db.Boolean, default=False)
    multiple_disability = db.Column(db.Boolean, default=False)
    caregiver_name = db.Column(db.String(200))
    caregiver_contact = db.Column(db.String(50))
    mobility_requirement = db.Column(db.Text)
    medical_requirement = db.Column(db.Text)
    evacuation_requirement = db.Column(db.Text)
    coordinates = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='disabled_persons', lazy=True)

    def to_dict(self):
        dis = []
        if self.physical_disability: dis.append('Physical Disability')
        if self.visual_disability: dis.append('Visual Disability')
        if self.hearing_disability: dis.append('Hearing Disability')
        if self.intellectual_disability: dis.append('Intellectual Disability')
        if self.multiple_disability: dis.append('Multiple Disability')
        return {
            'id': self.id, 'person_name': self.person_name, 'gender': self.gender, 'age': self.age,
            'ward_id': self.ward_id, 'ward_name': self.ward.name if self.ward else None,
            'settlement': self.settlement, 'contact_number': self.contact_number, 'disabilities': dis,
            'caregiver_name': self.caregiver_name, 'caregiver_contact': self.caregiver_contact,
            'mobility_requirement': self.mobility_requirement, 'medical_requirement': self.medical_requirement,
            'evacuation_requirement': self.evacuation_requirement, 'coordinates': self.coordinates,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 8: HIGH RISK POPULATION REGISTRY
# ============================================

HIGH_RISK_CATEGORIES = [
    'Pregnant Women', 'Lactating Mothers', 'Infants', 'Chronic Patients',
    'Dialysis Patients', 'Oxygen Dependent Patients', 'Bedridden Persons'
]

class HighRiskPerson(db.Model):
    __tablename__ = 'high_risk_person'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    category = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(50))
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    settlement = db.Column(db.String(200))
    health_condition = db.Column(db.Text)
    health_facility_linked = db.Column(db.String(300))
    emergency_contact = db.Column(db.String(200))
    coordinates = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='high_risk_persons', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'person_name': self.person_name, 'age': self.age, 'gender': self.gender,
            'category': self.category, 'contact_number': self.contact_number, 'ward_id': self.ward_id,
            'ward_name': self.ward.name if self.ward else None, 'settlement': self.settlement,
            'health_condition': self.health_condition, 'health_facility_linked': self.health_facility_linked,
            'emergency_contact': self.emergency_contact, 'coordinates': self.coordinates,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 9: VOLUNTEER MANAGEMENT
# ============================================

class Volunteer(db.Model):
    __tablename__ = 'volunteer'
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    contact_number = db.Column(db.String(50))
    email = db.Column(db.String(200))
    skills = db.Column(db.Text)
    home_coordinates = db.Column(db.String(100))
    availability_status = db.Column(db.String(20), default='Available')
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='volunteers', lazy=True)
    trainings = db.relationship('VolunteerTraining', backref='volunteer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'volunteer_id': self.volunteer_id, 'name': self.name, 'gender': self.gender,
            'age': self.age, 'ward_id': self.ward_id, 'ward_name': self.ward.name if self.ward else None,
            'contact_number': self.contact_number, 'email': self.email,
            'skills': self.skills.split(',') if self.skills else [],
            'home_coordinates': self.home_coordinates, 'availability_status': self.availability_status,
            'trainings': [t.to_dict() for t in self.trainings],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class VolunteerTraining(db.Model):
    __tablename__ = 'volunteer_training'
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    training_name = db.Column(db.String(300), nullable=False)
    training_date = db.Column(db.Date)
    certification_status = db.Column(db.String(50), default='Pending')

    def to_dict(self):
        return {'id': self.id, 'volunteer_id': self.volunteer_id, 'training_name': self.training_name, 'training_date': self.training_date.isoformat() if self.training_date else None, 'certification_status': self.certification_status}


# ============================================
# MODULE 10: RAPID RESPONSE TEAM (RRT)
# ============================================

class RapidResponseTeam(db.Model):
    __tablename__ = 'rapid_response_team'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(200), nullable=False)
    team_type = db.Column(db.String(100))
    coverage_area = db.Column(db.String(300))
    team_leader = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    base_coordinates = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    members = db.relationship('RRTMember', backref='team', lazy=True, cascade='all, delete-orphan')
    resources = db.relationship('RRTResource', backref='team', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'team_name': self.team_name, 'team_type': self.team_type,
            'coverage_area': self.coverage_area, 'team_leader': self.team_leader,
            'contact_number': self.contact_number, 'base_coordinates': self.base_coordinates,
            'members': [m.to_dict() for m in self.members], 'resources': [r.to_dict() for r in self.resources],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class RRTMember(db.Model):
    __tablename__ = 'rrt_member'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('rapid_response_team.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    designation = db.Column(db.String(200))
    skill = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))

    def to_dict(self):
        return {'id': self.id, 'team_id': self.team_id, 'name': self.name, 'designation': self.designation, 'skill': self.skill, 'contact_number': self.contact_number}

class RRTResource(db.Model):
    __tablename__ = 'rrt_resource'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('rapid_response_team.id'), nullable=False)
    equipment_assigned = db.Column(db.String(500))
    vehicles_assigned = db.Column(db.String(500))

    def to_dict(self):
        return {'id': self.id, 'team_id': self.team_id, 'equipment_assigned': self.equipment_assigned, 'vehicles_assigned': self.vehicles_assigned}


# ============================================
# MODULE 11: DISASTER MANAGEMENT COMMITTEE
# ============================================

class DisasterCommittee(db.Model):
    __tablename__ = 'disaster_committee'
    id = db.Column(db.Integer, primary_key=True)
    committee_name = db.Column(db.String(300), nullable=False)
    committee_type = db.Column(db.String(100), nullable=False)
    formation_date = db.Column(db.Date)
    tenure = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    members = db.relationship('CommitteeMember', backref='committee', lazy=True, cascade='all, delete-orphan')
    meetings = db.relationship('CommitteeMeeting', backref='committee', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'committee_name': self.committee_name, 'committee_type': self.committee_type,
            'formation_date': self.formation_date.isoformat() if self.formation_date else None,
            'tenure': self.tenure, 'members': [m.to_dict() for m in self.members],
            'meetings': [m.to_dict() for m in self.meetings],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class CommitteeMember(db.Model):
    __tablename__ = 'committee_member'
    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey('disaster_committee.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200))
    organization = db.Column(db.String(300))
    contact_number = db.Column(db.String(50))

    def to_dict(self):
        return {'id': self.id, 'committee_id': self.committee_id, 'name': self.name, 'position': self.position, 'organization': self.organization, 'contact_number': self.contact_number}

class CommitteeMeeting(db.Model):
    __tablename__ = 'committee_meeting'
    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey('disaster_committee.id'), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    agenda = db.Column(db.Text)
    decisions = db.Column(db.Text)
    action_items = db.Column(db.Text)

    def to_dict(self):
        return {'id': self.id, 'committee_id': self.committee_id, 'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None, 'agenda': self.agenda, 'decisions': self.decisions, 'action_items': self.action_items}


# ============================================
# MODULE 12: VEHICLE MANAGEMENT
# ============================================

VEHICLE_TYPES = ['Ambulance', 'Fire Engine', 'Excavator', 'Tractor', 'Pickup', 'Truck', 'Jeep', 'Motorcycle', 'Boat']

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    owner_organization = db.Column(db.String(300))
    driver_name = db.Column(db.String(200))
    driver_contact = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Available')
    current_coordinates = db.Column(db.String(100))
    fuel_status = db.Column(db.String(50))
    capacity = db.Column(db.String(100))
    last_service_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id, 'vehicle_number': self.vehicle_number, 'vehicle_type': self.vehicle_type,
            'owner_organization': self.owner_organization, 'driver_name': self.driver_name,
            'driver_contact': self.driver_contact, 'status': self.status,
            'current_coordinates': self.current_coordinates, 'fuel_status': self.fuel_status,
            'capacity': self.capacity,
            'last_service_date': self.last_service_date.isoformat() if self.last_service_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# MODULE 13: SHELTER AND EVACUATION MANAGEMENT
# ============================================

class Shelter(db.Model):
    __tablename__ = 'shelter'
    id = db.Column(db.Integer, primary_key=True)
    shelter_name = db.Column(db.String(300), nullable=False)
    shelter_type = db.Column(db.String(100))
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    location = db.Column(db.String(300))
    coordinates = db.Column(db.String(100))
    boundary_polygon = db.Column(db.Text)
    total_capacity = db.Column(db.Integer)
    male_capacity = db.Column(db.Integer)
    female_capacity = db.Column(db.Integer)
    children_capacity = db.Column(db.Integer)
    water_available = db.Column(db.Boolean, default=False)
    toilet_available = db.Column(db.Boolean, default=False)
    electricity_available = db.Column(db.Boolean, default=False)
    kitchen_available = db.Column(db.Boolean, default=False)
    medical_support = db.Column(db.Boolean, default=False)
    accessibility_support = db.Column(db.Boolean, default=False)
    current_occupancy = db.Column(db.Integer, default=0)
    available_space = db.Column(db.Integer)
    shelter_manager = db.Column(db.String(200))
    contact_number = db.Column(db.String(50))
    evacuation_routes = db.Column(db.Text)
    assembly_points = db.Column(db.Text)
    linked_risk_zones = db.Column(db.Text)
    linked_vulnerable_households = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    created_by = db.Column(db.Integer)

    ward = db.relationship('Ward', backref='shelters', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'shelter_name': self.shelter_name, 'shelter_type': self.shelter_type,
            'ward_id': self.ward_id, 'ward_name': self.ward.name if self.ward else None,
            'location': self.location, 'coordinates': self.coordinates,
            'boundary_polygon': self.boundary_polygon, 'total_capacity': self.total_capacity,
            'male_capacity': self.male_capacity, 'female_capacity': self.female_capacity,
            'children_capacity': self.children_capacity,
            'water_available': self.water_available, 'toilet_available': self.toilet_available,
            'electricity_available': self.electricity_available, 'kitchen_available': self.kitchen_available,
            'medical_support': self.medical_support, 'accessibility_support': self.accessibility_support,
            'current_occupancy': self.current_occupancy, 'available_space': self.available_space,
            'shelter_manager': self.shelter_manager, 'contact_number': self.contact_number,
            'evacuation_routes': self.evacuation_routes, 'assembly_points': self.assembly_points,
            'linked_risk_zones': self.linked_risk_zones, 'linked_vulnerable_households': self.linked_vulnerable_households,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
