from app import app, db
from models import Tenants, Properties, Units, Leases, RentPayments, Expenses, MaintenanceRequests, Users
from datetime import datetime, date

with app.app_context():
    db.drop_all()
    db.create_all()

    # --- Properties ---
    properties = [
        Properties(address="123 Main St", city="Nairobi", state="Nairobi", zip_code="00100"),
        Properties(address="456 Market Rd", city="Mombasa", state="Coast", zip_code="80100"),
        Properties(address="789 Hilltop", city="Kisumu", state="Nyanza", zip_code="40100"),
        Properties(address="12 Garden Lane", city="Nakuru", state="Rift", zip_code="20100"),
        Properties(address="34 Ocean View", city="Malindi", state="Coast", zip_code="80200"),
    ]
    db.session.add_all(properties)
    db.session.commit()

    # --- Tenants ---
    tenants = [
        Tenants(first_name="Alice", last_name="Brown", email="alice@example.com", phone="0700111222",
                date_of_birth=date(1995, 5, 10), emergency_contact_name="Eve", emergency_contact_number="0722000001",
                move_in_date=date(2024, 1, 10), move_out_date=None),
        Tenants(first_name="Bob", last_name="Smith", email="bob@example.com", phone="0700111333",
                date_of_birth=date(1990, 8, 20), emergency_contact_name="Dan", emergency_contact_number="0722000002",
                move_in_date=date(2024, 2, 1), move_out_date=None),
        Tenants(first_name="Carol", last_name="Johnson", email="carol@example.com", phone="0700111444",
                date_of_birth=date(1992, 4, 22), emergency_contact_name="Sam", emergency_contact_number="0722000003",
                move_in_date=date(2024, 3, 5), move_out_date=None),
        Tenants(first_name="David", last_name="Lee", email="david@example.com", phone="0700111555",
                date_of_birth=date(1991, 6, 18), emergency_contact_name="Ben", emergency_contact_number="0722000004",
                move_in_date=date(2024, 3, 10), move_out_date=None),
        Tenants(first_name="Eva", last_name="Kim", email="eva@example.com", phone="0700111666",
                date_of_birth=date(1993, 9, 12), emergency_contact_name="Tom", emergency_contact_number="0722000005",
                move_in_date=date(2024, 4, 1), move_out_date=None),
    ]
    db.session.add_all(tenants)
    db.session.commit()

    # --- Units ---
    units = [
        Units(property_id=1, unit_number="A1", unit_name="Sunrise", status="Occupied", monthly_rent=25000, deposit_amount=50000),
        Units(property_id=1, unit_number="A2", unit_name="Sunset", status="Available", monthly_rent=27000, deposit_amount=54000),
        Units(property_id=2, unit_number="B1", unit_name="Ocean View", status="Occupied", monthly_rent=20000, deposit_amount=40000),
        Units(property_id=3, unit_number="C1", unit_name="Hilltop", status="Occupied", monthly_rent=18000, deposit_amount=36000),
        Units(property_id=4, unit_number="D1", unit_name="Garden", status="Occupied", monthly_rent=30000, deposit_amount=60000),
    ]
    db.session.add_all(units)
    db.session.commit()

    # --- Leases ---
    leases = [
        Leases(tenant_id=1, unit_id=1, start_date=date(2024, 1, 10), end_date=date(2024, 12, 31),
               monthly_rent=25000, deposit_amount=50000, lease_status="Active"),
        Leases(tenant_id=2, unit_id=3, start_date=date(2024, 2, 1), end_date=date(2024, 12, 31),
               monthly_rent=20000, deposit_amount=40000, lease_status="Active"),
        Leases(tenant_id=3, unit_id=4, start_date=date(2024, 3, 5), end_date=date(2024, 12, 31),
               monthly_rent=18000, deposit_amount=36000, lease_status="Active"),
        Leases(tenant_id=4, unit_id=5, start_date=date(2024, 3, 10), end_date=date(2024, 12, 31),
               monthly_rent=30000, deposit_amount=60000, lease_status="Active"),
        Leases(tenant_id=5, unit_id=2, start_date=date(2024, 4, 1), end_date=date(2024, 12, 31),
               monthly_rent=27000, deposit_amount=54000, lease_status="Active"),
    ]
    db.session.add_all(leases)
    db.session.commit()

    # --- Rent Payments ---
    payments = [
        RentPayments(lease_id=1, payment_date=date(2024, 2, 5), amount=25000, payment_method="Mpesa", transaction_reference_number="TXN001"),
        RentPayments(lease_id=2, payment_date=date(2024, 3, 1), amount=20000, payment_method="Cash", transaction_reference_number="TXN002"),
        RentPayments(lease_id=3, payment_date=date(2024, 4, 5), amount=18000, payment_method="Bank", transaction_reference_number="TXN003"),
        RentPayments(lease_id=4, payment_date=date(2024, 4, 10), amount=30000, payment_method="Mpesa", transaction_reference_number="TXN004"),
        RentPayments(lease_id=5, payment_date=date(2024, 5, 1), amount=27000, payment_method="Cash", transaction_reference_number="TXN005"),
    ]
    db.session.add_all(payments)

    # --- Expenses ---
    expenses = [
        Expenses(lease_id=1, expense_date=date(2024, 2, 15), expense_amount=1500, expense_description="Tap Repair", payment_reference_number="EXP001", paid_by="Caretaker"),
        Expenses(lease_id=2, expense_date=date(2024, 3, 10), expense_amount=3000, expense_description="Painting", payment_reference_number="EXP002", paid_by="Admin"),
        Expenses(lease_id=3, expense_date=date(2024, 4, 1), expense_amount=2000, expense_description="Bulb Replacement", payment_reference_number="EXP003", paid_by="Caretaker"),
        Expenses(lease_id=4, expense_date=date(2024, 4, 18), expense_amount=4000, expense_description="Fence Repair", payment_reference_number="EXP004", paid_by="Admin"),
        Expenses(lease_id=5, expense_date=date(2024, 5, 5), expense_amount=2500, expense_description="Water Pipe Fix", payment_reference_number="EXP005", paid_by="Caretaker"),
    ]
    db.session.add_all(expenses)

    # --- Maintenance Requests ---
    requests = [
        MaintenanceRequests(lease_id=1, request_date=date(2024, 2, 10), request_description="Leaking sink", request_status="Pending", request_priority="High", cost=1500),
        MaintenanceRequests(lease_id=2, request_date=date(2024, 3, 1), request_description="Broken window", request_status="In Progress", request_priority="Medium", cost=3000),
        MaintenanceRequests(lease_id=3, request_date=date(2024, 3, 20), request_description="No water", request_status="Resolved", request_priority="High", cost=2000),
        MaintenanceRequests(lease_id=4, request_date=date(2024, 4, 2), request_description="Clogged toilet", request_status="Pending", request_priority="Low", cost=1000),
        MaintenanceRequests(lease_id=5, request_date=date(2024, 5, 5), request_description="Broken door lock", request_status="Resolved", request_priority="High", cost=2500),
    ]
    db.session.add_all(requests)

    # --- Users ---
    users = [
        Users(username="admin1", password="adminpass", role="Admin", last_login=datetime.now(), is_active=True),
        Users(username="caretaker1", password="carepass", role="Caretaker", last_login=datetime.now(), is_active=True),
        Users(username="manager", password="managerpass", role="Manager", last_login=datetime.now(), is_active=True),
        Users(username="admin2", password="adminpass2", role="Admin", last_login=datetime.now(), is_active=False),
        Users(username="techguy", password="techpass", role="Technician", last_login=datetime.now(), is_active=True),
    ]
    db.session.add_all(users)

    db.session.commit()
    print("✅ Seeded 5 entries for each table successfully!")
