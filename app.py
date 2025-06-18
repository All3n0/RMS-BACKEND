from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from datetime import datetime

# === Initialize extensions (no app bound yet) ===
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# === Create Flask app ===
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    property = property_schema.load(request.json)
    db.session.add(property)
    db.session.commit()
    return property_schema.jsonify(property), 201

@app.route('/properties', methods=['GET'])
def get_properties():
    return properties_schema.jsonify(Properties.query.all())

@app.route('/properties/<int:id>', methods=['PUT'])
def update_property(id):
    prop = Properties.query.get_or_404(id)
    for k, v in request.json.items():
        setattr(prop, k, v)
    db.session.commit()
    return property_schema.jsonify(prop)

@app.route('/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    db.session.delete(Properties.query.get_or_404(id))
    db.session.commit()
    return '', 204

# ------- UNITS -------
@app.route('/units', methods=['POST'])
def create_unit():
    unit = unit_schema.load(request.json)
    db.session.add(unit)
    db.session.commit()
    return unit_schema.jsonify(unit), 201

@app.route('/units', methods=['GET'])
def get_units():
    return units_schema.jsonify(Units.query.all())

@app.route('/units/<int:id>', methods=['PUT'])
def update_unit(id):
    unit = Units.query.get_or_404(id)
    for k, v in request.json.items():
        setattr(unit, k, v)
    db.session.commit()
    return unit_schema.jsonify(unit)

@app.route('/units/<int:id>', methods=['DELETE'])
def delete_unit(id):
    db.session.delete(Units.query.get_or_404(id))
    db.session.commit()
    return '', 204

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

@app.route('/rent_payments', methods=['GET'])
def get_rents():
    return rents_schema.jsonify(RentPayments.query.all())

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


# === Run the app ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
