import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from shared import db, utc_now
from new_models import (
    CriticalInfrastructure, InfrastructurePhoto, InfrastructureDocument,
    EmergencyFacility,
    RiskLayer,
    EmergencyContact,
    Cluster, ClusterMember, ClusterMeeting, ClusterDeployment,
    VulnerableHousehold,
    DisabledPerson,
    HighRiskPerson,
    Volunteer, VolunteerTraining,
    RapidResponseTeam, RRTMember, RRTResource,
    DisasterCommittee, CommitteeMember, CommitteeMeeting,
    Vehicle,
    Shelter,
)

new_bp = Blueprint('new', __name__, template_folder='templates')


def int_or_none(data, key):
    v = data.get(key)
    if v is None or v == '':
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def float_or_none(data, key):
    v = data.get(key)
    if v is None or v == '':
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def bool_or_false(data, key):
    v = data.get(key)
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ('true', '1', 'yes')
    return bool(v)


def parse_coordinates(data, field='coordinates'):
    val = data.get(field)
    if val and isinstance(val, str) and ',' in val:
        parts = val.split(',', 1)
        try:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            return f"{lat},{lng}"
        except (ValueError, TypeError):
            pass
    return val or None


def save_upload(file, subdir='new_modules'):
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subdir)
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return f"uploads/{subdir}/{filename}"


def log_activity(action, module, record_id=None, details=None):
    try:
        from app import ActivityLog
        entry = ActivityLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            module=module,
            record_id=str(record_id) if record_id else None,
            details=details,
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()


# ================================================================
# PAGE ROUTES
# ================================================================

@new_bp.route('/critical-infrastructure')
@login_required
def critical_infrastructure_page():
    return render_template('critical_infrastructure.html')


@new_bp.route('/emergency-facilities')
@login_required
def emergency_facilities_page():
    return render_template('emergency_facilities.html')


@new_bp.route('/risk-layers')
@login_required
def risk_layers_page():
    return render_template('risk_layers.html')


@new_bp.route('/emergency-contacts')
@login_required
def emergency_contacts_page():
    return render_template('emergency_contacts.html')


@new_bp.route('/clusters')
@login_required
def clusters_page():
    return render_template('clusters.html')


@new_bp.route('/vulnerable-population')
@login_required
def vulnerable_population_page():
    return render_template('vulnerable_population.html')


@new_bp.route('/differently-abled')
@login_required
def differently_abled_page():
    return render_template('differently_abled.html')


@new_bp.route('/high-risk-population')
@login_required
def high_risk_population_page():
    return render_template('high_risk_population.html')


@new_bp.route('/volunteers')
@login_required
def volunteers_page():
    return render_template('volunteers.html')


@new_bp.route('/rrt')
@login_required
def rrt_page():
    return render_template('rrt.html')


@new_bp.route('/committees')
@login_required
def committees_page():
    return render_template('committees.html')


@new_bp.route('/vehicles')
@login_required
def vehicles_page():
    return render_template('vehicles.html')


@new_bp.route('/shelters')
@login_required
def shelters_page():
    return render_template('shelters.html')


# ================================================================
# API: CRITICAL INFRASTRUCTURE
# ================================================================

@new_bp.route('/api/critical-infrastructure', methods=['GET', 'POST'])
@login_required
def api_critical_infrastructure():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        infra_type = request.args.get('type')
        q = CriticalInfrastructure.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        if infra_type:
            q = q.filter_by(infrastructure_type=infra_type)
        return jsonify({'success': True, 'data': [item.to_dict() for item in q.all()]})

    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403

    data = request.form.to_dict() if request.files else request.get_json(force=True)
    if isinstance(data, dict) and request.files:
        pass
    elif isinstance(data, dict):
        pass
    else:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    infra_id = data.get('infrastructure_id') or f"INF-{uuid.uuid4().hex[:8].upper()}"
    item = CriticalInfrastructure(
        infrastructure_id=infra_id,
        name=data.get('name'),
        infrastructure_type=data.get('infrastructure_type'),
        description=data.get('description'),
        ward_id=int_or_none(data, 'ward_id'),
        settlement=data.get('settlement'),
        coordinates=parse_coordinates(data),
        elevation=float_or_none(data, 'elevation'),
        capacity=data.get('capacity'),
        current_status=data.get('current_status', 'Operational'),
        contact_person=data.get('contact_person'),
        contact_number=data.get('contact_number'),
        accessibility_status=data.get('accessibility_status', 'Accessible'),
        available_facilities=data.get('available_facilities'),
        created_by=current_user.id,
    )
    db.session.add(item)
    db.session.flush()

    if request.files:
        for key in request.files:
            files = request.files.getlist(key)
            for f in files:
                if f and f.filename:
                    path = save_upload(f, 'infrastructure')
                    if key == 'photos':
                        db.session.add(InfrastructurePhoto(infrastructure_id=item.id, filename=path, original_name=f.filename))
                    else:
                        db.session.add(InfrastructureDocument(infrastructure_id=item.id, filename=path, original_name=f.filename))

    db.session.commit()
    log_activity('create', 'CriticalInfrastructure', item.id, f"Created infrastructure: {item.name}")
    return jsonify({'success': True, 'data': item.to_dict()})


@new_bp.route('/api/critical-infrastructure/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_critical_infrastructure_item(id):
    item = CriticalInfrastructure.query.get_or_404(id)
    if request.method == 'GET':
        result = item.to_dict()
        result['photos'] = [{'id': p.id, 'url': p.filename, 'original_name': p.original_name} for p in item.photos]
        result['documents'] = [{'id': d.id, 'url': d.filename, 'original_name': d.original_name} for d in item.documents]
        return jsonify({'success': True, 'data': result})

    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        log_activity('delete', 'CriticalInfrastructure', id, f"Deleted infrastructure: {item.name}")
        return jsonify({'success': True, 'message': 'Deleted'})

    data = request.get_json(force=True)
    for field in ['name', 'infrastructure_type', 'description', 'settlement', 'capacity',
                  'current_status', 'contact_person', 'contact_number', 'accessibility_status',
                  'available_facilities']:
        if field in data:
            setattr(item, field, data[field])
    if 'ward_id' in data:
        item.ward_id = int_or_none(data, 'ward_id')
    if 'elevation' in data:
        item.elevation = float_or_none(data, 'elevation')
    if 'coordinates' in data:
        item.coordinates = parse_coordinates(data, 'coordinates')
    db.session.commit()
    log_activity('update', 'CriticalInfrastructure', id, f"Updated infrastructure: {item.name}")
    return jsonify({'success': True, 'data': item.to_dict()})


@new_bp.route('/api/critical-infrastructure/<int:id>/upload', methods=['POST'])
@login_required
def api_infrastructure_upload(id):
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    item = CriticalInfrastructure.query.get_or_404(id)
    if 'photo' in request.files:
        for f in request.files.getlist('photo'):
            if f and f.filename:
                path = save_upload(f, 'infrastructure')
                db.session.add(InfrastructurePhoto(infrastructure_id=item.id, filename=path, original_name=f.filename))
    if 'document' in request.files:
        for f in request.files.getlist('document'):
            if f and f.filename:
                path = save_upload(f, 'infrastructure')
                db.session.add(InfrastructureDocument(infrastructure_id=item.id, filename=path, original_name=f.filename))
    db.session.commit()
    return jsonify({'success': True})


# ================================================================
# API: EMERGENCY FACILITIES
# ================================================================

@new_bp.route('/api/emergency-facilities', methods=['GET', 'POST'])
@login_required
def api_emergency_facilities():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        ftype = request.args.get('facility_type')
        q = EmergencyFacility.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        if ftype:
            q = q.filter_by(facility_type=ftype)
        return jsonify({'success': True, 'data': [f.to_dict() for f in q.all()]})

    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403

    data = request.get_json(force=True)
    facility = EmergencyFacility(
        facility_name=data.get('facility_name'),
        facility_type=data.get('facility_type'),
        ward_id=int_or_none(data, 'ward_id'),
        location_description=data.get('location_description'),
        coordinates=parse_coordinates(data),
        polygon_boundary=data.get('polygon_boundary'),
        max_capacity=int_or_none(data, 'max_capacity'),
        current_occupancy=int_or_none(data, 'current_occupancy') or 0,
        water_availability=bool_or_false(data, 'water_availability'),
        electricity_availability=bool_or_false(data, 'electricity_availability'),
        toilet_availability=bool_or_false(data, 'toilet_availability'),
        kitchen_availability=bool_or_false(data, 'kitchen_availability'),
        internet_availability=bool_or_false(data, 'internet_availability'),
        accessibility_disabled=bool_or_false(data, 'accessibility_disabled'),
        managing_organization=data.get('managing_organization'),
        focal_person=data.get('focal_person'),
        contact_number=data.get('contact_number'),
        created_by=current_user.id,
    )
    db.session.add(facility)
    db.session.commit()
    log_activity('create', 'EmergencyFacility', facility.id, f"Created facility: {facility.facility_name}")
    return jsonify({'success': True, 'data': facility.to_dict()})


@new_bp.route('/api/emergency-facilities/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_emergency_facility_item(id):
    facility = EmergencyFacility.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': facility.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(facility)
        db.session.commit()
        log_activity('delete', 'EmergencyFacility', id, f"Deleted facility: {facility.facility_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['facility_name', 'facility_type', 'location_description', 'polygon_boundary',
                  'managing_organization', 'focal_person', 'contact_number']:
        if field in data:
            setattr(facility, field, data[field])
    if 'ward_id' in data:
        facility.ward_id = int_or_none(data, 'ward_id')
    if 'max_capacity' in data:
        facility.max_capacity = int_or_none(data, 'max_capacity')
    if 'current_occupancy' in data:
        facility.current_occupancy = int_or_none(data, 'current_occupancy')
    if 'coordinates' in data:
        facility.coordinates = parse_coordinates(data, 'coordinates')
    for field in ['water_availability', 'electricity_availability', 'toilet_availability',
                  'kitchen_availability', 'internet_availability', 'accessibility_disabled']:
        if field in data:
            setattr(facility, field, bool_or_false(data, field))
    db.session.commit()
    log_activity('update', 'EmergencyFacility', id, f"Updated facility: {facility.facility_name}")
    return jsonify({'success': True, 'data': facility.to_dict()})


# ================================================================
# API: RISK LAYERS
# ================================================================

@new_bp.route('/api/risk-layers', methods=['GET', 'POST'])
@login_required
def api_risk_layers():
    if request.method == 'GET':
        risk_type = request.args.get('risk_type')
        level = request.args.get('risk_level')
        q = RiskLayer.query
        if risk_type:
            q = q.filter_by(risk_type=risk_type)
        if level:
            q = q.filter_by(risk_level=level)
        return jsonify({'success': True, 'data': [r.to_dict() for r in q.all()]})

    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403

    data = request.get_json(force=True)
    layer = RiskLayer(
        name=data.get('name'),
        risk_type=data.get('risk_type'),
        risk_level=data.get('risk_level'),
        polygon_boundary=data.get('polygon_boundary'),
        coordinates=parse_coordinates(data),
        area_coverage=float_or_none(data, 'area_coverage'),
        affected_settlements=data.get('affected_settlements'),
        affected_households=int_or_none(data, 'affected_households'),
        population_at_risk=int_or_none(data, 'population_at_risk'),
        created_by=current_user.id,
    )
    db.session.add(layer)
    db.session.commit()
    log_activity('create', 'RiskLayer', layer.id, f"Created risk layer: {layer.name}")
    return jsonify({'success': True, 'data': layer.to_dict()})


@new_bp.route('/api/risk-layers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_risk_layer_item(id):
    layer = RiskLayer.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': layer.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(layer)
        db.session.commit()
        log_activity('delete', 'RiskLayer', id, f"Deleted risk layer: {layer.name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['name', 'risk_type', 'risk_level', 'polygon_boundary', 'affected_settlements']:
        if field in data:
            setattr(layer, field, data[field])
    if 'area_coverage' in data:
        layer.area_coverage = float_or_none(data, 'area_coverage')
    if 'affected_households' in data:
        layer.affected_households = int_or_none(data, 'affected_households')
    if 'population_at_risk' in data:
        layer.population_at_risk = int_or_none(data, 'population_at_risk')
    if 'coordinates' in data:
        layer.coordinates = parse_coordinates(data, 'coordinates')
    db.session.commit()
    log_activity('update', 'RiskLayer', id, f"Updated risk layer: {layer.name}")
    return jsonify({'success': True, 'data': layer.to_dict()})


# ================================================================
# API: EMERGENCY CONTACTS
# ================================================================

@new_bp.route('/api/emergency-contacts', methods=['GET', 'POST'])
@login_required
def api_emergency_contacts():
    if request.method == 'GET':
        cat = request.args.get('category')
        ward_id = request.args.get('ward_id', type=int)
        q = EmergencyContact.query
        if cat:
            q = q.filter_by(category=cat)
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        return jsonify({'success': True, 'data': [c.to_dict() for c in q.all()]})

    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403

    data = request.get_json(force=True)
    contact = EmergencyContact(
        organization_name=data.get('organization_name'),
        contact_person=data.get('contact_person'),
        designation=data.get('designation'),
        category=data.get('category'),
        sub_category=data.get('sub_category'),
        mobile_number=data.get('mobile_number'),
        alternative_number=data.get('alternative_number'),
        email=data.get('email'),
        address=data.get('address'),
        ward_id=int_or_none(data, 'ward_id'),
        coordinates=parse_coordinates(data),
        availability_status=data.get('availability_status', 'Available'),
        service_area=data.get('service_area'),
        created_by=current_user.id,
    )
    db.session.add(contact)
    db.session.commit()
    log_activity('create', 'EmergencyContact', contact.id, f"Created contact: {contact.organization_name}")
    return jsonify({'success': True, 'data': contact.to_dict()})


@new_bp.route('/api/emergency-contacts/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_emergency_contact_item(id):
    contact = EmergencyContact.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': contact.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(contact)
        db.session.commit()
        log_activity('delete', 'EmergencyContact', id, f"Deleted contact: {contact.organization_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['organization_name', 'contact_person', 'designation', 'category', 'sub_category',
                  'mobile_number', 'alternative_number', 'email', 'address', 'availability_status', 'service_area']:
        if field in data:
            setattr(contact, field, data[field])
    if 'ward_id' in data:
        contact.ward_id = int_or_none(data, 'ward_id')
    if 'coordinates' in data:
        contact.coordinates = parse_coordinates(data, 'coordinates')
    db.session.commit()
    log_activity('update', 'EmergencyContact', id, f"Updated contact: {contact.organization_name}")
    return jsonify({'success': True, 'data': contact.to_dict()})


# ================================================================
# API: CLUSTERS
# ================================================================

@new_bp.route('/api/clusters', methods=['GET', 'POST'])
@login_required
def api_clusters():
    if request.method == 'GET':
        return jsonify({'success': True, 'data': [c.to_dict() for c in Cluster.query.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    cluster = Cluster(
        cluster_name=data.get('cluster_name'),
        lead_organization=data.get('lead_organization'),
        focal_person=data.get('focal_person'),
        contact_details=data.get('contact_details'),
        resource_capacity=data.get('resource_capacity'),
        available_equipment=data.get('available_equipment'),
        coverage_area=data.get('coverage_area'),
        gis_coverage_boundary=data.get('gis_coverage_boundary'),
        created_by=current_user.id,
    )
    members = data.get('members', [])
    db.session.add(cluster)
    db.session.flush()
    for m in members:
        db.session.add(ClusterMember(cluster_id=cluster.id, **m))
    db.session.commit()
    log_activity('create', 'Cluster', cluster.id, f"Created cluster: {cluster.cluster_name}")
    return jsonify({'success': True, 'data': cluster.to_dict()})


@new_bp.route('/api/clusters/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_cluster_item(id):
    cluster = Cluster.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': cluster.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(cluster)
        db.session.commit()
        log_activity('delete', 'Cluster', id, f"Deleted cluster: {cluster.cluster_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['cluster_name', 'lead_organization', 'focal_person', 'contact_details',
                  'resource_capacity', 'available_equipment', 'coverage_area', 'gis_coverage_boundary']:
        if field in data:
            setattr(cluster, field, data[field])
    if 'members' in data:
        ClusterMember.query.filter_by(cluster_id=cluster.id).delete()
        for m in data['members']:
            db.session.add(ClusterMember(cluster_id=cluster.id, **m))
    db.session.commit()
    log_activity('update', 'Cluster', id, f"Updated cluster: {cluster.cluster_name}")
    return jsonify({'success': True, 'data': cluster.to_dict()})


@new_bp.route('/api/clusters/<int:id>/meetings', methods=['GET', 'POST'])
@login_required
def api_cluster_meetings(id):
    cluster = Cluster.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': [m.to_dict() for m in cluster.meetings]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    meeting = ClusterMeeting(
        cluster_id=cluster.id,
        meeting_date=datetime.strptime(data['meeting_date'], '%Y-%m-%d').date() if data.get('meeting_date') else None,
        agenda=data.get('agenda'),
        decisions=data.get('decisions'),
        action_items=data.get('action_items'),
    )
    db.session.add(meeting)
    db.session.commit()
    return jsonify({'success': True, 'data': meeting.to_dict()})


@new_bp.route('/api/clusters/<int:id>/deployments', methods=['GET', 'POST'])
@login_required
def api_cluster_deployments(id):
    cluster = Cluster.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': [d.to_dict() for d in cluster.deployments]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    deployment = ClusterDeployment(
        cluster_id=cluster.id,
        deployment_date=datetime.strptime(data['deployment_date'], '%Y-%m-%d').date() if data.get('deployment_date') else None,
        location=data.get('location'),
        details=data.get('details'),
        status=data.get('status', 'Active'),
    )
    db.session.add(deployment)
    db.session.commit()
    return jsonify({'success': True, 'data': deployment.to_dict()})


# ================================================================
# API: VULNERABLE POPULATION
# ================================================================

@new_bp.route('/api/vulnerable-population', methods=['GET', 'POST'])
@login_required
def api_vulnerable_population():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        cat = request.args.get('category')
        q = VulnerableHousehold.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        if cat:
            q = q.filter_by(category=cat)
        return jsonify({'success': True, 'data': [h.to_dict() for h in q.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    hh = VulnerableHousehold(
        household_id=data.get('household_id') or f"VUL-{uuid.uuid4().hex[:8].upper()}",
        head_of_household=data.get('head_of_household'),
        family_size=int_or_none(data, 'family_size'),
        category=data.get('category'),
        ward_id=int_or_none(data, 'ward_id'),
        settlement=data.get('settlement'),
        contact_number=data.get('contact_number'),
        coordinates=parse_coordinates(data),
        disaster_exposure=data.get('disaster_exposure'),
        evacuation_priority=data.get('evacuation_priority', 'Normal'),
        created_by=current_user.id,
    )
    db.session.add(hh)
    db.session.commit()
    log_activity('create', 'VulnerableHousehold', hh.id, f"Created vulnerable household: {hh.head_of_household}")
    return jsonify({'success': True, 'data': hh.to_dict()})


@new_bp.route('/api/vulnerable-population/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_vulnerable_population_item(id):
    hh = VulnerableHousehold.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': hh.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(hh)
        db.session.commit()
        log_activity('delete', 'VulnerableHousehold', id, f"Deleted vulnerable household: {hh.head_of_household}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['head_of_household', 'category', 'settlement', 'contact_number', 'disaster_exposure', 'evacuation_priority']:
        if field in data:
            setattr(hh, field, data[field])
    if 'family_size' in data:
        hh.family_size = int_or_none(data, 'family_size')
    if 'ward_id' in data:
        hh.ward_id = int_or_none(data, 'ward_id')
    if 'coordinates' in data:
        hh.coordinates = parse_coordinates(data, 'coordinates')
    db.session.commit()
    log_activity('update', 'VulnerableHousehold', id, f"Updated vulnerable household: {hh.head_of_household}")
    return jsonify({'success': True, 'data': hh.to_dict()})


# ================================================================
# API: DIFFERENTLY ABLED PERSONS
# ================================================================

@new_bp.route('/api/differently-abled', methods=['GET', 'POST'])
@login_required
def api_differently_abled():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        q = DisabledPerson.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        return jsonify({'success': True, 'data': [p.to_dict() for p in q.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    person = DisabledPerson(
        person_name=data.get('person_name'),
        gender=data.get('gender'),
        age=int_or_none(data, 'age'),
        ward_id=int_or_none(data, 'ward_id'),
        settlement=data.get('settlement'),
        contact_number=data.get('contact_number'),
        physical_disability=bool_or_false(data, 'physical_disability'),
        visual_disability=bool_or_false(data, 'visual_disability'),
        hearing_disability=bool_or_false(data, 'hearing_disability'),
        intellectual_disability=bool_or_false(data, 'intellectual_disability'),
        multiple_disability=bool_or_false(data, 'multiple_disability'),
        caregiver_name=data.get('caregiver_name'),
        caregiver_contact=data.get('caregiver_contact'),
        mobility_requirement=data.get('mobility_requirement'),
        medical_requirement=data.get('medical_requirement'),
        evacuation_requirement=data.get('evacuation_requirement'),
        coordinates=parse_coordinates(data),
        created_by=current_user.id,
    )
    db.session.add(person)
    db.session.commit()
    log_activity('create', 'DisabledPerson', person.id, f"Created disabled person: {person.person_name}")
    return jsonify({'success': True, 'data': person.to_dict()})


@new_bp.route('/api/differently-abled/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_differently_abled_item(id):
    person = DisabledPerson.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': person.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(person)
        db.session.commit()
        log_activity('delete', 'DisabledPerson', id, f"Deleted disabled person: {person.person_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['person_name', 'gender', 'settlement', 'contact_number', 'caregiver_name',
                  'caregiver_contact', 'mobility_requirement', 'medical_requirement', 'evacuation_requirement']:
        if field in data:
            setattr(person, field, data[field])
    if 'age' in data:
        person.age = int_or_none(data, 'age')
    if 'ward_id' in data:
        person.ward_id = int_or_none(data, 'ward_id')
    if 'coordinates' in data:
        person.coordinates = parse_coordinates(data, 'coordinates')
    for field in ['physical_disability', 'visual_disability', 'hearing_disability',
                  'intellectual_disability', 'multiple_disability']:
        if field in data:
            setattr(person, field, bool_or_false(data, field))
    db.session.commit()
    log_activity('update', 'DisabledPerson', id, f"Updated disabled person: {person.person_name}")
    return jsonify({'success': True, 'data': person.to_dict()})


# ================================================================
# API: HIGH RISK POPULATION
# ================================================================

@new_bp.route('/api/high-risk-population', methods=['GET', 'POST'])
@login_required
def api_high_risk_population():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        cat = request.args.get('category')
        q = HighRiskPerson.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        if cat:
            q = q.filter_by(category=cat)
        return jsonify({'success': True, 'data': [p.to_dict() for p in q.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    person = HighRiskPerson(
        person_name=data.get('person_name'),
        age=int_or_none(data, 'age'),
        gender=data.get('gender'),
        category=data.get('category'),
        contact_number=data.get('contact_number'),
        ward_id=int_or_none(data, 'ward_id'),
        settlement=data.get('settlement'),
        health_condition=data.get('health_condition'),
        health_facility_linked=data.get('health_facility_linked'),
        emergency_contact=data.get('emergency_contact'),
        coordinates=parse_coordinates(data),
        created_by=current_user.id,
    )
    db.session.add(person)
    db.session.commit()
    log_activity('create', 'HighRiskPerson', person.id, f"Created high risk person: {person.person_name}")
    return jsonify({'success': True, 'data': person.to_dict()})


@new_bp.route('/api/high-risk-population/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_high_risk_population_item(id):
    person = HighRiskPerson.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': person.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(person)
        db.session.commit()
        log_activity('delete', 'HighRiskPerson', id, f"Deleted high risk person: {person.person_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['person_name', 'gender', 'category', 'contact_number', 'settlement',
                  'health_condition', 'health_facility_linked', 'emergency_contact']:
        if field in data:
            setattr(person, field, data[field])
    if 'age' in data:
        person.age = int_or_none(data, 'age')
    if 'ward_id' in data:
        person.ward_id = int_or_none(data, 'ward_id')
    if 'coordinates' in data:
        person.coordinates = parse_coordinates(data, 'coordinates')
    db.session.commit()
    log_activity('update', 'HighRiskPerson', id, f"Updated high risk person: {person.person_name}")
    return jsonify({'success': True, 'data': person.to_dict()})


# ================================================================
# API: VOLUNTEERS
# ================================================================

@new_bp.route('/api/volunteers', methods=['GET', 'POST'])
@login_required
def api_volunteers():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        status = request.args.get('status')
        skill = request.args.get('skill')
        q = Volunteer.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        if status:
            q = q.filter_by(availability_status=status)
        if skill:
            q = q.filter(Volunteer.skills.contains(skill))
        return jsonify({'success': True, 'data': [v.to_dict() for v in q.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    skills = data.get('skills', [])
    if isinstance(skills, list):
        skills = ','.join(skills)
    volunteer = Volunteer(
        volunteer_id=data.get('volunteer_id') or f"VOL-{uuid.uuid4().hex[:8].upper()}",
        name=data.get('name'),
        gender=data.get('gender'),
        age=int_or_none(data, 'age'),
        ward_id=int_or_none(data, 'ward_id'),
        contact_number=data.get('contact_number'),
        email=data.get('email'),
        skills=skills,
        home_coordinates=parse_coordinates(data, 'home_coordinates'),
        availability_status=data.get('availability_status', 'Available'),
        created_by=current_user.id,
    )
    db.session.add(volunteer)
    db.session.flush()
    trainings = data.get('trainings', [])
    for t in trainings:
        db.session.add(VolunteerTraining(
            volunteer_id=volunteer.id,
            training_name=t.get('training_name'),
            training_date=datetime.strptime(t['training_date'], '%Y-%m-%d').date() if t.get('training_date') else None,
            certification_status=t.get('certification_status', 'Pending'),
        ))
    db.session.commit()
    log_activity('create', 'Volunteer', volunteer.id, f"Created volunteer: {volunteer.name}")
    return jsonify({'success': True, 'data': volunteer.to_dict()})


@new_bp.route('/api/volunteers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_volunteer_item(id):
    volunteer = Volunteer.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': volunteer.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(volunteer)
        db.session.commit()
        log_activity('delete', 'Volunteer', id, f"Deleted volunteer: {volunteer.name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['name', 'gender', 'contact_number', 'email', 'availability_status']:
        if field in data:
            setattr(volunteer, field, data[field])
    if 'age' in data:
        volunteer.age = int_or_none(data, 'age')
    if 'ward_id' in data:
        volunteer.ward_id = int_or_none(data, 'ward_id')
    if 'home_coordinates' in data:
        volunteer.home_coordinates = parse_coordinates(data, 'home_coordinates')
    if 'skills' in data:
        s = data['skills']
        volunteer.skills = ','.join(s) if isinstance(s, list) else s
    if 'trainings' in data:
        VolunteerTraining.query.filter_by(volunteer_id=volunteer.id).delete()
        for t in data['trainings']:
            db.session.add(VolunteerTraining(
                volunteer_id=volunteer.id,
                training_name=t.get('training_name'),
                training_date=datetime.strptime(t['training_date'], '%Y-%m-%d').date() if t.get('training_date') else None,
                certification_status=t.get('certification_status', 'Pending'),
            ))
    db.session.commit()
    log_activity('update', 'Volunteer', id, f"Updated volunteer: {volunteer.name}")
    return jsonify({'success': True, 'data': volunteer.to_dict()})


@new_bp.route('/api/volunteers/<int:id>/trainings', methods=['POST'])
@login_required
def api_volunteer_add_training(id):
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    volunteer = Volunteer.query.get_or_404(id)
    data = request.get_json(force=True)
    t = VolunteerTraining(
        volunteer_id=volunteer.id,
        training_name=data.get('training_name'),
        training_date=datetime.strptime(data['training_date'], '%Y-%m-%d').date() if data.get('training_date') else None,
        certification_status=data.get('certification_status', 'Pending'),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True, 'data': t.to_dict()})


# ================================================================
# API: RAPID RESPONSE TEAM
# ================================================================

@new_bp.route('/api/rrt', methods=['GET', 'POST'])
@login_required
def api_rrt():
    if request.method == 'GET':
        return jsonify({'success': True, 'data': [t.to_dict() for t in RapidResponseTeam.query.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    team = RapidResponseTeam(
        team_name=data.get('team_name'),
        team_type=data.get('team_type'),
        coverage_area=data.get('coverage_area'),
        team_leader=data.get('team_leader'),
        contact_number=data.get('contact_number'),
        base_coordinates=parse_coordinates(data, 'base_coordinates'),
        created_by=current_user.id,
    )
    db.session.add(team)
    db.session.flush()
    for m in data.get('members', []):
        db.session.add(RRTMember(team_id=team.id, **m))
    for r in data.get('resources', []):
        db.session.add(RRTResource(team_id=team.id, **r))
    db.session.commit()
    log_activity('create', 'RapidResponseTeam', team.id, f"Created RRT: {team.team_name}")
    return jsonify({'success': True, 'data': team.to_dict()})


@new_bp.route('/api/rrt/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_rrt_item(id):
    team = RapidResponseTeam.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': team.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(team)
        db.session.commit()
        log_activity('delete', 'RapidResponseTeam', id, f"Deleted RRT: {team.team_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['team_name', 'team_type', 'coverage_area', 'team_leader', 'contact_number']:
        if field in data:
            setattr(team, field, data[field])
    if 'base_coordinates' in data:
        team.base_coordinates = parse_coordinates(data, 'base_coordinates')
    if 'members' in data:
        RRTMember.query.filter_by(team_id=team.id).delete()
        for m in data['members']:
            db.session.add(RRTMember(team_id=team.id, **m))
    if 'resources' in data:
        RRTResource.query.filter_by(team_id=team.id).delete()
        for r in data['resources']:
            db.session.add(RRTResource(team_id=team.id, **r))
    db.session.commit()
    log_activity('update', 'RapidResponseTeam', id, f"Updated RRT: {team.team_name}")
    return jsonify({'success': True, 'data': team.to_dict()})


# ================================================================
# API: DISASTER COMMITTEES
# ================================================================

@new_bp.route('/api/committees', methods=['GET', 'POST'])
@login_required
def api_committees():
    if request.method == 'GET':
        return jsonify({'success': True, 'data': [c.to_dict() for c in DisasterCommittee.query.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    committee = DisasterCommittee(
        committee_name=data.get('committee_name'),
        committee_type=data.get('committee_type'),
        formation_date=datetime.strptime(data['formation_date'], '%Y-%m-%d').date() if data.get('formation_date') else None,
        tenure=data.get('tenure'),
        created_by=current_user.id,
    )
    db.session.add(committee)
    db.session.flush()
    for m in data.get('members', []):
        db.session.add(CommitteeMember(committee_id=committee.id, **m))
    db.session.commit()
    log_activity('create', 'DisasterCommittee', committee.id, f"Created committee: {committee.committee_name}")
    return jsonify({'success': True, 'data': committee.to_dict()})


@new_bp.route('/api/committees/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_committee_item(id):
    committee = DisasterCommittee.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': committee.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(committee)
        db.session.commit()
        log_activity('delete', 'DisasterCommittee', id, f"Deleted committee: {committee.committee_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['committee_name', 'committee_type', 'tenure']:
        if field in data:
            setattr(committee, field, data[field])
    if 'formation_date' in data and data['formation_date']:
        committee.formation_date = datetime.strptime(data['formation_date'], '%Y-%m-%d').date()
    if 'members' in data:
        CommitteeMember.query.filter_by(committee_id=committee.id).delete()
        for m in data['members']:
            db.session.add(CommitteeMember(committee_id=committee.id, **m))
    db.session.commit()
    log_activity('update', 'DisasterCommittee', id, f"Updated committee: {committee.committee_name}")
    return jsonify({'success': True, 'data': committee.to_dict()})


@new_bp.route('/api/committees/<int:id>/meetings', methods=['GET', 'POST'])
@login_required
def api_committee_meetings(id):
    committee = DisasterCommittee.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': [m.to_dict() for m in committee.meetings]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    meeting = CommitteeMeeting(
        committee_id=committee.id,
        meeting_date=datetime.strptime(data['meeting_date'], '%Y-%m-%d').date() if data.get('meeting_date') else None,
        agenda=data.get('agenda'),
        decisions=data.get('decisions'),
        action_items=data.get('action_items'),
    )
    db.session.add(meeting)
    db.session.commit()
    return jsonify({'success': True, 'data': meeting.to_dict()})


# ================================================================
# API: VEHICLES
# ================================================================

@new_bp.route('/api/vehicles', methods=['GET', 'POST'])
@login_required
def api_vehicles():
    if request.method == 'GET':
        vtype = request.args.get('vehicle_type')
        status = request.args.get('status')
        q = Vehicle.query
        if vtype:
            q = q.filter_by(vehicle_type=vtype)
        if status:
            q = q.filter_by(status=status)
        return jsonify({'success': True, 'data': [v.to_dict() for v in q.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    vehicle = Vehicle(
        vehicle_number=data.get('vehicle_number'),
        vehicle_type=data.get('vehicle_type'),
        owner_organization=data.get('owner_organization'),
        driver_name=data.get('driver_name'),
        driver_contact=data.get('driver_contact'),
        status=data.get('status', 'Available'),
        current_coordinates=parse_coordinates(data, 'current_coordinates'),
        fuel_status=data.get('fuel_status'),
        capacity=data.get('capacity'),
        last_service_date=datetime.strptime(data['last_service_date'], '%Y-%m-%d').date() if data.get('last_service_date') else None,
        created_by=current_user.id,
    )
    db.session.add(vehicle)
    db.session.commit()
    log_activity('create', 'Vehicle', vehicle.id, f"Created vehicle: {vehicle.vehicle_number}")
    return jsonify({'success': True, 'data': vehicle.to_dict()})


@new_bp.route('/api/vehicles/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_vehicle_item(id):
    vehicle = Vehicle.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': vehicle.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(vehicle)
        db.session.commit()
        log_activity('delete', 'Vehicle', id, f"Deleted vehicle: {vehicle.vehicle_number}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['vehicle_number', 'vehicle_type', 'owner_organization', 'driver_name',
                  'driver_contact', 'status', 'fuel_status', 'capacity']:
        if field in data:
            setattr(vehicle, field, data[field])
    if 'current_coordinates' in data:
        vehicle.current_coordinates = parse_coordinates(data, 'current_coordinates')
    if 'last_service_date' in data and data['last_service_date']:
        vehicle.last_service_date = datetime.strptime(data['last_service_date'], '%Y-%m-%d').date()
    db.session.commit()
    log_activity('update', 'Vehicle', id, f"Updated vehicle: {vehicle.vehicle_number}")
    return jsonify({'success': True, 'data': vehicle.to_dict()})


# ================================================================
# API: SHELTERS
# ================================================================

@new_bp.route('/api/shelters', methods=['GET', 'POST'])
@login_required
def api_shelters():
    if request.method == 'GET':
        ward_id = request.args.get('ward_id', type=int)
        stype = request.args.get('shelter_type')
        q = Shelter.query
        if ward_id:
            q = q.filter_by(ward_id=ward_id)
        if stype:
            q = q.filter_by(shelter_type=stype)
        return jsonify({'success': True, 'data': [s.to_dict() for s in q.all()]})
    if current_user.role == 'viewer':
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    data = request.get_json(force=True)
    shelter = Shelter(
        shelter_name=data.get('shelter_name'),
        shelter_type=data.get('shelter_type'),
        ward_id=int_or_none(data, 'ward_id'),
        location=data.get('location'),
        coordinates=parse_coordinates(data),
        boundary_polygon=data.get('boundary_polygon'),
        total_capacity=int_or_none(data, 'total_capacity'),
        male_capacity=int_or_none(data, 'male_capacity'),
        female_capacity=int_or_none(data, 'female_capacity'),
        children_capacity=int_or_none(data, 'children_capacity'),
        water_available=bool_or_false(data, 'water_available'),
        toilet_available=bool_or_false(data, 'toilet_available'),
        electricity_available=bool_or_false(data, 'electricity_available'),
        kitchen_available=bool_or_false(data, 'kitchen_available'),
        medical_support=bool_or_false(data, 'medical_support'),
        accessibility_support=bool_or_false(data, 'accessibility_support'),
        current_occupancy=int_or_none(data, 'current_occupancy') or 0,
        available_space=int_or_none(data, 'available_space'),
        shelter_manager=data.get('shelter_manager'),
        contact_number=data.get('contact_number'),
        evacuation_routes=data.get('evacuation_routes'),
        assembly_points=data.get('assembly_points'),
        linked_risk_zones=data.get('linked_risk_zones'),
        linked_vulnerable_households=data.get('linked_vulnerable_households'),
        created_by=current_user.id,
    )
    db.session.add(shelter)
    db.session.commit()
    log_activity('create', 'Shelter', shelter.id, f"Created shelter: {shelter.shelter_name}")
    return jsonify({'success': True, 'data': shelter.to_dict()})


@new_bp.route('/api/shelters/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_shelter_item(id):
    shelter = Shelter.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'success': True, 'data': shelter.to_dict()})
    if request.method in ('PUT',) and current_user.role not in ('admin', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE' and current_user.role not in ('admin', 'warehouse_manager', 'operator'):
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    if request.method == 'DELETE':
        db.session.delete(shelter)
        db.session.commit()
        log_activity('delete', 'Shelter', id, f"Deleted shelter: {shelter.shelter_name}")
        return jsonify({'success': True, 'message': 'Deleted'})
    data = request.get_json(force=True)
    for field in ['shelter_name', 'shelter_type', 'location', 'boundary_polygon', 'shelter_manager',
                  'contact_number', 'evacuation_routes', 'assembly_points',
                  'linked_risk_zones', 'linked_vulnerable_households']:
        if field in data:
            setattr(shelter, field, data[field])
    if 'ward_id' in data:
        shelter.ward_id = int_or_none(data, 'ward_id')
    if 'total_capacity' in data:
        shelter.total_capacity = int_or_none(data, 'total_capacity')
    if 'male_capacity' in data:
        shelter.male_capacity = int_or_none(data, 'male_capacity')
    if 'female_capacity' in data:
        shelter.female_capacity = int_or_none(data, 'female_capacity')
    if 'children_capacity' in data:
        shelter.children_capacity = int_or_none(data, 'children_capacity')
    if 'current_occupancy' in data:
        shelter.current_occupancy = int_or_none(data, 'current_occupancy')
    if 'available_space' in data:
        shelter.available_space = int_or_none(data, 'available_space')
    if 'coordinates' in data:
        shelter.coordinates = parse_coordinates(data, 'coordinates')
    for field in ['water_available', 'toilet_available', 'electricity_available',
                  'kitchen_available', 'medical_support', 'accessibility_support']:
        if field in data:
            setattr(shelter, field, bool_or_false(data, field))
    db.session.commit()
    log_activity('update', 'Shelter', id, f"Updated shelter: {shelter.shelter_name}")
    return jsonify({'success': True, 'data': shelter.to_dict()})


# ================================================================
# API: GIS MAP DATA (All Layers)
# ================================================================

@new_bp.route('/gis-map')
@login_required
def gis_map_page():
    return render_template('gis_map.html')

@new_bp.route('/api/new-modules/map-data')
@login_required
def api_new_modules_map_data():
    data = {}

    data['infrastructure'] = [{
        'id': i.id, 'name': i.name, 'type': i.infrastructure_type,
        'lat': float(i.coordinates.split(',')[0]) if i.coordinates else None,
        'lng': float(i.coordinates.split(',')[1]) if i.coordinates else None,
        'ward': i.ward.name if i.ward else None,
    } for i in CriticalInfrastructure.query.all() if i.coordinates]

    data['facilities'] = [{
        'id': f.id, 'name': f.facility_name, 'type': f.facility_type,
        'lat': float(f.coordinates.split(',')[0]) if f.coordinates else None,
        'lng': float(f.coordinates.split(',')[1]) if f.coordinates else None,
        'capacity': f.max_capacity, 'occupancy': f.current_occupancy,
        'polygon': f.polygon_boundary,
    } for f in EmergencyFacility.query.all() if f.coordinates]

    data['risk_layers'] = [{
        'id': r.id, 'name': r.name, 'type': r.risk_type, 'level': r.risk_level,
        'lat': float(r.coordinates.split(',')[0]) if r.coordinates else None,
        'lng': float(r.coordinates.split(',')[1]) if r.coordinates else None,
        'polygon': r.polygon_boundary,
        'population': r.population_at_risk,
    } for r in RiskLayer.query.all() if r.coordinates]

    data['contacts'] = [{
        'id': c.id, 'name': c.contact_person, 'designation': c.designation,
        'phone': c.mobile_number,
        'lat': float(c.coordinates.split(',')[0]) if c.coordinates else None,
        'lng': float(c.coordinates.split(',')[1]) if c.coordinates else None,
    } for c in EmergencyContact.query.all() if c.coordinates]

    data['shelters'] = [{
        'id': s.id, 'name': s.shelter_name, 'type': s.shelter_type,
        'lat': float(s.coordinates.split(',')[0]) if s.coordinates else None,
        'lng': float(s.coordinates.split(',')[1]) if s.coordinates else None,
        'capacity': s.total_capacity, 'occupancy': s.current_occupancy,
        'boundary_polygon': json.loads(s.boundary_polygon) if s.boundary_polygon else None,
    } for s in Shelter.query.all() if s.coordinates]

    data['volunteers'] = [{
        'id': v.id, 'name': v.name, 'status': v.availability_status,
        'lat': float(v.home_coordinates.split(',')[0]) if v.home_coordinates else None,
        'lng': float(v.home_coordinates.split(',')[1]) if v.home_coordinates else None,
    } for v in Volunteer.query.all() if v.home_coordinates]

    data['vehicles'] = [{
        'id': v.id, 'number': v.vehicle_number, 'type': v.vehicle_type, 'status': v.status,
        'lat': float(v.current_coordinates.split(',')[0]) if v.current_coordinates else None,
        'lng': float(v.current_coordinates.split(',')[1]) if v.current_coordinates else None,
    } for v in Vehicle.query.all() if v.current_coordinates]

    data['vulnerable'] = [{
        'id': h.id, 'head': h.head_of_household, 'category': h.category,
        'lat': float(h.coordinates.split(',')[0]) if h.coordinates else None,
        'lng': float(h.coordinates.split(',')[1]) if h.coordinates else None,
        'priority': h.evacuation_priority,
    } for h in VulnerableHousehold.query.all() if h.coordinates]

    data['disabled'] = [{
        'id': p.id, 'name': p.person_name,
        'lat': float(p.coordinates.split(',')[0]) if p.coordinates else None,
        'lng': float(p.coordinates.split(',')[1]) if p.coordinates else None,
    } for p in DisabledPerson.query.all() if p.coordinates]

    data['high_risk'] = [{
        'id': p.id, 'name': p.person_name, 'category': p.category,
        'lat': float(p.coordinates.split(',')[0]) if p.coordinates else None,
        'lng': float(p.coordinates.split(',')[1]) if p.coordinates else None,
    } for p in HighRiskPerson.query.all() if p.coordinates]

    data['rrt'] = [{
        'id': t.id, 'name': t.team_name, 'leader': t.team_leader,
        'lat': float(t.base_coordinates.split(',')[0]) if t.base_coordinates else None,
        'lng': float(t.base_coordinates.split(',')[1]) if t.base_coordinates else None,
    } for t in RapidResponseTeam.query.all() if t.base_coordinates]

    return jsonify(data)
