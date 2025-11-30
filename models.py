from config import db
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash

class PasswordResetToken(db.Model):
    """Store password reset tokens with expiration and usage tracking"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hashed_token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    
    user = db.relationship('Users', backref='reset_tokens', lazy=True)
    
    @staticmethod
    def create_token(user_id, ip_address=None, expiry_minutes=30):
        """Generate a new password reset token (raw + hashed)"""
        raw_token = secrets.token_urlsafe(48)  # 64 bytes in URL-safe format
        hashed_token = generate_password_hash(raw_token)
        
        reset_token = PasswordResetToken(
            id=secrets.token_hex(18),  # UUID-like ID
            user_id=user_id,
            hashed_token=hashed_token,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
            ip_address=ip_address
        )
        
        return reset_token, raw_token  # Return token object and raw token for email

class Tenants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    emergency_contact_name = db.Column(db.String(50), nullable=False)
    emergency_contact_number= db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    password = db.Column(db.String(50), nullable=False)
    leases=db.relationship('Leases', backref='tenant', lazy=True)
    payments = db.relationship('RentPayments', backref='payment_tenant', lazy=True, foreign_keys='RentPayments.tenant_id')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_number': self.emergency_contact_number,
            'is_active': self.is_active,
            'admin_id': self.admin_id
        }
class Properties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_name=db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False,default='unnamed')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)  # 🔥 Add this

    units = db.relationship('Units', backref='property', lazy=True)
    leases = db.relationship('Leases', backref='property', lazy=True)



class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    gmail = db.Column(db.String(50), nullable=False)
    property = db.relationship('Properties', backref='admin', lazy=True)
    tenants = db.relationship('Tenants', backref='admin', lazy=True)
    units = db.relationship('Units', backref='admin', lazy=True)
    leases = db.relationship('Leases', backref='admin', lazy=True)
    rent_payments = db.relationship('RentPayments', backref='admin', lazy=True)
    expenses = db.relationship('Expenses', backref='admin', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequests', backref='admin', lazy=True)
    # users = db.relationship('Users', backref='admin', lazy=True)
    
class Units(db.Model):
    unit_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    unit_number = db.Column(db.String(50), nullable=False)
    unit_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    type=db.Column(db.String(50), nullable=False)
    # tenants = db.relationship('Leases', backref='unit', lazy=True)
     
    def to_dict(self):
        return {
            'unit_id': self.unit_id,
            'property_id': self.property_id,
            'unit_number': self.unit_number,
            'unit_name': self.unit_name,
            'status': self.status,
            'monthly_rent': self.monthly_rent,
            'deposit_amount': self.deposit_amount,
            'admin_id': self.admin_id,
            'type': self.type
        }
class Leases(db.Model):
    lease_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.unit_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    lease_status = db.Column(db.String(50), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    # lease_documents = db.relationship('LeaseDocuments', backref='lease', lazy=True)
    payment_due_day = db.Column(db.Integer, nullable=False)
    payments=db.relationship('RentPayments', backref='lease', lazy=True)
    unit=db.relationship('Units', backref='lease', lazy=True)
    
    def to_dict(self):
        return {
            'lease_id': self.lease_id,
            'tenant_id': self.tenant_id,
            'unit_id': self.unit_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'monthly_rent': self.monthly_rent,
            'deposit_amount': self.deposit_amount,
            'lease_status': self.lease_status,
            'property_id': self.property_id,
            'admin_id': self.admin_id,
            'payment_due_day': self.payment_due_day
        }
class RentPayments(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.lease_id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_reference_number = db.Column(db.String(50), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    status=db.Column(db.String(50), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'lease_id': self.lease_id,
            'payment_date': self.payment_date,
            'admin_id': self.admin_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_reference_number': self.transaction_reference_number,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'status': self.status,
            'tenant_id': self.tenant_id
        }
class Expenses(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.lease_id'), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    expense_amount = db.Column(db.Float, nullable=False)
    expense_description = db.Column(db.String(50), nullable=False)
    payment_reference_number = db.Column(db.String(50), nullable=False)
    paid_by= db.Column(db.String(50), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)

class MaintenanceRequests(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.lease_id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_description = db.Column(db.String(50), nullable=False)
    request_status = db.Column(db.String(50), nullable=False)
    request_priority = db.Column(db.String(50), nullable=False)
    cost= db.Column(db.Float, nullable=True)
    lease=  db.relationship('Leases', backref='maintenance_request', lazy=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False,server_default='xxx', unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'last_login': self.last_login,
            'is_active': self.is_active
        }