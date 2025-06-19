from app import app, db
from models import Admin, Users, Properties, Units, Tenants, Leases, RentPayments, Expenses, MaintenanceRequests
from datetime import date, datetime

with app.app_context():
    db.drop_all()
    db.create_all()

    # # --- Admins ---
    # admin1 = Admin(username="admin1", password="adminpass", gmail="admin1@gmail.com")
    # admin2 = Admin(username="admin2", password="adminpass", gmail="admin2@gmail.com")
    # admin3 = Admin(username="admin3", password="adminpass", gmail="admin3@gmail.com")
    # admin4 = Admin(username="admin4", password="adminpass", gmail="admin4@gmail.com")
    # admin5 = Admin(username="admin5", password="adminpass", gmail="admin5@gmail.com")
    # admin6 = Admin(username="allan",password="12345678",gmail="allan@gmail")
    # db.session.add_all([admin1, admin2, admin3, admin4, admin5])
    # db.session.commit()

    # # --- Users ---
    # user1 = Users(username="user1", email="user1@mail.com", password="pass1", role="admin", last_login=datetime.utcnow(), is_active=True)
    # user2 = Users(username="user2", email="user2@mail.com", password="pass2", role="tenant", last_login=datetime.utcnow(), is_active=True)
    # user3 = Users(username="user3", email="user3@mail.com", password="pass3", role="admin", last_login=datetime.utcnow(), is_active=True)
    # user4 = Users(username="user4", email="user4@mail.com", password="pass4", role="tenant", last_login=datetime.utcnow(), is_active=True)
    # user5 = Users(username="user5", email="user5@mail.com", password="pass5", role="admin", last_login=datetime.utcnow(), is_active=True)
    # db.session.add_all([user1, user2, user3, user4, user5])
    # db.session.commit()

    # # --- Properties ---
    # prop1 = Properties(address="101 Koinange St", city="Nairobi", state="Nairobi", zip_code="00100", admin_id=admin1.admin_id)
    # prop2 = Properties(address="202 Moi Ave", city="Nairobi", state="Nairobi", zip_code="00200", admin_id=admin2.admin_id)
    # prop3 = Properties(address="303 Haile Selassie", city="Nairobi", state="Nairobi", zip_code="00300", admin_id=admin3.admin_id)
    # prop4 = Properties(address="404 Kenyatta Ave", city="Nairobi", state="Nairobi", zip_code="00400", admin_id=admin4.admin_id)
    # prop5 = Properties(address="505 Kimathi St", city="Nairobi", state="Nairobi", zip_code="00500", admin_id=admin5.admin_id)
    # db.session.add_all([prop1, prop2, prop3, prop4, prop5])
    # db.session.commit()

    # # --- Units ---
    # unit1 = Units(property_id=prop1.id, unit_number="A1", unit_name="Alpha", status="occupied", monthly_rent=12000, deposit_amount=5000, admin_id=admin1.admin_id)
    # unit2 = Units(property_id=prop2.id, unit_number="B2", unit_name="Beta", status="vacant", monthly_rent=14000, deposit_amount=6000, admin_id=admin2.admin_id)
    # unit3 = Units(property_id=prop3.id, unit_number="C3", unit_name="Gamma", status="occupied", monthly_rent=13000, deposit_amount=5500, admin_id=admin3.admin_id)
    # unit4 = Units(property_id=prop4.id, unit_number="D4", unit_name="Delta", status="vacant", monthly_rent=15000, deposit_amount=7000, admin_id=admin4.admin_id)
    # unit5 = Units(property_id=prop5.id, unit_number="E5", unit_name="Epsilon", status="occupied", monthly_rent=16000, deposit_amount=8000, admin_id=admin5.admin_id)
    # db.session.add_all([unit1, unit2, unit3, unit4, unit5])
    # db.session.commit()

    # # --- Tenants ---
    # tenant1 = Tenants(first_name="Alice", last_name="Mwangi", email="alice@mail.com", phone="0700000001", date_of_birth=date(1990,1,1), emergency_contact_name="James", emergency_contact_number="0711000001", move_in_date=date(2024,1,1), move_out_date=None, admin_id=admin1.admin_id)
    # tenant2 = Tenants(first_name="Brian", last_name="Otieno", email="brian@mail.com", phone="0700000002", date_of_birth=date(1992,2,2), emergency_contact_name="Lucy", emergency_contact_number="0711000002", move_in_date=date(2024,2,1), move_out_date=None, admin_id=admin2.admin_id)
    # tenant3 = Tenants(first_name="Cynthia", last_name="Njeri", email="cynthia@mail.com", phone="0700000003", date_of_birth=date(1993,3,3), emergency_contact_name="Peter", emergency_contact_number="0711000003", move_in_date=date(2024,3,1), move_out_date=None, admin_id=admin3.admin_id)
    # tenant4 = Tenants(first_name="Dennis", last_name="Kamau", email="dennis@mail.com", phone="0700000004", date_of_birth=date(1994,4,4), emergency_contact_name="Ann", emergency_contact_number="0711000004", move_in_date=date(2024,4,1), move_out_date=None, admin_id=admin4.admin_id)
    # tenant5 = Tenants(first_name="Esther", last_name="Kiplagat", email="esther@mail.com", phone="0700000005", date_of_birth=date(1995,5,5), emergency_contact_name="Steve", emergency_contact_number="0711000005", move_in_date=date(2024,5,1), move_out_date=None, admin_id=admin5.admin_id)
    # db.session.add_all([tenant1, tenant2, tenant3, tenant4, tenant5])
    # db.session.commit()

    # # --- Leases ---
    # lease1 = Leases(tenant_id=tenant1.id, unit_id=unit1.unit_id, start_date=date(2024,1,1), end_date=date(2025,1,1), monthly_rent=unit1.monthly_rent, deposit_amount=unit1.deposit_amount, lease_status="active", property_id=prop1.id, admin_id=admin1.admin_id)
    # lease2 = Leases(tenant_id=tenant2.id, unit_id=unit2.unit_id, start_date=date(2024,2,1), end_date=date(2025,2,1), monthly_rent=unit2.monthly_rent, deposit_amount=unit2.deposit_amount, lease_status="active", property_id=prop2.id, admin_id=admin2.admin_id)
    # lease3 = Leases(tenant_id=tenant3.id, unit_id=unit3.unit_id, start_date=date(2024,3,1), end_date=date(2025,3,1), monthly_rent=unit3.monthly_rent, deposit_amount=unit3.deposit_amount, lease_status="active", property_id=prop3.id, admin_id=admin3.admin_id)
    # lease4 = Leases(tenant_id=tenant4.id, unit_id=unit4.unit_id, start_date=date(2024,4,1), end_date=date(2025,4,1), monthly_rent=unit4.monthly_rent, deposit_amount=unit4.deposit_amount, lease_status="active", property_id=prop4.id, admin_id=admin4.admin_id)
    # lease5 = Leases(tenant_id=tenant5.id, unit_id=unit5.unit_id, start_date=date(2024,5,1), end_date=date(2025,5,1), monthly_rent=unit5.monthly_rent, deposit_amount=unit5.deposit_amount, lease_status="active", property_id=prop5.id, admin_id=admin5.admin_id)
    # db.session.add_all([lease1, lease2, lease3, lease4, lease5])
    # db.session.commit()

    # # --- Rent Payments ---
    # pay1 = RentPayments(lease_id=lease1.lease_id, payment_date=date(2024,6,1), admin_id=admin1.admin_id, amount=lease1.monthly_rent, payment_method="Mpesa", transaction_reference_number="MPESA123")
    # pay2 = RentPayments(lease_id=lease2.lease_id, payment_date=date(2024,6,2), admin_id=admin2.admin_id, amount=lease2.monthly_rent, payment_method="Mpesa", transaction_reference_number="MPESA124")
    # pay3 = RentPayments(lease_id=lease3.lease_id, payment_date=date(2024,6,3), admin_id=admin3.admin_id, amount=lease3.monthly_rent, payment_method="Bank", transaction_reference_number="BANK125")
    # pay4 = RentPayments(lease_id=lease4.lease_id, payment_date=date(2024,6,4), admin_id=admin4.admin_id, amount=lease4.monthly_rent, payment_method="Cash", transaction_reference_number="CASH126")
    # pay5 = RentPayments(lease_id=lease5.lease_id, payment_date=date(2024,6,5), admin_id=admin5.admin_id, amount=lease5.monthly_rent, payment_method="Mpesa", transaction_reference_number="MPESA127")
    # db.session.add_all([pay1, pay2, pay3, pay4, pay5])
    # db.session.commit()

    # # --- Expenses ---
    # exp1 = Expenses(lease_id=lease1.lease_id, expense_date=date(2024,6,1), expense_amount=1000, expense_description="Fix plumbing", payment_reference_number="EXP001", paid_by="Admin", admin_id=admin1.admin_id)
    # exp2 = Expenses(lease_id=lease2.lease_id, expense_date=date(2024,6,2), expense_amount=2000, expense_description="Paint walls", payment_reference_number="EXP002", paid_by="Admin", admin_id=admin2.admin_id)
    # exp3 = Expenses(lease_id=lease3.lease_id, expense_date=date(2024,6,3), expense_amount=1500, expense_description="Replace bulbs", payment_reference_number="EXP003", paid_by="Admin", admin_id=admin3.admin_id)
    # exp4 = Expenses(lease_id=lease4.lease_id, expense_date=date(2024,6,4), expense_amount=2500, expense_description="New locks", payment_reference_number="EXP004", paid_by="Admin", admin_id=admin4.admin_id)
    # exp5 = Expenses(lease_id=lease5.lease_id, expense_date=date(2024,6,5), expense_amount=1200, expense_description="Carpet cleaning", payment_reference_number="EXP005", paid_by="Admin", admin_id=admin5.admin_id)
    # db.session.add_all([exp1, exp2, exp3, exp4, exp5])
    # db.session.commit()

    # # --- Maintenance Requests ---
    # req1 = MaintenanceRequests(lease_id=lease1.lease_id, request_date=date(2024,6,1), request_description="Leaking tap", request_status="completed", request_priority="high", cost=500, admin_id=admin1.admin_id)
    # req2 = MaintenanceRequests(lease_id=lease2.lease_id, request_date=date(2024,6,2), request_description="Broken window", request_status="pending", request_priority="medium", cost=800, admin_id=admin2.admin_id)
    # req3 = MaintenanceRequests(lease_id=lease3.lease_id, request_date=date(2024,6,3), request_description="AC not working", request_status="in-progress", request_priority="high", cost=1500, admin_id=admin3.admin_id)
    # req4 = MaintenanceRequests(lease_id=lease4.lease_id, request_date=date(2024,6,4), request_description="Power outage", request_status="resolved", request_priority="high", cost=0, admin_id=admin4.admin_id)
    # req5 = MaintenanceRequests(lease_id=lease5.lease_id, request_date=date(2024,6,5), request_description="Toilet blocked", request_status="pending", request_priority="low", cost=700, admin_id=admin5.admin_id)
    # db.session.add_all([req1, req2, req3, req4, req5])
    # db.session.commit()

    # print("✅ Seeded 5 records in each table manually.")
