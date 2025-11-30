from email.utils import parsedate
import os
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from flask import Blueprint, Flask, json, make_response, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, func, or_
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from json import JSONDecodeError
import re
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
load_dotenv()

# === Import config first (before using db) ===
from config import db, ma, migrate, app

# CORS Configuration (Frontend on port 3000)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Environment Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# === Email Configuration ===
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

def send_reset_email(user_email, reset_token):
    """Send password reset email with secure token"""
    try:
        subject = "Password Reset Request"
        reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Password Reset Request</h2>
                <p>You requested a password reset for your account.</p>
                <p><strong>This link expires in 30 minutes.</strong></p>
                <p>
                    <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Reset Password
                    </a>
                </p>
                <p>Or copy this link: <a href="{reset_url}">{reset_url}</a></p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    If you didn't request this, please ignore this email. Your account remains secure.
                </p>
            </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = user_email
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f" Email send failed: {str(e)}")
        return False




# Extensions already initialized in config.py

# === Import models after db is initialized ===
from models import Tenants, Properties, Units, Leases, RentPayments, Expenses, MaintenanceRequests, Users, PasswordResetToken

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
from urllib.parse import unquote
import json
@app.route('/tenant-dashboard', methods=['GET'])
def tenant_dashboard():
    try:
        # Get user data from cookie
        user_cookie = request.cookies.get('user')
        if not user_cookie:
            return jsonify({'error': 'Not authenticated'}), 401
        
        print("✅ Cookie found:", user_cookie)
        
        # URL-decode the cookie first, then parse as JSON
        decoded_cookie = unquote(user_cookie)
        print("🔓 Decoded cookie:", decoded_cookie)
        
        user_data = json.loads(decoded_cookie)
        user_id = user_data.get('user_id')
        user_role = user_data.get('role')
        
        print(f"Dashboard request - User ID: {user_id}, Role: {user_role}")
        if user_role != 'tenant':
            return jsonify({'error': 'Access denied'}), 403
        
        # Find the user
        user = Users.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        print(f"🔍 Found user: {user.username}, email: {user.email}")
            
        # Find the tenant by email
        tenant = Tenants.query.filter_by(email=user.email).first()
        
        if not tenant:
            print("❌ No tenant record found for this user")
            # Create a tenant record if it doesn't exist
            new_tenant = Tenants(
                first_name=user.username.split('@')[0],  # Use part of email as first name
                last_name='User',
                email=user.email,
                phone='Not provided',
                date_of_birth=datetime.utcnow().date(),
                emergency_contact_name='Not provided',
                emergency_contact_number='Not provided',
                password='default_password',  # You might want to handle this differently
                admin_id=1  # Default admin
            )
            db.session.add(new_tenant)
            db.session.commit()
            tenant = new_tenant
            print(f"✅ Created new tenant record with ID: {tenant.id}")
        else:
            print(f"✅ Found tenant with ID: {tenant.id}")  # Changed from tenant_id to id
            
        # 3. Get lease - FIXED: use tenant.id instead of tenant.tenant_id
        lease = Leases.query.filter_by(tenant_id=tenant.id, lease_status='active').first()
        if lease:
            print(f"📄 Active lease found: ID={lease.lease_id}, property_id={lease.property_id}, unit_id={lease.unit_id}")
        else:
            print("ℹ️ No active lease found")

        # 4. Get unit
        unit = Units.query.get(lease.unit_id) if lease else None
        if unit:
            print(f"🏠 Unit: {unit.unit_name} ({unit.type}) - #{unit.unit_number}")
        else:
            print("⚠️ Unit not found or no lease")

        # 5. Get property
        property = Properties.query.get(lease.property_id) if lease else None
        if property:
            print(f"🏢 Property: {property.property_name}, {property.address}")
        else:
            print("⚠️ Property not found or no lease")

        # 6. Get recent payments - FIXED: use tenant.id instead of tenant.tenant_id
        payments = RentPayments.query.filter_by(tenant_id=tenant.id)\
            .order_by(RentPayments.payment_date.desc()).limit(5).all()
        print(f"💰 Retrieved {len(payments)} recent payment(s)")

        # 7. Check current month payment - FIXED: use tenant.id instead of tenant.tenant_id
        today = datetime.now().date()
        first_of_month = today.replace(day=1)
        first_next_month = (first_of_month + timedelta(days=32)).replace(day=1)

        current_month_paid = RentPayments.query.filter(
            RentPayments.tenant_id == tenant.id,  # FIXED: use tenant.id
            func.lower(RentPayments.status).in_(['paid', 'completed']),
            RentPayments.period_start <= first_next_month,
            RentPayments.period_end >= first_of_month
        ).first() is not None

        print(f"📆 Current month rent paid: {current_month_paid}")

        
            # 8. Calculate next payment date
        next_payment_date = None
        if lease and lease.payment_due_day:
            try:
                next_payment_date = today.replace(day=lease.payment_due_day)
                if next_payment_date < today:
                    next_payment_date = (next_payment_date + timedelta(days=32)).replace(day=lease.payment_due_day)
                print(f"📅 Next payment due on: {next_payment_date}")
            except ValueError:
                print("⚠️ Invalid payment_due_day in lease")

        # NEW: Calculate EXACT payment position (ahead or behind)
        payment_position = 0.0  # Positive = ahead, Negative = behind
        payment_details = []
        months_ahead = 0
        months_behind = 0
        
        if lease:
            monthly_rent = lease.monthly_rent
            lease_start = lease.start_date
            
            # Get ALL payments for this tenant to calculate exact amounts
            all_payments = RentPayments.query.filter_by(tenant_id=tenant.id).all()
            
            # Calculate total paid amount
            total_paid = sum(p.amount for p in all_payments if p.status.lower() in ['paid', 'completed'])
            
            # Calculate expected payments up to current date
            current_date = today
            expected_periods = []
            period_date = lease_start.replace(day=1)
            
            while period_date <= current_date:
                if period_date >= lease_start:  # Only count periods after lease start
                    expected_periods.append(period_date)
                # Move to next month
                period_date = (period_date + timedelta(days=32)).replace(day=1)
            
            # Calculate expected amount up to current date
            expected_amount = len(expected_periods) * monthly_rent
            
            # Calculate payment position (positive = ahead, negative = behind)
            payment_position = total_paid - expected_amount
            
            # Calculate months ahead/behind based on payment position
            if payment_position > 0:
                months_ahead = payment_position / monthly_rent
            elif payment_position < 0:
                months_behind = abs(payment_position) / monthly_rent
            
            print(f"💰 Total paid: {total_paid}")
            print(f"💰 Expected amount: {expected_amount}")
            print(f"💰 Exact payment position: {payment_position}")
            print(f"💰 Months ahead: {months_ahead}, Months behind: {months_behind}")

            # Build payment details for display
            period_date = lease_start.replace(day=1)
            display_end_date = current_date + timedelta(days=90)  # Show 3 months ahead
            
            while period_date <= display_end_date:
                if period_date >= lease_start:
                    period_end = (period_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    
                    # Check if this specific period is paid
                    period_paid = any(
                        p for p in all_payments 
                        if p.status.lower() in ['paid', 'completed']
                        and p.period_start <= period_end
                        and p.period_end >= period_date
                    )
                    
                    status = 'unpaid'
                    if period_paid:
                        status = 'paid'
                    elif period_date > current_date.replace(day=1):
                        status = 'upcoming'
                    elif period_date <= current_date.replace(day=1):
                        status = 'due'
                    
                    payment_details.append({
                        'period': period_date.strftime('%B %Y'),
                        'amount': monthly_rent,
                        'due_date': period_date.replace(day=lease.payment_due_day).strftime('%Y-%m-%d'),
                        'status': status
                    })
                
                # Move to next month
                period_date = (period_date + timedelta(days=32)).replace(day=1)

        # 9. Build response
        response = {
            'tenant': {
                'first_name': tenant.first_name,
                'last_name': tenant.last_name,
                'email': tenant.email,
                'phone': tenant.phone,
                'emergency_contact_name': tenant.emergency_contact_name,
                'emergency_contact_number': tenant.emergency_contact_number
            },
            'unit': {
                'unit_name': unit.unit_name if unit else None,
                'type': unit.type if unit else None,
                'unit_number': unit.unit_number if unit else None,
                'monthly_rent': unit.monthly_rent if unit else None
            } if unit else None,
            'property': {
                'property_name': property.property_name if property else None,
                'address': f"{property.address}, {property.city}, {property.state} {property.zip_code}" if property else None
            } if property else None,
            'lease': {
                'start_date': lease.start_date.strftime('%Y-%m-%d') if lease else None,
                'end_date': lease.end_date.strftime('%Y-%m-%d') if lease else None,
                'monthly_rent': lease.monthly_rent if lease else None,
                'deposit_amount': lease.deposit_amount if lease else None,
                'payment_due_day': lease.payment_due_day if lease else None,
                'lease_status': lease.lease_status if lease else 'inactive'
            } if lease else None,
            'payments': [{
                'payment_id': p.payment_id,
                'payment_date': p.payment_date.strftime('%Y-%m-%d'),
                'amount': p.amount,
                'payment_method': p.payment_method,
                'status': p.status,
                'period_start': p.period_start.strftime('%Y-%m-%d'),
                'period_end': p.period_end.strftime('%Y-%m-%d')
            } for p in payments],
            'payment_status': {
                'current_month_paid': current_month_paid,
                'next_payment_date': next_payment_date.strftime('%Y-%m-%d') if next_payment_date else None,
                'last_payment_date': payments[0].payment_date.strftime('%Y-%m-%d') if payments else None,
                'payment_position': float(payment_position),  # Ensure it's a float
                'months_ahead': float(months_ahead),  # Can be fractional
                'months_behind': float(months_behind),  # Can be fractional
                'payment_details': payment_details
            }
        }

        print("✅ Dashboard response ready")
        return jsonify(response), 200

    except Exception as e:
        print("💥 Error in /tenant-dashboard:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/tenant-leases', methods=['GET'])
def tenant_leases():
    try:
        import urllib.parse

        print("🔍 Incoming request to /tenant-leases")

        # 1. Check session cookie
        session_cookie = request.cookies.get('user')
        if not session_cookie:
            print("❌ No session cookie found")
            return jsonify({'error': 'Authentication required'}), 401

        decoded_cookie = urllib.parse.unquote(session_cookie)
        session_data = json.loads(decoded_cookie)

        email = session_data.get('email')
        role = session_data.get('role')

        if not email or role != 'tenant':
            print("🚫 Unauthorized access")
            return jsonify({'error': 'Unauthorized access'}), 403

        # 2. Get tenant
        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            print("❌ Tenant not found")
            return jsonify({'error': 'Tenant not found'}), 404

        print(f"👤 Tenant: {tenant.first_name} {tenant.last_name} (ID={tenant.id})")

        # 3. Get all leases for tenant
        leases = Leases.query.filter_by(tenant_id=tenant.id).order_by(Leases.start_date.desc()).all()
        print(f"📄 Found {len(leases)} lease(s)")

        # 4. Build response
        lease_data = []
        for lease in leases:
            unit = Units.query.get(lease.unit_id)
            property = Properties.query.get(lease.property_id)

            lease_data.append({
                'lease_id': lease.lease_id,
                'start_date': lease.start_date.strftime('%Y-%m-%d'),
                'end_date': lease.end_date.strftime('%Y-%m-%d'),
                'monthly_rent': lease.monthly_rent,
                'deposit_amount': lease.deposit_amount,
                'lease_status': lease.lease_status,
                'unit': {
                    'unit_name': unit.unit_name if unit else None,
                    'type': unit.type if unit else None,
                    'unit_number': unit.unit_number if unit else None,
                } if unit else None,
                'property': {
                    'property_name': property.property_name if property else None,
                    'address': f"{property.address}, {property.city}, {property.state} {property.zip_code}" if property else None
                } if property else None,
            })

        print("✅ Lease history response ready")
        return jsonify({'leases': lease_data}), 200

    except Exception as e:
        print("💥 Error in /tenant-leases:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/tenant-payments', methods=['GET'])
def tenant_payment_history():
    try:
        import urllib.parse

        session_cookie = request.cookies.get('user')
        if not session_cookie:
            return jsonify({'error': 'Authentication required'}), 401

        decoded_cookie = urllib.parse.unquote(session_cookie)
        session_data = json.loads(decoded_cookie)
        email = session_data.get('email')
        role = session_data.get('role')

        if not email or role != 'tenant':
            return jsonify({'error': 'Unauthorized access'}), 403

        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        payments = RentPayments.query.filter_by(tenant_id=tenant.id)\
            .order_by(RentPayments.payment_date.desc()).all()

        payment_list = [{
            'payment_id': p.payment_id,
            'payment_date': p.payment_date.strftime('%Y-%m-%d'),
            'amount': p.amount,
            'payment_method': p.payment_method,
            'status': p.status,
            'period_start': p.period_start.strftime('%Y-%m-%d'),
            'period_end': p.period_end.strftime('%Y-%m-%d')
        } for p in payments]

        return jsonify({'payments': payment_list}), 200

    except Exception as e:
        print("💥 Error in /tenant-payments:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/tenant-profile', methods=['GET'])
def get_tenant_profile():
    try:
        import urllib.parse
        session_cookie = request.cookies.get('user')
        if not session_cookie:
            return jsonify({'error': 'Authentication required'}), 401

        decoded_cookie = urllib.parse.unquote(session_cookie)
        session_data = json.loads(decoded_cookie)
        email = session_data.get('email')
        role = session_data.get('role')

        if not email or role != 'tenant':
            return jsonify({'error': 'Unauthorized'}), 403

        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        profile = {
            'first_name': tenant.first_name,
            'last_name': tenant.last_name,
            'email': tenant.email,
            'phone': tenant.phone,
            'emergency_contact_name': tenant.emergency_contact_name,
            'emergency_contact_number': tenant.emergency_contact_number,
        }

        return jsonify(profile), 200

    except Exception as e:
        print("Error in get_tenant_profile:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/tenant-profile/update', methods=['PUT'])
def update_tenant_profile():
    try:
        import urllib.parse
        session_cookie = request.cookies.get('user')
        if not session_cookie:
            return jsonify({'error': 'Authentication required'}), 401

        decoded_cookie = urllib.parse.unquote(session_cookie)
        session_data = json.loads(decoded_cookie)
        email = session_data.get('email')
        role = session_data.get('role')

        if not email or role != 'tenant':
            return jsonify({'error': 'Unauthorized'}), 403

        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        data = request.get_json()
        tenant.first_name = data.get('first_name', tenant.first_name)
        tenant.last_name = data.get('last_name', tenant.last_name)
        tenant.phone = data.get('phone', tenant.phone)
        tenant.emergency_contact_name = data.get('emergency_contact_name', tenant.emergency_contact_name)
        tenant.emergency_contact_number = data.get('emergency_contact_number', tenant.emergency_contact_number)

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        print("Error in update_tenant_profile:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/tenant-profile/change-password', methods=['PUT'])
def change_tenant_password():
    try:
        import urllib.parse

        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Step 1: Decode session
        session_cookie = request.cookies.get('user')
        if not session_cookie:
            return jsonify({'error': 'Authentication required'}), 401

        decoded_cookie = urllib.parse.unquote(session_cookie)
        session_data = json.loads(decoded_cookie)

        email = session_data.get('email')
        role = session_data.get('role')

        if not email or role != 'tenant':
            return jsonify({'error': 'Unauthorized access'}), 403

        # Step 2: Get tenant by email
        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        # Step 3: Get user account by tenant email
        user = Users.query.filter_by(email=tenant.email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Step 4: Validate current password
        if not check_password_hash(user.password, current_password):
            return jsonify({'error': 'Incorrect current password'}), 400

        # Step 5: Update to new hashed password
        user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        print("💥 Error changing password:", str(e))
        return jsonify({'error': 'Server error'}), 500


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
    required_fields = ['property_name', 'address', 'city', 'state', 'zip_code', 'admin_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        new_property = Properties(
            property_name=data['property_name'],  # Add this line
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
                'property_name': new_property.property_name,  # Add this line
                'address': new_property.address,
                'city': new_property.city,
                'state': new_property.state,
                'zip_code': new_property.zip_code
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create property', 'details': str(e)}), 500@app.route('/properties/admin/<int:admin_id>', methods=['GET'])
@app.route('/properties/admin/<int:admin_id>', methods=['GET'])
def get_properties_by_admin(admin_id):
    properties = Properties.query.filter_by(admin_id=admin_id).all()
    
    if not properties:
        return jsonify({'message': 'No properties found for this admin.'}), 404

    property_list = []
    for prop in properties:
        # Count total units for this property
        total_units = Units.query.filter_by(property_id=prop.id).count()
        
        # Count occupied units (units with active leases)
        occupied_units = db.session.query(Leases).join(Units).filter(
            Units.property_id == prop.id,
            Leases.lease_status == 'active'
        ).count()

        property_list.append({
            'id': prop.id,
            'address': prop.address,
            'city': prop.city,
            'state': prop.state,
            'zip_code': prop.zip_code,
            'property_name': prop.property_name,
            'total_units': total_units,
            'occupied_units': occupied_units
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

        # Check if lease should automatically be ended
        if current_lease and current_lease.end_date <= date.today():
            current_lease.lease_status = 'ended'
            unit.status = 'vacant'

            tenant = Tenants.query.get(current_lease.tenant_id)
            if tenant:
                tenant.move_out_date = date.today()

            db.session.commit()
            current_lease = None
            tenant = None

        else:
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
        }), 200

    except Exception as e:
        db.session.rollback()
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
                    # move_in_date=datetime.strptime(data['move_in_date'], '%Y-%m-%d').date(),
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
@app.route('/units/<int:unit_id>/assign-lease', methods=['POST'])
def assign_lease(unit_id):
    try:
        data = request.get_json()
        unit = Units.query.get_or_404(unit_id)

        # ✅ Validate required lease dates
        for field in ['lease_start', 'lease_end']:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        try:
            lease_start = datetime.strptime(data['lease_start'], '%Y-%m-%d').date()
            lease_end = datetime.strptime(data['lease_end'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format for lease dates'}), 400

        if lease_end <= lease_start:
            return jsonify({'error': 'Lease end date must be AFTER start date'}), 400

        # ✅ Validate payment due day
        payment_due_day = int(data.get('payment_due_day', 1))
        if not (1 <= payment_due_day <= 28):
            return jsonify({'error': 'Payment due day must be between 1 and 28'}), 400

        # ✅ Get admin_id using the same logic as tenants route
        user_id = data.get('user_id')  # Frontend should send user_id
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Get the user by user_id
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Find the admin by matching the user's email with admin's gmail
        admin = Admin.query.filter_by(gmail=user.email).first()
        if not admin:
            return jsonify({'error': 'Admin not found for this user'}), 404

        admin_id = admin.admin_id

        # ✅ CASE A: Assign existing tenant
        if data.get('tenant_id'):
            tenant = Tenants.query.get(data['tenant_id'])
            if not tenant:
                return jsonify({'error': 'Tenant not found'}), 404

            # ✅ Ensure tenant belongs to same admin as unit
            if tenant.admin_id != admin_id:
                return jsonify({'error': 'Tenant does not belong to this admin'}), 403

            # Reactivate tenant if previously inactive
            tenant.is_active = True

        else:
            # ✅ CASE B: Create new tenant
            required = [
                'first_name','last_name','email','phone','date_of_birth',
                'emergency_contact_name','emergency_contact_number',
                'move_in_date'
            ]
            missing = [f for f in required if not data.get(f)]
            if missing:
                return jsonify({'error': f'Missing tenant fields: {missing}'}), 400

            # ✅ Check for duplicate email
            if Tenants.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists in tenants'}), 400
            if Users.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists in users'}), 400

            # ✅ Hash default password
            default_password = f"{data['first_name'].lower()}@123"
            hashed_password = generate_password_hash(default_password)

            # ✅ Create tenant with the correct admin_id
            tenant = Tenants(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
                emergency_contact_name=data['emergency_contact_name'],
                emergency_contact_number=data['emergency_contact_number'],
                move_in_date=datetime.strptime(data['move_in_date'], '%Y-%m-%d').date(),
                password=hashed_password,
                admin_id=admin_id,  # Use the correct admin_id from user lookup
                is_active=True
            )
            db.session.add(tenant)
            db.session.flush()

            # ✅ Create user login account
            user = Users(
                username=data['email'],
                email=data['email'],
                password=hashed_password,
                role='tenant',
                is_active=True
            )
            db.session.add(user)

        # ✅ Create lease entry
        lease = Leases(
            tenant_id=tenant.id,
            unit_id=unit_id,
            start_date=lease_start,
            end_date=lease_end,
            monthly_rent=unit.monthly_rent,
            deposit_amount=unit.deposit_amount,
            lease_status='active',
            property_id=unit.property_id,
            admin_id=admin_id,  # Use the correct admin_id
            payment_due_day=payment_due_day
        )
        db.session.add(lease)

        # ✅ Update unit
        unit.status = 'occupied'

        db.session.commit()

        return jsonify({
            'message': 'Lease assigned successfully',
            'tenant': tenant.to_dict(),
            'lease': lease.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
@app.route('/tenants/by-admin/<int:user_id>', methods=['GET'])
def tenants_by_admin(user_id):
    try:
        tenants = Tenants.query.filter_by(admin_id=user_id).all()
        return jsonify({'tenants': [tenant.to_dict() for tenant in tenants]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/units/<int:unit_id>/record-payment', methods=['POST'])
def record_payment(unit_id):
    """Record a new rent payment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'payment_date', 'period_start', 'period_end', 'payment_method', 'admin_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate numeric fields
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than zero'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400

        # Validate dates
        try:
            payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
            period_start = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
            period_end = datetime.strptime(data['period_end'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        today = datetime.today().date()
        if payment_date > today:
            return jsonify({'error': 'Payment date cannot be in the future'}), 400
        if period_start > period_end:
            return jsonify({'error': 'Start date must be before end date'}), 400

        # Get active lease for unit
        lease = Leases.query.filter_by(
            unit_id=unit_id, 
            lease_status='active'
        ).first_or_404()

        # Create payment record
        payment = RentPayments(
            lease_id=lease.lease_id,
            payment_date=payment_date,
            amount=amount,
            payment_method=data['payment_method'],
            transaction_reference_number=data.get('transaction_reference', ''),
            period_start=period_start,
            period_end=period_end,
            status='completed',
            tenant_id=lease.tenant_id,
            admin_id=int(data['admin_id'])
        )
        db.session.add(payment)
        db.session.commit()

        # Calculate payment status for lease
        payments = RentPayments.query.filter_by(
            lease_id=lease.lease_id,
            status='completed'
        ).all()
        
        total_paid = sum(p.amount for p in payments)
        lease_start = lease.start_date
        today = datetime.today().date()
        
        # Calculate months elapsed since lease start
        months_elapsed = (today.year - lease_start.year) * 12 + today.month - lease_start.month
        if today.day > lease.start_date.day:
            months_elapsed += 1
            
        expected_total = months_elapsed * lease.monthly_rent
        balance = expected_total - total_paid
        months_paid = total_paid // lease.monthly_rent
        months_behind = months_elapsed - months_paid

        # Return payment with additional info
        payment_dict = payment.to_dict()
        payment_dict.update({
            'tenant_name': f"{lease.tenant.first_name} {lease.tenant.last_name}",
            'unit_name': lease.unit.unit_name,
            'property_name': lease.unit.property.property_name,
            'payment_month': payment.payment_date.strftime('%Y-%m')
        })

        return jsonify({
            'success': True,
            'message': 'Payment recorded successfully',
            'payment': payment_dict,
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/units/<int:unit_id>/end-lease', methods=['POST'])
def end_lease(unit_id):
    try:
        data = request.get_json() or {}
        # Fetch active lease
        lease = Leases.query.filter_by(unit_id=unit_id, lease_status='active').first()
        if not lease:
            return jsonify({'error': 'No active lease found for this unit'}), 400

        # Determine end date - ensure it's a date object
        end_date_str = data.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            end_date = date.today()
            
        # Ensure both dates are date objects for comparison
        lease_start = lease.start_date.date() if isinstance(lease.start_date, datetime) else lease.start_date
        
        if end_date < lease_start:
            return jsonify({'error': f'End date ({end_date}) cannot be before start date ({lease_start})'}), 400

        # End the lease
        lease.lease_status = 'ended'
        lease.end_date = end_date

        # Update unit status
        unit = Units.query.get(unit_id)
        if unit:
            unit.status = 'vacant'

        # Update tenant status only (no unit_id or move_out_date in your model)
        tenant = Tenants.query.get(lease.tenant_id)
        if tenant:
            tenant.is_active = False

        db.session.commit()

        return jsonify({
            'message': 'Lease ended successfully',
            'unit': unit.to_dict() if unit else None,
            'lease': lease.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        print("Error ending lease:", e)
        return jsonify({'error': str(e)}), 500
# Update Unit
@app.route('/units/<int:unit_id>', methods=['DELETE'])
def delete_unit(unit_id):
    unit = Units.query.get(unit_id)
    if not unit:
        return jsonify({'error': 'Unit not found'}), 404

    # Check if there's an active lease for this unit
    leases = Leases.query.filter_by(unit_id=unit_id).all()
    for lease in leases:
        db.session.delete(lease)  # Or you can update the lease to detach the unit_id if needed

    db.session.delete(unit)
    db.session.commit()
    return jsonify({'message': 'Unit and related leases deleted successfully'}), 200

@app.route('/units/<int:unit_id>', methods=['PATCH'])
def update_unit(unit_id):
    data = request.get_json()
    unit = Units.query.get(unit_id)

    if not unit:
        return jsonify({'error': 'Unit not found'}), 404

    for key, value in data.items():
        if hasattr(unit, key):
            setattr(unit, key, value)

    db.session.commit()
    return jsonify(unit.to_dict()), 200

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
from datetime import date
def check_and_update_leases():
    """Check all active leases and mark as ended if past end date"""
    try:
        today = date.today()
        active_leases = Leases.query.filter(
            Leases.lease_status == 'active',
            Leases.end_date <= today
        ).all()

        for lease in active_leases:
            # Update lease status
            lease.lease_status = 'ended'
            
            # Update unit status
            unit = Units.query.get(lease.unit_id)
            if unit:
                unit.status = 'vacant'
            
            db.session.add(lease)
            if unit:
                db.session.add(unit)
        
        db.session.commit()
        return f"Updated {len(active_leases)} leases"
    except Exception as e:
        db.session.rollback()
        return f"Error updating leases: {str(e)}"
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
from flask import request, jsonify, session
from models import Tenants, Leases  # make sure these are imported

import traceback

@app.route('/tenant/active-lease', methods=['GET'])
def get_active_lease():
    try:
        import json
        user_cookie = request.cookies.get('user')
        if not user_cookie:
            print("❌ No session cookie found")
            return jsonify({'error': 'Unauthorized'}), 401

        print("✅ Cookie found:", user_cookie)
        import urllib.parse
        decoded_cookie = urllib.parse.unquote(user_cookie)
        user_data = json.loads(decoded_cookie)

        email = user_data.get('email')
        if not email:
            print("❌ No email found in cookie")
            return jsonify({'error': 'Unauthorized'}), 401

        print("✅ Email from cookie:", email)
        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            print("❌ Tenant not found for email:", email)
            return jsonify({'error': 'Tenant not found'}), 404

        print("✅ Tenant found:", tenant.id)
        lease = Leases.query.filter_by(tenant_id=tenant.id, lease_status='active').first()
        if not lease:
            print("❌ No active lease found for tenant:", tenant.id)
            return jsonify({'error': 'No active lease found'}), 404

        print("✅ Lease found:", lease.lease_id)
        return jsonify({'lease': lease.to_dict()}), 200

    except Exception as e:
        print("🔥 Exception occurred:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@app.route('/tenant/file-payment', methods=['POST'])
def file_payment():
    try:
        data = request.get_json()
        print("✅ Received payment data:", data)

        # Auto parse any valid date format
        period_start = parse_date(data['period_start']).date()
        period_end = parse_date(data['period_end']).date()
        payment_date = parse_date(data['payment_date']).date()

        new_payment = RentPayments(
            lease_id=data['lease_id'],
            tenant_id=data['tenant_id'],
            admin_id=data['admin_id'],
            amount=data['amount'],
            payment_method=data['payment_method'],
            transaction_reference_number=data['transaction_reference_number'],
            period_start=period_start,
            period_end=period_end,
            payment_date=payment_date,
            status='pending'
        )

        db.session.add(new_payment)
        db.session.commit()
        print("✅ Payment record saved to database")
        return jsonify({'message': 'Payment submitted successfully'}), 201

    except Exception as e:
        db.session.rollback()
        print("🔥 Exception occurred while filing payment:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
@app.route('/admin/rent-payments/<int:admin_id>/months')
def get_payment_months(admin_id):
    """Get distinct months for which payments exist"""
    try:
        months = db.session.query(
            db.func.extract('year', RentPayments.payment_date).label('year'),
            db.func.extract('month', RentPayments.payment_date).label('month')
        ).filter(RentPayments.admin_id == admin_id)\
         .distinct()\
         .order_by('year', 'month')\
         .all()
        
        # Format as YYYY-MM
        month_options = [f"{int(m.year)}-{int(m.month):02d}" for m in months]
        return jsonify({'months': month_options})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/admin/rent-payments/<int:admin_id>')
def get_payments(admin_id):
    """Get payments with filtering options - Fixed version"""
    try:
        # Get all filter parameters
        search = request.args.get('search')
        tenant_name = request.args.get('tenant_name')
        unit_name = request.args.get('unit_name')
        property_name = request.args.get('property_name')
        reference_number = request.args.get('reference_number')
        status = request.args.get('status')
        month = request.args.get('month')
        year = request.args.get('year')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        print(f"🔍 Fetching payments for admin {admin_id} with filters:")
        print(f"   Search: {search}, Status: {status}, Month: {month}")

        # Base query - SIMPLIFIED like properties route
        query = db.session.query(
            RentPayments.payment_id,
            RentPayments.amount,
            RentPayments.payment_method,
            RentPayments.transaction_reference_number,
            RentPayments.payment_date,
            RentPayments.status,
            RentPayments.period_start,
            RentPayments.period_end,
            RentPayments.lease_id,
            RentPayments.tenant_id,
            RentPayments.admin_id,
            (Tenants.first_name + ' ' + Tenants.last_name).label('tenant_name'),
            Units.unit_name,
            Properties.property_name
        ).join(Leases, RentPayments.lease_id == Leases.lease_id)\
         .join(Tenants, RentPayments.tenant_id == Tenants.id)\
         .join(Units, Leases.unit_id == Units.unit_id)\
         .join(Properties, Units.property_id == Properties.id)\
         .filter(RentPayments.admin_id == admin_id)

        # Apply filters
        if search:
            query = query.filter(
                (Tenants.first_name + ' ' + Tenants.last_name).ilike(f'%{search}%') |
                Units.unit_name.ilike(f'%{search}%') |
                Properties.property_name.ilike(f'%{search}%') |
                RentPayments.transaction_reference_number.ilike(f'%{search}%')
            )
        if tenant_name:
            query = query.filter((Tenants.first_name + ' ' + Tenants.last_name).ilike(f'%{tenant_name}%'))
        if unit_name:
            query = query.filter(Units.unit_name.ilike(f'%{unit_name}%'))
        if property_name:
            query = query.filter(Properties.property_name.ilike(f'%{property_name}%'))
        if reference_number:
            query = query.filter(RentPayments.transaction_reference_number.ilike(f'%{reference_number}%'))
        if status:
            query = query.filter(RentPayments.status == status)
        if month:
            query = query.filter(db.func.extract('month', RentPayments.payment_date) == int(month))
        if year:
            query = query.filter(db.func.extract('year', RentPayments.payment_date) == int(year))
        if start_date:
            query = query.filter(RentPayments.payment_date >= start_date)
        if end_date:
            query = query.filter(RentPayments.payment_date <= end_date)

        # Execute query
        results = query.order_by(RentPayments.payment_date.desc()).all()

        # Format results - SIMPLE like properties route
        payments = []
        for result in results:
            payment_dict = {
                'payment_id': result.payment_id,
                'amount': float(result.amount) if result.amount else 0.0,
                'payment_method': result.payment_method,
                'transaction_reference_number': result.transaction_reference_number,
                'payment_date': result.payment_date.strftime('%Y-%m-%d') if result.payment_date else None,
                'status': result.status,
                'period_start': result.period_start.strftime('%Y-%m-%d') if result.period_start else None,
                'period_end': result.period_end.strftime('%Y-%m-%d') if result.period_end else None,
                'lease_id': result.lease_id,
                'tenant_id': result.tenant_id,
                'admin_id': result.admin_id,
                'tenant_name': result.tenant_name,
                'unit_name': result.unit_name,
                'property_name': result.property_name,
                'payment_month': result.payment_date.strftime('%Y-%m') if result.payment_date else None
            }
            payments.append(payment_dict)

        print(f"✅ Found {len(payments)} payments for admin {admin_id}")
        return jsonify({'success': True, 'payments': payments})

    except Exception as e:
        print(f"❌ Error fetching payments: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500@app.route('/admin/rent-payments/<int:admin_id>/stats', methods=['GET'])
@app.route('/admin/rent-payments/<int:admin_id>/stats', methods=['GET'])
def get_rent_stats(admin_id):
    try:
        # Get filter parameters
        month = request.args.get('month')
        year = request.args.get('year')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        print(f"\n=== Rent Stats Calculation ===\nAdmin ID: {admin_id}")

        # Determine date range
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        elif month and year:
            start_date = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d').date()
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            # Default to current month
            today = datetime.today().date()
            start_date = today.replace(day=1)
            end_date = today

        print(f"Date range: {start_date} to {end_date}")

        # SIMPLIFIED: Get expected rent from active leases
        expected_rent_query = db.session.query(
            func.sum(Leases.monthly_rent)
        ).filter(
            Leases.admin_id == admin_id,
            Leases.lease_status == 'active'
        )
        expected_rent = expected_rent_query.scalar() or 0

        # SIMPLIFIED: Get collected rent from completed payments in date range
        collected_rent_query = db.session.query(
            func.sum(RentPayments.amount)
        ).filter(
            RentPayments.admin_id == admin_id,
            RentPayments.status == 'completed',
            RentPayments.payment_date >= start_date,
            RentPayments.payment_date <= end_date
        )
        collected_rent = collected_rent_query.scalar() or 0

        print(f"Expected rent: {expected_rent}")
        print(f"Collected rent: {collected_rent}")

        # Calculate percentage
        percentage = 0
        if expected_rent > 0:
            percentage = round((collected_rent / expected_rent) * 100, 1)

        print(f"Percentage: {percentage}%")
        print("=====================\n")

        return jsonify({
            'success': True,
            'collected': float(collected_rent),
            'expected': float(expected_rent),
            'percentage': percentage
        }), 200

    except Exception as e:
        print(f"❌ Error in rent stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@app.route('/admin/rent-payments/<int:payment_id>/status', methods=['PATCH'])
def update_payment_status(payment_id):
    """Admin updates the status of a rent payment"""
    try:
        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['completed', 'rejected']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400

        payment = RentPayments.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404

        if payment.status != 'pending':
            return jsonify({'success': False, 'error': 'Only pending payments can be updated'}), 400

        payment.status = new_status
        db.session.commit()

        return jsonify({'success': True, 'message': f'Status updated to {new_status}'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
@app.route('/tenant/maintenance', methods=['POST'])
def schedule_maintenance():
    try:
        import urllib.parse

        session_cookie = request.cookies.get('user')
        if not session_cookie:
            return jsonify({'error': 'Authentication required'}), 401

        session_data = json.loads(urllib.parse.unquote(session_cookie))
        email = session_data.get('email')
        role = session_data.get('role')

        if role != 'tenant':
            return jsonify({'error': 'Unauthorized'}), 403

        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        # Get active lease
        lease = Leases.query.filter_by(tenant_id=tenant.id, lease_status='active').first()
        if not lease:
            return jsonify({'error': 'No active lease found'}), 404

        data = request.get_json()

        new_request = MaintenanceRequests(
            lease_id=lease.lease_id,
            tenant_id=tenant.id,
            admin_id=tenant.admin_id,
            request_date=datetime.now().date(),
            request_description=data.get('request_description'),
            request_status='pending',
            request_priority='secondary',  # default
            cost=None  # editable by admin later
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({'message': 'Maintenance request submitted successfully'}), 201

    except Exception as e:
        print("💥 Error scheduling maintenance:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/tenant/maintenance', methods=['GET'])
def get_tenant_maintenance_requests():
    try:
        import urllib.parse

        session_cookie = request.cookies.get('user')
        if not session_cookie:
            return jsonify({'error': 'Authentication required'}), 401

        session_data = json.loads(urllib.parse.unquote(session_cookie))
        email = session_data.get('email')
        role = session_data.get('role')

        if role != 'tenant':
            return jsonify({'error': 'Unauthorized'}), 403

        tenant = Tenants.query.filter_by(email=email).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404

        requests = MaintenanceRequests.query.filter_by(tenant_id=tenant.id).order_by(MaintenanceRequests.request_date.desc()).all()

        return jsonify([{
            'request_id': r.request_id,
            'request_date': r.request_date.strftime('%Y-%m-%d'),
            'request_description': r.request_description,
            'request_status': r.request_status,
            'request_priority': r.request_priority,
            'cost': r.cost
        } for r in requests]), 200

    except Exception as e:
        print("💥 Error retrieving tenant maintenance requests:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/admin/maintenance-requests/<int:admin_id>', methods=['GET'])
def admin_get_all_requests(admin_id):
    try:
        requests = MaintenanceRequests.query.filter_by(admin_id=admin_id).order_by(MaintenanceRequests.request_date.desc()).all()

        return jsonify([{
            'request_id': r.request_id,
            'tenant_id': r.tenant_id,
            'lease_id': r.lease_id,
            'request_date': r.request_date.strftime('%Y-%m-%d'),
            'request_description': r.request_description,
            'request_status': r.request_status,
            'request_priority': r.request_priority,
            'cost': r.cost
        } for r in requests]), 200

    except Exception as e:
        print("💥 Error retrieving admin maintenance requests:", str(e))
        return jsonify({'error': 'Server error'}), 500
@app.route('/admin/maintenance-request/<int:request_id>', methods=['PUT'])
def update_maintenance_request(request_id):
    try:
        data = request.get_json()

        req = MaintenanceRequests.query.get(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404

        # Optional fields to update
        req.request_status = data.get('request_status', req.request_status)
        req.request_priority = data.get('request_priority', req.request_priority)
        req.cost = data.get('cost', req.cost)

        db.session.commit()
        return jsonify({'message': 'Request updated successfully'}), 200

    except Exception as e:
        print("💥 Error updating maintenance request:", str(e))
        return jsonify({'error': 'Server error'}), 500

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
        db.session.commit()  # Commit to get the admin_id
        
        # Return admin_id as user_id for admin users
        user_response_id = new_admin.admin_id
    else:
        # For other roles, use the user_id
        user_response_id = new_user.user_id

    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': {
            'user_id': user_response_id,  # This will be admin_id for admins, user_id for others
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

        # Determine the ID to return based on role
        if user.role == 'admin':
            # Find the admin by matching the user's email with admin's gmail
            admin = Admin.query.filter_by(gmail=user.email).first()
            if admin:
                user_id_to_return = admin.admin_id
                print(f"Admin found, returning admin_id: {user_id_to_return}")  # Debug log
            else:
                print("Error: Admin record not found for admin user")  # Debug log
                return jsonify({'error': 'Admin record not found'}), 500
        else:
            # For non-admin users, use the user_id
            user_id_to_return = user.user_id
            print(f"Non-admin user, returning user_id: {user_id_to_return}")  # Debug log

        user_data = {
            'user_id': user_id_to_return,  # This will be admin_id for admins, user_id for others
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


# -------------------- PASSWORD RESET: REQUEST --------------------
@app.route('/auth/request-reset', methods=['POST'])
def request_password_reset():
    """
    Request a password reset token. Returns generic message regardless.
    Rate limit: 3 resets per hour per user, 5 per hour per IP
    """
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'message': 'If this email exists, we\'ve sent a reset link.'}), 200
        
        user = Users.query.filter_by(email=email).first()
        
        # Always return generic message (prevent account enumeration)
        if not user:
            return jsonify({'message': 'If this email exists, we\'ve sent a reset link.'}), 200
        
        # Rate limiting check (simplified - use Redis in production)
        ip_address = request.remote_addr
        recent_tokens = PasswordResetToken.query.filter(
            PasswordResetToken.user_id == user.user_id,
            PasswordResetToken.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).all()
        
        if len(recent_tokens) >= 3:
            print(f" Rate limit exceeded for user {user.user_id}")
            return jsonify({'message': 'If this email exists, we\'ve sent a reset link.'}), 200
        
        # Create secure token (30 minute expiry)
        reset_token_obj, raw_token = PasswordResetToken.create_token(
            user.user_id, 
            ip_address=ip_address,
            expiry_minutes=30
        )
        
        db.session.add(reset_token_obj)
        db.session.commit()
        
        # Send email
        if SMTP_USERNAME and SMTP_PASSWORD:
            email_sent = send_reset_email(user.email, raw_token)
            if not email_sent:
                print(f" Failed to send reset email to {user.email}")
                # Still return success to not leak email status
        else:
            print(" Email not configured. Reset token created but not sent.")
            print(f"Debug: Reset token for {user.email}: {raw_token}")
        
        print(f" Password reset requested for user {user.user_id} ({user.email})")
        return jsonify({'message': 'If this email exists, we\'ve sent a reset link.'}), 200
        
    except Exception as e:
        print(f" Error in request_password_reset: {str(e)}")
        return jsonify({'message': 'If this email exists, we\'ve sent a reset link.'}), 200


# -------------------- PASSWORD RESET: VERIFY TOKEN --------------------
@app.route('/auth/verify-reset-token', methods=['GET'])
def verify_reset_token():
    """Validate reset token without consuming it"""
    try:
        token = request.args.get('token', '').strip()
        
        if not token:
            return jsonify({'valid': False, 'message': 'Token missing'}), 400
        
        # Find token by raw value (we'll check hash)
        reset_tokens = PasswordResetToken.query.filter(
            PasswordResetToken.used == False
        ).all()
        
        valid_token = None
        for rt in reset_tokens:
            if check_password_hash(rt.hashed_token, token):
                valid_token = rt
                break
        
        if not valid_token:
            return jsonify({'valid': False, 'message': 'Invalid token'}), 401
        
        # Check expiration
        if datetime.utcnow() > valid_token.expires_at:
            return jsonify({'valid': False, 'message': 'Token expired'}), 401
        
        print(f" Token verified for user {valid_token.user_id}")
        return jsonify({'valid': True, 'user_id': valid_token.user_id}), 200
        
    except Exception as e:
        print(f" Error in verify_reset_token: {str(e)}")
        return jsonify({'valid': False, 'message': 'Server error'}), 500


# -------------------- PASSWORD RESET: RESET PASSWORD --------------------
@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using valid token. Token becomes single-use.
    Invalidates all existing sessions.
    """
    try:
        data = request.json
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not token or not new_password:
            return jsonify({'error': 'Token and password required'}), 400
        
        # Validate password strength (minimum 8 chars)
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Find and validate token
        reset_tokens = PasswordResetToken.query.filter(
            PasswordResetToken.used == False
        ).all()
        
        valid_token = None
        for rt in reset_tokens:
            if check_password_hash(rt.hashed_token, token):
                valid_token = rt
                break
        
        if not valid_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check expiration
        if datetime.utcnow() > valid_token.expires_at:
            return jsonify({'error': 'Token expired'}), 401
        
        user = Users.query.get(valid_token.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Mark token as used
        valid_token.used = True
        
        # Update password
        user.password = generate_password_hash(new_password)
        user.last_login = None  # Force re-authentication
        
        # Invalidate all other reset tokens for this user
        PasswordResetToken.query.filter_by(user_id=user.user_id, used=False).update({'used': True})
        
        db.session.commit()
        
        print(f" Password reset successful for user {user.user_id}")
        
        # Optional: Send confirmation email
        # send_confirmation_email(user.email)
        
        return jsonify({
            'message': 'Password reset successful. Please login with your new password.',
            'user_id': user.user_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f" Error in reset_password: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
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
      # Get start and end of the current month
        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Calculate potential revenue from active leases within the month
        potential_revenue = db.session.query(
            func.sum(Leases.monthly_rent)
        ).filter(
            Leases.admin_id == admin_id,
            Leases.start_date <= end_of_month,
            or_(
                Leases.end_date >= start_of_month,
                Leases.end_date == None
            ),
            Leases.lease_status == 'active'
        ).scalar() or 0

        
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
            .join(Leases, RentPayments.lease_id == Leases.lease_id)\
            .filter(
                RentPayments.admin_id == admin_id,
                RentPayments.status == 'completed',
                Leases.lease_status == 'active',
                extract('month', RentPayments.payment_date) == current_month,
                extract('year', RentPayments.payment_date) == current_year
            )\
            .scalar() or 0

        
        # Calculate outstanding payments
        # Subquery to calculate sum of payments per lease this month
        subq = db.session.query(
            RentPayments.lease_id,
            func.sum(RentPayments.amount).label("paid_amount")
        ).filter(
            RentPayments.status == 'completed',
            extract('month', RentPayments.payment_date) == current_month,
            extract('year', RentPayments.payment_date) == current_year
        ).group_by(RentPayments.lease_id).subquery()

        # Outer query to calculate outstanding for active leases
        outstanding_query = db.session.query(
            func.sum(Leases.monthly_rent - func.coalesce(subq.c.paid_amount, 0))
        ).outerjoin(subq, subq.c.lease_id == Leases.lease_id)\
        .filter(
            Leases.admin_id == admin_id,
            Leases.lease_status == 'active'
        ).scalar()

        outstanding = outstanding_query or 0

        
        outstanding = outstanding_query or 0

        # Recent activity (last 5 maintenance requests)
        recent_activity = MaintenanceRequests.query\
            .join(Leases, MaintenanceRequests.lease_id == Leases.lease_id)\
            .join(Tenants, Leases.tenant_id == Tenants.id)\
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
            'text': f"Maintenance for {req.lease.unit.unit_name} filed by {req.lease.tenant.first_name} {req.lease.tenant.last_name}",
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
