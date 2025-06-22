import os
from datetime import datetime, timedelta
from flask import Blueprint, Flask, json, make_response, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, func, or_
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import re
load_dotenv()

# === Extensions ===
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# === Flask App Config ===
app = Flask(__name__)
from config import config_by_name
env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config_by_name[env])

# CORS Configuration (Frontend on port 3000)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Environment Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False




# === Bind extensions to app ===
db.init_app(app)
ma.init_app(app)
migrate.init_app(app, db)

# === Import models after db is initialized ===
from models import Tenants, Properties, Units, Leases, RentPayments, Expenses, MaintenanceRequests, Users

# === Schemas ===
class GenericSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True

class TenantSchema(GenericSchema):
    class Meta:
        model = Tenants

class PropertySchema(GenericSchema):
    class Meta:
        model = Properties

class UnitSchema(GenericSchema):
    class Meta:
        model = Units

class LeaseSchema(GenericSchema):
    class Meta:
        model = Leases

class RentPaymentSchema(GenericSchema):
    class Meta:
        model = RentPayments

class ExpenseSchema(GenericSchema):
    class Meta:
        model = Expenses

class MaintenanceRequestSchema(GenericSchema):
    class Meta:
        model = MaintenanceRequests

class UserSchema(GenericSchema):
    class Meta:
        model = Users

# === Schema Instances ===
tenant_schema = TenantSchema()
tenants_schema = TenantSchema(many=True)

property_schema = PropertySchema()
properties_schema = PropertySchema(many=True)

unit_schema = UnitSchema()
units_schema = UnitSchema(many=True)

lease_schema = LeaseSchema()
leases_schema = LeaseSchema(many=True)

rent_schema = RentPaymentSchema()
rents_schema = RentPaymentSchema(many=True)

expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)

maint_schema = MaintenanceRequestSchema()
maintenances_schema = MaintenanceRequestSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# === CRUD Routes for each model ===

# ------- TENANTS -------
@app.route('/tenants', methods=['POST'])
def create_tenant():
    """Create a new tenant"""
    tenant = tenant_schema.load(request.json)
    db.session.add(tenant)
    db.session.commit()
    return tenant_schema.jsonify(tenant), 201

@app.route('/tenants', methods=['GET'])
def get_tenants():
    """Get all tenants"""
    return tenants_schema.jsonify(Tenants.query.all())

@app.route('/tenants/<int:id>', methods=['GET'])
def get_tenant(id):
    """Get a single tenant by ID"""
    return tenant_schema.jsonify(Tenants.query.get_or_404(id))

@app.route('/tenants/<int:id>', methods=['PUT'])
def update_tenant(id):
    """Update a tenant by ID"""
    tenant = Tenants.query.get_or_404(id)
    for key, value in request.json.items():
        setattr(tenant, key, value)
    db.session.commit()
    return tenant_schema.jsonify(tenant)

@app.route('/tenants/<int:id>', methods=['DELETE'])
def delete_tenant(id):
    """Delete a tenant"""
    db.session.delete(Tenants.query.get_or_404(id))
    db.session.commit()
    return '', 204

# ------- PROPERTIES -------
@app.route('/properties', methods=['POST'])
def create_property():
    data = request.get_json()
    required_fields = ['address', 'city', 'state', 'zip_code', 'admin_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        new_property = Properties(
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            admin_id=data['admin_id']
        )
        db.session.add(new_property)
        db.session.commit()

        return jsonify({
            'message': 'Property created successfully',
            'property': {
                'id': new_property.id,
                'address': new_property.address,
                'city': new_property.city,
                'state': new_property.state,
                'zip_code': new_property.zip_code
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create property', 'details': str(e)}), 500
@app.route('/properties/admin/<int:admin_id>', methods=['GET'])
def get_properties_by_admin(admin_id):
    properties = Properties.query.filter_by(admin_id=admin_id).all()
    
    if not properties:
        return jsonify({'message': 'No properties found for this admin.'}), 404

    property_list = []
    for prop in properties:
        property_list.append({
            'id': prop.id,
            'address': prop.address,
            'city': prop.city,
            'state': prop.state,
            'zip_code': prop.zip_code
        })

    return jsonify(property_list), 200

@app.route('/properties', methods=['GET'])
def get_properties():
    return properties_schema.jsonify(Properties.query.all())

# Property routes (assuming you're using Flask)

# Update Property
@app.route('/properties/<int:property_id>', methods=['PATCH'])
def update_property(property_id):
    data = request.get_json()
    property = Properties.query.get(property_id)
    
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    # Update only allowed fields
    allowed_fields = ['address', 'city', 'state', 'zip_code']
    for key, value in data.items():
        if key in allowed_fields and hasattr(property, key):
            setattr(property, key, value)
    
    db.session.commit()
    return jsonify({
        'id': property.id,
        'address': property.address,
        'city': property.city,
        'state': property.state,
        'zip_code': property.zip_code,
        'admin_id': property.admin_id
    }), 200

# Delete Property
@app.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    try:
        # Start a transaction
        db.session.begin_nested()
        
        property = Properties.query.get(property_id)
        if not property:
            return jsonify({'error': 'Property not found'}), 404

        # Get all units in this property
        units = Units.query.filter_by(property_id=property_id).all()
        
        for unit in units:
            # Handle all leases for this unit
            leases = Leases.query.filter_by(unit_id=unit.unit_id).all()
            
            for lease in leases:
                # Option 1: Delete associated rent payments
                RentPayments.query.filter_by(lease_id=lease.lease_id).delete()
                
                # Option 2: Orphan the payments (if you want to keep payment records)
                # RentPayments.query.filter_by(lease_id=lease.lease_id).update(
                #     {'lease_id': None}, synchronize_session=False
                # )
                
                # Delete the lease
                db.session.delete(lease)
            
            # Delete the unit
            db.session.delete(unit)
        
        # Finally delete the property
        db.session.delete(property)
        db.session.commit()
        
        return jsonify({
            'message': 'Property deleted successfully with all associated units, leases, and payments'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to delete property: {str(e)}',
            'solution': 'Ensure all related records are properly handled before deletion'
        }), 500
# ------- UNITS -------
# app.py or routes.py

@app.route('/units', methods=['POST'])
def create_unit():
    data = request.get_json()
    print(data)
    required_fields = ['property_id', 'unit_number', 'unit_name', 'status', 'monthly_rent', 'deposit_amount', 'admin_id', 'type']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        new_unit = Units(
            property_id=data['property_id'],
            unit_number=data['unit_number'],
            unit_name=data['unit_name'],
            status=data['status'],
            monthly_rent=data['monthly_rent'],
            deposit_amount=data['deposit_amount'],
            admin_id=data['admin_id'],
            type=data['type']
        )
        db.session.add(new_unit)
        db.session.commit()

        return jsonify({
            'message': 'Unit created successfully',
            'unit': {
                'unit_id': new_unit.unit_id,
                'unit_number': new_unit.unit_number,
                'unit_name': new_unit.unit_name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/units/property/<int:property_id>', methods=['GET'])
def get_units_by_property(property_id):
    units = Units.query.filter_by(property_id=property_id).all()
    return jsonify([
        {
            'unit_id': u.unit_id,
            'unit_name': u.unit_name,
            'unit_number': u.unit_number,
            'status': u.status,
            'type': u.type,
            'monthly_rent': u.monthly_rent,
            'deposit_amount': u.deposit_amount
        }
        for u in units
    ]), 200

# Unit routes (assuming you're using Flask)
@app.route('/units/<int:unit_id>', methods=['GET'])
def get_unit(unit_id):
    try:
        unit = Units.query.get_or_404(unit_id)
        current_lease = Leases.query.filter_by(unit_id=unit_id, lease_status='active').first()
        tenant = Tenants.query.get(current_lease.tenant_id) if current_lease else None

        payments = []
        if current_lease:
            payments = RentPayments.query.filter_by(lease_id=current_lease.lease_id)\
                .order_by(RentPayments.period_start.desc()).all()

        return jsonify({
            'unit': unit.to_dict(),
            'current_tenant': tenant.to_dict() if tenant else None,
            'current_lease': current_lease.to_dict() if current_lease else None,
            'payment_history': [p.to_dict() for p in payments]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/units/<int:unit_id>/assign-tenant', methods=['POST'])
def assign_tenant(unit_id):
    try:
        data = request.get_json()
        unit = Units.query.get_or_404(unit_id)

        # Validate required fields
        if not data.get('tenant_id') and not all(field in data for field in [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'emergency_contact_name', 'emergency_contact_number', 'move_in_date'
        ]):
            return jsonify({'error': 'Either tenant_id or complete tenant details required'}), 400

        # Handle tenant creation/lookup
        if data.get('tenant_id'):
            tenant = Tenants.query.get(data['tenant_id'])
            if not tenant:
                return jsonify({'error': 'Tenant not found'}), 404
            
            # Verify the tenant has a corresponding user
            user = Users.query.filter_by(email=tenant.email).first()
            if not user:
                # Create user if doesn't exist
                user = Users(
                    username=tenant.email,
                    email=tenant.email,
                    password=tenant.password,  # Should be hashed already
                    role='tenant',
                    is_active=True
                )
                db.session.add(user)
        else:
            # Validate email doesn't exist in either table
            if Tenants.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists in tenants table'}), 400
            if Users.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists in users table'}), 400

            try:
                # Create password and hash it
                default_password = f"{data['first_name'].lower().replace(' ', '')}@123"
                hashed_password = generate_password_hash(default_password)
                
                # Create tenant
                tenant = Tenants(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    phone=data['phone'],
                    date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
                    emergency_contact_name=data['emergency_contact_name'],
                    emergency_contact_number=data['emergency_contact_number'],
                    move_in_date=datetime.strptime(data['move_in_date'], '%Y-%m-%d').date(),
                    admin_id=data['admin_id'],
                    password=hashed_password
                )
                db.session.add(tenant)
                db.session.flush()  # Get the tenant ID before commit
                
                # Create corresponding user account (without tenant_id)
                user = Users(
                    username=data['email'],  # Using email as username
                    email=data['email'],
                    password=hashed_password,
                    role='tenant',
                    is_active=True
                )
                db.session.add(user)
                
            except ValueError as e:
                return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
            except KeyError as e:
                return jsonify({'error': f'Missing required field: {str(e)}'}), 400

        # Validate lease dates
        lease_start = datetime.strptime(data['lease_start'], '%Y-%m-%d').date()
        lease_end = datetime.strptime(data['lease_end'], '%Y-%m-%d').date()

        if lease_end <= lease_start:
            return jsonify({'error': 'Lease end date must be after start date'}), 400

        if not (1 <= int(data.get('payment_due_day', 1)) <= 28):
            return jsonify({'error': 'Payment due day must be between 1 and 28'}), 400
        
        # Create lease
        lease = Leases(
            tenant_id=tenant.id,
            unit_id=unit_id,
            start_date=lease_start,
            end_date=lease_end,
            monthly_rent=unit.monthly_rent,
            deposit_amount=unit.deposit_amount,
            lease_status='active',
            property_id=unit.property_id,
            admin_id=data['admin_id'],
            payment_due_day=int(data.get('payment_due_day', 1))
        )
        db.session.add(lease)
        unit.status = 'occupied'
        
        db.session.commit()

        return jsonify({
            'message': 'Tenant assigned successfully',
            'tenant': tenant.to_dict(),
            'user': user.to_dict(),
            'lease': lease.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/units/<int:unit_id>/record-payment', methods=['POST'])
def record_payment(unit_id):
    try:
        data = request.get_json()
        lease = Leases.query.filter_by(unit_id=unit_id, lease_status='active').first_or_404()

        # Record payment
        payment = RentPayments(
            lease_id=lease.lease_id,
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d'),
            amount=data['amount'],
            payment_method=data['payment_method'],
            transaction_reference_number=data.get('transaction_reference', ''),
            period_start=datetime.strptime(data['period_start'], '%Y-%m-%d'),
            period_end=datetime.strptime(data['period_end'], '%Y-%m-%d'),
            status='completed',
            tenant_id=lease.tenant_id,
            admin_id=data['admin_id']
        )
        db.session.add(payment)
        db.session.commit()

        # Rent analysis
        payments = RentPayments.query.filter_by(lease_id=lease.lease_id).all()
        total_paid = sum(p.amount for p in payments)

        lease_start = lease.start_date
        today = datetime.today()
        months_elapsed = (today.year - lease_start.year) * 12 + today.month - lease_start.month + 1
        expected_total = months_elapsed * lease.monthly_rent
        balance = expected_total - total_paid
        months_paid = total_paid // lease.monthly_rent
        months_behind = months_elapsed - months_paid

        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': payment.to_dict(),
            'payment_status': {
                'total_months': months_elapsed,
                'expected_total_rent': expected_total,
                'total_paid': total_paid,
                'balance_due': balance,
                'months_behind': months_behind
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/units/<int:unit_id>/end-lease', methods=['POST'])
def end_lease(unit_id):
    try:
        data = request.get_json()
        lease = Leases.query.filter_by(unit_id=unit_id, lease_status='active').first_or_404()

        lease.lease_status = 'ended'
        lease.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

        unit = Units.query.get(unit_id)
        unit.status = 'vacant'

        db.session.commit()

        return jsonify({
            'message': 'Lease ended successfully',
            'unit': unit.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update Unit
@app.route('/units/<int:unit_id>', methods=['PATCH'])
def update_unit(unit_id):
    data = request.get_json()
    unit = Units.query.get(unit_id)
    
    if not unit:
        return jsonify({'error': 'Unit not found'}), 404
    
    # Update fields
    for key, value in data.items():
        if hasattr(unit, key):
            setattr(unit, key, value)
    
    db.session.commit()
    return jsonify(unit.to_dict()), 200

# Delete Unit
@app.route('/units/<int:unit_id>', methods=['DELETE'])
def delete_unit(unit_id):
    unit = Units.query.get(unit_id)
    
    if not unit:
        return jsonify({'error': 'Unit not found'}), 404
    
    db.session.delete(unit)
    db.session.commit()
    return jsonify({'message': 'Unit deleted successfully'}), 200

# ------- LEASES -------
@app.route('/leases', methods=['POST'])
def create_lease():
    lease = lease_schema.load(request.json)
    db.session.add(lease)
    db.session.commit()
    return lease_schema.jsonify(lease), 201

@app.route('/leases', methods=['GET'])
def get_leases():
    return leases_schema.jsonify(Leases.query.all())

@app.route('/leases/<int:id>', methods=['PUT'])
def update_lease(id):
    lease = Leases.query.get_or_404(id)
    for k, v in request.json.items():
        setattr(lease, k, v)
    db.session.commit()
    return lease_schema.jsonify(lease)

@app.route('/leases/<int:id>', methods=['DELETE'])
def delete_lease(id):
    db.session.delete(Leases.query.get_or_404(id))
    db.session.commit()
    return '', 204

# ------- RENT PAYMENTS -------
@app.route('/rent_payments', methods=['POST'])
def create_rent():
    rent = rent_schema.load(request.json)
    db.session.add(rent)
    db.session.commit()
    return rent_schema.jsonify(rent), 201

from flask import request, jsonify
from sqlalchemy import or_, and_
from datetime import datetime

@app.route('/admin/rent-payments/<int:admin_id>', methods=['GET'])
def get_rent_payments(admin_id):
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        tenant_name = request.args.get('tenant_name', '').strip()
        unit_name = request.args.get('unit_name', '').strip()
        property_name = request.args.get('property_name', '').strip()
        reference_number = request.args.get('reference_number', '').strip()
        status = request.args.get('status', '').strip()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query
        query = db.session.query(
            RentPayments,
            Tenants,
            Units,
            Properties
        ).join(
            Tenants, Tenants.id == RentPayments.tenant_id
        ).join(
            Leases, Leases.lease_id == RentPayments.lease_id
        ).join(
            Units, Units.unit_id == Leases.unit_id
        ).join(
            Properties, Properties.id == Units.property_id
        ).filter(
            RentPayments.admin_id == admin_id
        )
        
        # Apply filters
        if search:
            query = query.filter(or_(
                Tenants.first_name.ilike(f'%{search}%'),
                Tenants.last_name.ilike(f'%{search}%'),
                Units.unit_name.ilike(f'%{search}%'),
                Properties.address.ilike(f'%{search}%'),
                RentPayments.transaction_reference_number.ilike(f'%{search}%')
            ))
        
        if tenant_name:
            query = query.filter(or_(
                Tenants.first_name.ilike(f'%{tenant_name}%'),
                Tenants.last_name.ilike(f'%{tenant_name}%')
            ))
            
        if unit_name:
            query = query.filter(Units.unit_name.ilike(f'%{unit_name}%'))
            
        if property_name:
            query = query.filter(Properties.address.ilike(f'%{property_name}%'))
            
        if reference_number:
            query = query.filter(
                RentPayments.transaction_reference_number.ilike(f'%{reference_number}%')
            )
            
        if status:
            query = query.filter(RentPayments.status == status)
            
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(and_(
                    RentPayments.payment_date >= start,
                    RentPayments.payment_date <= end
                ))
            except ValueError:
                pass
                
        # Execute query
        results = query.order_by(RentPayments.payment_date.desc()).all()
        
        # Format response
        payments = []
        for payment, tenant, unit, property in results:
            payments.append({
                'id': payment.payment_id,
                'tenant_name': f"{tenant.first_name} {tenant.last_name}",
                'tenant_id': tenant.id,
                'unit_name': unit.unit_name,
                'unit_id': unit.unit_id,
                'property_name': property.address,
                'property_id': property.id,
                'amount': payment.amount,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'payment_method': payment.payment_method,
                'reference_number': payment.transaction_reference_number,
                'period_start': payment.period_start.strftime('%Y-%m-%d'),
                'period_end': payment.period_end.strftime('%Y-%m-%d'),
                'status': payment.status,
                'lease_id': payment.lease_id
            })
            
        return jsonify({
            'success': True,
            'payments': payments,
            'count': len(payments)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@app.route('/admin/rent-payments/<int:admin_id>/stats', methods=['GET'])
def get_rent_stats(admin_id):
    try:
        # Get current month's start and end dates
        today = datetime.today()
        first_day = today.replace(day=1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Query for total expected rent (sum of all active leases)
        expected_rent = db.session.query(
            func.sum(Leases.monthly_rent)
        ).filter(
            Leases.admin_id == admin_id,
            Leases.start_date <= last_day,
            or_(
                Leases.end_date >= first_day,
                Leases.end_date == None  # Ongoing leases
            )
        ).scalar() or 0
        
        # Query for collected rent in current month
        collected_rent = db.session.query(
            func.sum(RentPayments.amount)
        ).filter(
            RentPayments.admin_id == admin_id,
            RentPayments.payment_date >= first_day,
            RentPayments.payment_date <= today,
            RentPayments.status == 'paid'
        ).scalar() or 0
        
        # Calculate percentage (avoid division by zero)
        percentage = 0
        if expected_rent > 0:
            percentage = round((collected_rent / expected_rent) * 100)
        
        return jsonify({
            'success': True,
            'collected': float(collected_rent),
            'expected': float(expected_rent),
            'percentage': percentage
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# ------- EXPENSES -------
@app.route('/expenses', methods=['POST'])
def create_expense():
    expense = expense_schema.load(request.json)
    db.session.add(expense)
    db.session.commit()
    return expense_schema.jsonify(expense), 201

@app.route('/expenses', methods=['GET'])
def get_expenses():
    return expenses_schema.jsonify(Expenses.query.all())

# ------- MAINTENANCE REQUESTS -------
@app.route('/maintenance_requests', methods=['POST'])
def create_maintenance():
    req = maint_schema.load(request.json)
    db.session.add(req)
    db.session.commit()
    return maint_schema.jsonify(req), 201

@app.route('/maintenance_requests', methods=['GET'])
def get_maintenance():
    return maintenances_schema.jsonify(MaintenanceRequests.query.all())

# ------- USERS -------
@app.route('/users', methods=['POST'])
def create_user():
    user = user_schema.load(request.json)
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 201

@app.route('/users', methods=['GET'])
def get_users():
    return users_schema.jsonify(Users.query.all())

from flask import request, jsonify, session
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, Users, Tenants, Admin

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    required_fields = ['username', 'password', 'role', 'email', 'is_active']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if user already exists
    existing_user = Users.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(data['password'])

    # Create user
    new_user = Users(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        role=data['role'],
        last_login=None,
        is_active=data['is_active']
    )
    db.session.add(new_user)
    db.session.commit()

    # Insert into related table based on role
    if new_user.role == 'tenant':
        new_tenant = Tenants(
            first_name=new_user.username,
            last_name='',
            email=new_user.email,
            phone='',
            date_of_birth=datetime.utcnow().date(),
            emergency_contact_name='',
            emergency_contact_number='',
            move_in_date=datetime.utcnow().date(),
            move_out_date=None,
            admin_id=1  # Optional: You might assign a default admin
        )
        db.session.add(new_tenant)

    elif new_user.role == 'admin':
        new_admin = Admin(
            username=new_user.username,
            password=hashed_password,
            gmail=new_user.email
        )
        db.session.add(new_admin)

    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': {
            'user_id': new_user.user_id,
            'username': new_user.username,
            'email': new_user.email,
            'role': new_user.role,
            'is_active': new_user.is_active
        }
    }), 201



# -------------------- LOGIN --------------------
@app.route('/login', methods=['POST'])
def login():
    print("Received login request")  # Debug log
    print("Request headers:", request.headers)  # Debug log
    print("Request data:", request.data)  # Debug log
    
    try:
        data = request.get_json()
        print("Parsed JSON data:", data)  # Debug log
        
        if not data:
            print("Error: No data received")  # Debug log
            return jsonify({'error': 'No data received'}), 400
            
        if 'email' not in data or 'password' not in data:
            print("Error: Missing email or password")  # Debug log
            return jsonify({'error': 'Email and password are required'}), 400
            
        print(f"Looking for user with email: {data['email']}")  # Debug log
        user = Users.query.filter_by(email=data['email']).first()
        
        if not user:
            print("Error: User not found")  # Debug log
            return jsonify({'error': 'Invalid email or password'}), 401
            
        print("User found, checking password")  # Debug log
        if not check_password_hash(user.password, data['password']):
            print("Error: Password mismatch")  # Debug log
            return jsonify({'error': 'Invalid email or password'}), 401
            
        print("Login successful")  # Debug log

        user.last_login = datetime.utcnow()
        db.session.commit()

        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }

        # Create response
        response_data = {
            'message': 'Login successful',
            'user': user_data  # This matches the frontend expectation
        }

        response = make_response(jsonify(response_data))

        # Set HttpOnly cookie (secure in production)
        response.set_cookie(
            'user',
            value=json.dumps(user_data),  # Store just the user_data in cookie
            httponly=True,
            secure=app.config.get('ENV') == 'production',
            samesite='Strict',
            max_age=604800  # 7 days
        )

        return response

    except Exception as e:
        print("Error in login endpoint:", str(e))  # Debug log
        return jsonify({'error': 'Internal server error'}), 500

# -------------------- LOGOUT --------------------
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    response = jsonify({'message': 'Logged out'})
    response.set_cookie('user_id', '', expires=0)
    return response


# -------------------- FORGOT PASSWORD --------------------
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # NOTE: In production, send a password reset token via email here.
    return jsonify({'message': 'Recovery instructions sent to email'}), 200


# -------------------- RECOVER PASSWORD --------------------
@app.route('/recover-password', methods=['POST'])
def recover_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({'error': 'Email and new password are required'}), 400

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200
@app.route('/admin/stats/<int:admin_id>', methods=['GET'])
def get_admin_stats(admin_id):
    try:
        # Validate admin exists
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404

        # Count properties
        property_count = db.session.query(func.count(Properties.id))\
            .filter(Properties.admin_id == admin_id)\
            .scalar() or 0
        
        # Count all units
        total_units = db.session.query(func.count(Units.unit_id))\
            .join(Properties)\
            .filter(Properties.admin_id == admin_id)\
            .scalar() or 0
        
        # Count occupied units
        occupied_units = db.session.query(func.count(Units.unit_id))\
            .join(Properties)\
            .filter(
                Properties.admin_id == admin_id,
                Units.status == 'occupied'
            )\
            .scalar() or 0
        
        # Calculate potential revenue
        potential_revenue = db.session.query(func.sum(Units.monthly_rent))\
            .join(Properties)\
            .filter(Properties.admin_id == admin_id)\
            .scalar() or 0
        
        # Count active tenants
        active_tenants = db.session.query(func.count(Tenants.id))\
            .join(Leases, Leases.tenant_id == Tenants.id)\
            .filter(
                Tenants.admin_id == admin_id,
                Leases.lease_status == 'active'
            )\
            .scalar() or 0
        
        # Calculate collected rent (current month)
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        collected_rent = db.session.query(func.sum(RentPayments.amount))\
            .filter(
                RentPayments.admin_id == admin_id,
                RentPayments.status == 'paid',
                extract('month', RentPayments.payment_date) == current_month,
                extract('year', RentPayments.payment_date) == current_year
            )\
            .scalar() or 0
        
        # Calculate outstanding payments
        outstanding_query = db.session.query(
            func.sum(Leases.monthly_rent - func.coalesce(
                db.session.query(func.sum(RentPayments.amount))
                .filter(
                    RentPayments.lease_id == Leases.lease_id,
                    extract('month', RentPayments.payment_date) == current_month,
                    extract('year', RentPayments.payment_date) == current_year
                )
                .scalar(), 0)
            ))\
            .filter(
                Leases.admin_id == admin_id,
                Leases.lease_status == 'active'
            )\
            .scalar()
        
        outstanding = outstanding_query or 0

        # Recent activity (last 5 maintenance requests)
        recent_activity = MaintenanceRequests.query\
            .filter(MaintenanceRequests.admin_id == admin_id)\
            .order_by(MaintenanceRequests.request_date.desc())\
            .limit(5)\
            .all()
        
        # Upcoming payments (next 7 days)
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        upcoming_payments = db.session.query(Leases, Tenants)\
            .join(Tenants, Tenants.id == Leases.tenant_id)\
            .filter(
                Leases.admin_id == admin_id,
                Leases.lease_status == 'active',
                Leases.payment_due_day.between(today.day, next_week.day)
            )\
            .all()
        
        # Format responses
        formatted_activity = [{
            'text': f"Maintenance for {req.lease.unit.unit_name}",
            'description': req.request_description,
            'time': req.request_date.strftime('%b %d, %Y'),
            'status': req.request_status
        } for req in recent_activity] if recent_activity else []
        
        formatted_payments = [{
            'id': lease.lease_id,
            'name': f"{tenant.first_name} {tenant.last_name}",
            'unit': lease.unit.unit_name,
            'amount': lease.monthly_rent,
            'status': 'due',
            'due_date': f"{today.year}-{today.month}-{lease.payment_due_day}"
        } for lease, tenant in upcoming_payments] if upcoming_payments else []

        return jsonify({
            'success': True,
            'data': {
                'property_count': property_count,
                'total_units': total_units,
                'occupied_units': occupied_units,
                'active_tenants': active_tenants,
                'potential_revenue': potential_revenue,
                'collected_rent': collected_rent,
                'outstanding': outstanding,
                'occupancy_rate': round((occupied_units / total_units * 100) if total_units > 0 else 0),
                'recent_activity': formatted_activity,
                'upcoming_payments': formatted_payments
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch dashboard data'
        }), 500
# === Run the app ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
