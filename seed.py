# # from app import app, db
# # from models import Admin, Users, Properties, Units, Tenants, Leases, RentPayments, Expenses, MaintenanceRequests
# # from datetime import date, datetime

# # with app.app_context():
# #     db.drop_all()
# #     db.create_all()

#     # # --- Admins ---
#     # admin1 = Admin(username="admin1", password="adminpass", gmail="admin1@gmail.com")
#     # admin2 = Admin(username="admin2", password="adminpass", gmail="admin2@gmail.com")
#     # admin3 = Admin(username="admin3", password="adminpass", gmail="admin3@gmail.com")
#     # admin4 = Admin(username="admin4", password="adminpass", gmail="admin4@gmail.com")
#     # admin5 = Admin(username="admin5", password="adminpass", gmail="admin5@gmail.com")
#     # admin6 = Admin(username="allan",password="12345678",gmail="allan@gmail")
#     # db.session.add_all([admin1, admin2, admin3, admin4, admin5])
#     # db.session.commit()

#     # # --- Users ---
#     # user1 = Users(username="user1", email="user1@mail.com", password="pass1", role="admin", last_login=datetime.utcnow(), is_active=True)
#     # user2 = Users(username="user2", email="user2@mail.com", password="pass2", role="tenant", last_login=datetime.utcnow(), is_active=True)
#     # user3 = Users(username="user3", email="user3@mail.com", password="pass3", role="admin", last_login=datetime.utcnow(), is_active=True)
#     # user4 = Users(username="user4", email="user4@mail.com", password="pass4", role="tenant", last_login=datetime.utcnow(), is_active=True)
#     # user5 = Users(username="user5", email="user5@mail.com", password="pass5", role="admin", last_login=datetime.utcnow(), is_active=True)
#     # db.session.add_all([user1, user2, user3, user4, user5])
#     # db.session.commit()

#     # # --- Properties ---
#     # prop1 = Properties(address="101 Koinange St", city="Nairobi", state="Nairobi", zip_code="00100", admin_id=admin1.admin_id)
#     # prop2 = Properties(address="202 Moi Ave", city="Nairobi", state="Nairobi", zip_code="00200", admin_id=admin2.admin_id)
#     # prop3 = Properties(address="303 Haile Selassie", city="Nairobi", state="Nairobi", zip_code="00300", admin_id=admin3.admin_id)
#     # prop4 = Properties(address="404 Kenyatta Ave", city="Nairobi", state="Nairobi", zip_code="00400", admin_id=admin4.admin_id)
#     # prop5 = Properties(address="505 Kimathi St", city="Nairobi", state="Nairobi", zip_code="00500", admin_id=admin5.admin_id)
#     # db.session.add_all([prop1, prop2, prop3, prop4, prop5])
#     # db.session.commit()

#     # # --- Units ---
#     # unit1 = Units(property_id=prop1.id, unit_number="A1", unit_name="Alpha", status="occupied", monthly_rent=12000, deposit_amount=5000, admin_id=admin1.admin_id)
#     # unit2 = Units(property_id=prop2.id, unit_number="B2", unit_name="Beta", status="vacant", monthly_rent=14000, deposit_amount=6000, admin_id=admin2.admin_id)
#     # unit3 = Units(property_id=prop3.id, unit_number="C3", unit_name="Gamma", status="occupied", monthly_rent=13000, deposit_amount=5500, admin_id=admin3.admin_id)
#     # unit4 = Units(property_id=prop4.id, unit_number="D4", unit_name="Delta", status="vacant", monthly_rent=15000, deposit_amount=7000, admin_id=admin4.admin_id)
#     # unit5 = Units(property_id=prop5.id, unit_number="E5", unit_name="Epsilon", status="occupied", monthly_rent=16000, deposit_amount=8000, admin_id=admin5.admin_id)
#     # db.session.add_all([unit1, unit2, unit3, unit4, unit5])
#     # db.session.commit()

#     # # --- Tenants ---
#     # tenant1 = Tenants(first_name="Alice", last_name="Mwangi", email="alice@mail.com", phone="0700000001", date_of_birth=date(1990,1,1), emergency_contact_name="James", emergency_contact_number="0711000001", move_in_date=date(2024,1,1), move_out_date=None, admin_id=admin1.admin_id)
#     # tenant2 = Tenants(first_name="Brian", last_name="Otieno", email="brian@mail.com", phone="0700000002", date_of_birth=date(1992,2,2), emergency_contact_name="Lucy", emergency_contact_number="0711000002", move_in_date=date(2024,2,1), move_out_date=None, admin_id=admin2.admin_id)
#     # tenant3 = Tenants(first_name="Cynthia", last_name="Njeri", email="cynthia@mail.com", phone="0700000003", date_of_birth=date(1993,3,3), emergency_contact_name="Peter", emergency_contact_number="0711000003", move_in_date=date(2024,3,1), move_out_date=None, admin_id=admin3.admin_id)
#     # tenant4 = Tenants(first_name="Dennis", last_name="Kamau", email="dennis@mail.com", phone="0700000004", date_of_birth=date(1994,4,4), emergency_contact_name="Ann", emergency_contact_number="0711000004", move_in_date=date(2024,4,1), move_out_date=None, admin_id=admin4.admin_id)
#     # tenant5 = Tenants(first_name="Esther", last_name="Kiplagat", email="esther@mail.com", phone="0700000005", date_of_birth=date(1995,5,5), emergency_contact_name="Steve", emergency_contact_number="0711000005", move_in_date=date(2024,5,1), move_out_date=None, admin_id=admin5.admin_id)
#     # db.session.add_all([tenant1, tenant2, tenant3, tenant4, tenant5])
#     # db.session.commit()

#     # # --- Leases ---
#     # lease1 = Leases(tenant_id=tenant1.id, unit_id=unit1.unit_id, start_date=date(2024,1,1), end_date=date(2025,1,1), monthly_rent=unit1.monthly_rent, deposit_amount=unit1.deposit_amount, lease_status="active", property_id=prop1.id, admin_id=admin1.admin_id)
#     # lease2 = Leases(tenant_id=tenant2.id, unit_id=unit2.unit_id, start_date=date(2024,2,1), end_date=date(2025,2,1), monthly_rent=unit2.monthly_rent, deposit_amount=unit2.deposit_amount, lease_status="active", property_id=prop2.id, admin_id=admin2.admin_id)
#     # lease3 = Leases(tenant_id=tenant3.id, unit_id=unit3.unit_id, start_date=date(2024,3,1), end_date=date(2025,3,1), monthly_rent=unit3.monthly_rent, deposit_amount=unit3.deposit_amount, lease_status="active", property_id=prop3.id, admin_id=admin3.admin_id)
#     # lease4 = Leases(tenant_id=tenant4.id, unit_id=unit4.unit_id, start_date=date(2024,4,1), end_date=date(2025,4,1), monthly_rent=unit4.monthly_rent, deposit_amount=unit4.deposit_amount, lease_status="active", property_id=prop4.id, admin_id=admin4.admin_id)
#     # lease5 = Leases(tenant_id=tenant5.id, unit_id=unit5.unit_id, start_date=date(2024,5,1), end_date=date(2025,5,1), monthly_rent=unit5.monthly_rent, deposit_amount=unit5.deposit_amount, lease_status="active", property_id=prop5.id, admin_id=admin5.admin_id)
#     # db.session.add_all([lease1, lease2, lease3, lease4, lease5])
#     # db.session.commit()

#     # # --- Rent Payments ---
#     # pay1 = RentPayments(lease_id=lease1.lease_id, payment_date=date(2024,6,1), admin_id=admin1.admin_id, amount=lease1.monthly_rent, payment_method="Mpesa", transaction_reference_number="MPESA123")
#     # pay2 = RentPayments(lease_id=lease2.lease_id, payment_date=date(2024,6,2), admin_id=admin2.admin_id, amount=lease2.monthly_rent, payment_method="Mpesa", transaction_reference_number="MPESA124")
#     # pay3 = RentPayments(lease_id=lease3.lease_id, payment_date=date(2024,6,3), admin_id=admin3.admin_id, amount=lease3.monthly_rent, payment_method="Bank", transaction_reference_number="BANK125")
#     # pay4 = RentPayments(lease_id=lease4.lease_id, payment_date=date(2024,6,4), admin_id=admin4.admin_id, amount=lease4.monthly_rent, payment_method="Cash", transaction_reference_number="CASH126")
#     # pay5 = RentPayments(lease_id=lease5.lease_id, payment_date=date(2024,6,5), admin_id=admin5.admin_id, amount=lease5.monthly_rent, payment_method="Mpesa", transaction_reference_number="MPESA127")
#     # db.session.add_all([pay1, pay2, pay3, pay4, pay5])
#     # db.session.commit()

#     # # --- Expenses ---
#     # exp1 = Expenses(lease_id=lease1.lease_id, expense_date=date(2024,6,1), expense_amount=1000, expense_description="Fix plumbing", payment_reference_number="EXP001", paid_by="Admin", admin_id=admin1.admin_id)
#     # exp2 = Expenses(lease_id=lease2.lease_id, expense_date=date(2024,6,2), expense_amount=2000, expense_description="Paint walls", payment_reference_number="EXP002", paid_by="Admin", admin_id=admin2.admin_id)
#     # exp3 = Expenses(lease_id=lease3.lease_id, expense_date=date(2024,6,3), expense_amount=1500, expense_description="Replace bulbs", payment_reference_number="EXP003", paid_by="Admin", admin_id=admin3.admin_id)
#     # exp4 = Expenses(lease_id=lease4.lease_id, expense_date=date(2024,6,4), expense_amount=2500, expense_description="New locks", payment_reference_number="EXP004", paid_by="Admin", admin_id=admin4.admin_id)
#     # exp5 = Expenses(lease_id=lease5.lease_id, expense_date=date(2024,6,5), expense_amount=1200, expense_description="Carpet cleaning", payment_reference_number="EXP005", paid_by="Admin", admin_id=admin5.admin_id)
#     # db.session.add_all([exp1, exp2, exp3, exp4, exp5])
#     # db.session.commit()

#     # # --- Maintenance Requests ---
#     # req1 = MaintenanceRequests(lease_id=lease1.lease_id, request_date=date(2024,6,1), request_description="Leaking tap", request_status="completed", request_priority="high", cost=500, admin_id=admin1.admin_id)
#     # req2 = MaintenanceRequests(lease_id=lease2.lease_id, request_date=date(2024,6,2), request_description="Broken window", request_status="pending", request_priority="medium", cost=800, admin_id=admin2.admin_id)
#     # req3 = MaintenanceRequests(lease_id=lease3.lease_id, request_date=date(2024,6,3), request_description="AC not working", request_status="in-progress", request_priority="high", cost=1500, admin_id=admin3.admin_id)
#     # req4 = MaintenanceRequests(lease_id=lease4.lease_id, request_date=date(2024,6,4), request_description="Power outage", request_status="resolved", request_priority="high", cost=0, admin_id=admin4.admin_id)
#     # req5 = MaintenanceRequests(lease_id=lease5.lease_id, request_date=date(2024,6,5), request_description="Toilet blocked", request_status="pending", request_priority="low", cost=700, admin_id=admin5.admin_id)
#     # db.session.add_all([req1, req2, req3, req4, req5])
#     # db.session.commit()

#     # print("✅ Seeded 5 records in each table manually.")
# import sqlite3
# from app import db, app
# from models import Tenants, Properties, Units, Leases, RentPayments, Expenses, MaintenanceRequests, Users, Admin
# from datetime import datetime

# # # Path to your backup database
# BACKUP_DB_PATH = "your_database_backup.db"

# def safe_parse_date(value, fmt="%Y-%m-%d", default="2000-01-01"):
#     """Safely parse a date string. Returns default date if invalid."""
#     try:
#         return datetime.strptime(value, fmt).date()
#     except (ValueError, TypeError):
#         return datetime.strptime(default, fmt).date()


# def safe_parse_datetime(value, fmt="%Y-%m-%d %H:%M:%S"):
#     """Safely parse a datetime string. Returns None if invalid."""
#     try:
#         return datetime.strptime(value, fmt)
#     except (ValueError, TypeError):
#         return None

# def seed_from_backup():
#     conn = sqlite3.connect(BACKUP_DB_PATH)
#     cursor = conn.cursor()

#     with app.app_context():
#         # Clear existing data
#         db.session.query(MaintenanceRequests).delete()
#         db.session.query(Expenses).delete()
#         db.session.query(RentPayments).delete()
#         db.session.query(Leases).delete()
#         db.session.query(Units).delete()
#         db.session.query(Properties).delete()
#         db.session.query(Tenants).delete()
#         db.session.query(Users).delete()
#         db.session.query(Admin).delete()
#         db.session.commit()

#         # ---------------- Seed Admins ----------------
#         cursor.execute("SELECT * FROM admin")
#         for row in cursor.fetchall():
#             admin = Admin(
#                 admin_id=row[0],
#                 username=row[1],
#                 password=row[2],
#                 gmail=row[3]
#             )
#             db.session.add(admin)

#         # ---------------- Seed Tenants ----------------
#         existing_emails = set()

#         # Inside your Tenants loop
#         for row in cursor.fetchall():
#             full_name = row[1].split(" ", 1)
#             first_name = full_name[0]
#             last_name = full_name[1] if len(full_name) > 1 else ""

#             # Original email from backup
#             email = row[2] if len(row) > 2 and row[2] else f"user{row[0]}@example.com"

#             # Ensure uniqueness
#             if email in existing_emails:
#                 name_part, domain = email.split("@")
#                 email = f"{name_part}_{row[0]}@{domain}"

#             existing_emails.add(email)

#             tenant = Tenants(
#                 id=row[0],
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 phone=row[3] if len(row) > 3 else "",
#                 date_of_birth=safe_parse_date(row[4]) if len(row) > 4 else safe_parse_date(None),
#                 emergency_contact_name=row[5] if len(row) > 5 else "N/A",
#                 emergency_contact_number=row[6] if len(row) > 6 else "N/A",
#                 is_active=bool(row[7]) if len(row) > 7 else True,
#                 password=row[8] if len(row) > 8 else "defaultpassword",
#                 admin_id=row[9] if len(row) > 9 else 1
#             )
#             db.session.add(tenant)


#         # ---------------- Seed Properties ----------------
#         cursor.execute("SELECT * FROM properties")
#         for row in cursor.fetchall():
#             prop = Properties(
#                 id=row[0],
#                 property_name=row[1],
#                 address=row[2],
#                 city=row[3],
#                 state=row[4],
#                 zip_code=row[5],
#                 name=row[6] if len(row) > 6 else "Unnamed",
#                 admin_id=row[7] if len(row) > 7 else 1
#             )
#             db.session.add(prop)

#         # ---------------- Seed Units ----------------
#         cursor.execute("SELECT * FROM units")
#         for row in cursor.fetchall():
#             unit = Units(
#                 unit_id=row[0],
#                 property_id=row[1],
#                 unit_number=row[2],
#                 unit_name=row[3],
#                 status=row[4],
#                 monthly_rent=row[5],
#                 deposit_amount=row[6],
#                 admin_id=row[7],
#                 type=row[8] if len(row) > 8 else "Unknown"
#             )
#             db.session.add(unit)

#         # ---------------- Seed Leases ----------------
#         cursor.execute("SELECT * FROM leases")
#         for row in cursor.fetchall():
#             lease = Leases(
#                 lease_id=row[0],
#                 tenant_id=row[1],
#                 unit_id=row[2],
#                 start_date=safe_parse_date(row[3]),
#                 end_date=safe_parse_date(row[4]),
#                 monthly_rent=row[5],
#                 deposit_amount=row[6],
#                 lease_status=row[7],
#                 property_id=row[8],
#                 admin_id=row[9],
#                 payment_due_day=row[10] if len(row) > 10 else 1
#             )
#             db.session.add(lease)

#         # ---------------- Seed RentPayments ----------------
#         cursor.execute("SELECT * FROM rent_payments")
#         for row in cursor.fetchall():
#             payment = RentPayments(
#                 payment_id=row[0],
#                 lease_id=row[1],
#                 payment_date=safe_parse_date(row[2]),
#                 admin_id=row[3],
#                 amount=row[4],
#                 payment_method=row[5],
#                 transaction_reference_number=row[6],
#                 period_start=safe_parse_date(row[7]),
#                 period_end=safe_parse_date(row[8]),
#                 status=row[9],
#                 tenant_id=row[10]
#             )
#             db.session.add(payment)

#         # ---------------- Seed Expenses ----------------
#         cursor.execute("SELECT * FROM expenses")
#         for row in cursor.fetchall():
#             expense = Expenses(
#                 expense_id=row[0],
#                 lease_id=row[1],
#                 expense_date=safe_parse_date(row[2]),
#                 expense_amount=row[3],
#                 expense_description=row[4],
#                 payment_reference_number=row[5],
#                 paid_by=row[6],
#                 admin_id=row[7]
#             )
#             db.session.add(expense)

#         # ---------------- Seed MaintenanceRequests ----------------
#         def safe_value(value, default):
#             """Return value if valid, else return default."""
#             if value is None or value == "":
#                 return default
#             return value

#         # Seed MaintenanceRequests
#         cursor.execute("SELECT * FROM maintenance_requests")
#         for row in cursor.fetchall():
#             request = MaintenanceRequests(
#                 request_id=row[0],
#                 lease_id=row[1],
#                 tenant_id=row[2],
#                 request_date=safe_parse_date(row[3]),  # Use your existing date helper
#                 request_description=row[4] if len(row) > 4 else "No description",
#                 request_status=safe_value(row[5], "pending"),
#                 request_priority=safe_value(row[6], "normal"),  # Default priority
#                 cost=row[7] if row[7] is not None else 0.0,
#                 admin_id=row[8] if len(row) > 8 else 1
#             )
#             db.session.add(request)


#         # ---------------- Seed Users ----------------
#         cursor.execute("SELECT * FROM users")
#         for row in cursor.fetchall():
#             user = Users(
#                 user_id=row[0],
#                 username=row[1],
#                 email=row[2],
#                 password=row[3],
#                 role=row[4],
#                 last_login=safe_parse_datetime(row[5]),
#                 is_active=bool(row[6]) if len(row) > 6 else True
#             )
#             db.session.add(user)

#         db.session.commit()
#         print("Seeding complete!")

#     conn.close()

# if __name__ == "__main__":
#     seed_from_backup()
import sqlite3
from app import db, app
from models import Tenants
from datetime import datetime

BACKUP_DB_PATH = "your_database_backup.db"

def safe_parse_date(value, fmt="%Y-%m-%d", default="2000-01-01"):
    """Safely parse a date string. Returns default date if invalid."""
    try:
        return datetime.strptime(value, fmt).date()
    except (ValueError, TypeError):
        return datetime.strptime(default, fmt).date()

def seed_tenants():
    conn = sqlite3.connect(BACKUP_DB_PATH)
    cursor = conn.cursor()

    with app.app_context():
        cursor.execute("SELECT * FROM tenants")
        rows = cursor.fetchall()

        for row in rows:
    # Ensure email exists
            email = row[3] if len(row) > 3 and row[3] else f"user{row[0]}@example.com"

            # Skip if tenant with this email already exists
            if db.session.query(Tenants).filter_by(email=email).first():
                continue

            # Ensure password is not null
            password = row[9] if len(row) > 9 and row[9] else "defaultpassword123"

            tenant = Tenants(
                id=row[0],
                first_name=row[1] if len(row) > 1 else "",
                last_name=row[2] if len(row) > 2 else "",
                email=email,
                phone=row[4] if len(row) > 4 else "",
                date_of_birth=safe_parse_date(row[5]) if len(row) > 5 else safe_parse_date(None),
                emergency_contact_name=row[6] if len(row) > 6 else "N/A",
                emergency_contact_number=row[7] if len(row) > 7 else "N/A",
                is_active=bool(row[8]) if len(row) > 8 else True,
                password=password,
                admin_id=row[10] if len(row) > 10 else 1
            )
            db.session.add(tenant)


        db.session.commit()
    conn.close()
    print("Tenants seeding complete!")

if __name__ == "__main__":
    seed_tenants()
