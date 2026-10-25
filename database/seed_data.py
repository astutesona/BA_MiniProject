"""
Database Seeding Script for Business Sales Intelligence and Revenue Analytics System
Populates realistic business records: Users, Categories, Products, Customers, Orders,
Order Items, and Sales Targets across 14 months with reproducible seed (seed=42).
"""

import os
import sys
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from werkzeug.security import generate_password_hash

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.customer import Customer
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.sales_target import SalesTarget

def ensure_database_exists():
    import pymysql
    host = os.environ.get('DB_HOST', 'localhost')
    port = int(os.environ.get('DB_PORT', '3306'))
    user = os.environ.get('DB_USER', 'root')
    password = os.environ.get('DB_PASSWORD', '12345678')
    dbname = os.environ.get('DB_NAME', 'business_sales_intelligence')

    print(f"[*] Ensuring database `{dbname}` exists on {host}:{port}...")
    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    conn.close()
    print(f"[+] Database `{dbname}` verified.")

def seed_database(drop_all=False):
    ensure_database_exists()
    app = create_app()
    with app.app_context():
        print("[*] Starting database initialization and seeding...")
        random.seed(42)

        if drop_all:
            print("[-] Dropping all tables...")
            db.drop_all()

        print("[+] Creating tables according to schema models...")
        db.create_all()

        # ---------------------------------------------------------------------
        # 1. Seed Users (Admin, Sales Employee, Manager)
        # ---------------------------------------------------------------------
        print("[+] Checking and seeding application users...")
        users_data = [
            {
                "full_name": "Eleanor Vance (System Administrator)",
                "username": "admin",
                "email": "admin@salesintel.local",
                "password_hash": generate_password_hash("Admin@123"),
                "role": "Admin",
                "is_active": True
            },
            {
                "full_name": "Marcus Sterling (Regional Sales Lead)",
                "username": "sales1",
                "email": "marcus.sales@salesintel.local",
                "password_hash": generate_password_hash("Sales@123"),
                "role": "Sales Employee",
                "is_active": True
            },
            {
                "full_name": "Diana Ross (Business & Operations Manager)",
                "username": "manager",
                "email": "diana.manager@salesintel.local",
                "password_hash": generate_password_hash("Manager@123"),
                "role": "Manager",
                "is_active": True
            },
            {
                "full_name": "Lucas Grey (Junior Sales Associate)",
                "username": "sales2",
                "email": "lucas.grey@salesintel.local",
                "password_hash": generate_password_hash("Sales@123"),
                "role": "Sales Employee",
                "is_active": True
            }
        ]

        user_objs = {}
        for u in users_data:
            existing = User.query.filter_by(username=u["username"]).first()
            if not existing:
                user_obj = User(**u)
                db.session.add(user_obj)
                db.session.flush()
                user_objs[u["username"]] = user_obj
            else:
                user_objs[u["username"]] = existing
        db.session.commit()
        print(f"    Users verified: {len(user_objs)} users active.")

        # ---------------------------------------------------------------------
        # 2. Seed Categories
        # ---------------------------------------------------------------------
        print("[+] Seeding product categories...")
        categories_data = [
            ("Enterprise Hardware", "Commercial servers, enterprise workstations, and rack computing"),
            ("Consumer Electronics", "Smart accessories, wearable displays, and consumer audio gadgets"),
            ("Office Automation", "Ergonomic furniture, smart desks, and high-volume laser printers"),
            ("Cloud & Network Gear", "Managed gigabit switches, routers, firewalls, and WiFi 6 access points"),
            ("Storage & Peripherals", "NVMe SSD arrays, external backup drives, and mechanical keyboards"),
            ("Software Licenses", "Annual SaaS seats, database diagnostic tools, and OS licenses")
        ]

        cat_objs = []
        for name, desc in categories_data:
            cat = Category.query.filter_by(category_name=name).first()
            if not cat:
                cat = Category(category_name=name, description=desc)
                db.session.add(cat)
                db.session.flush()
            cat_objs.append(cat)
        db.session.commit()
        print(f"    Categories verified: {len(cat_objs)} categories.")

        # ---------------------------------------------------------------------
        # 3. Seed Products (25 realistic products across categories)
        # ---------------------------------------------------------------------
        print("[+] Seeding catalog products...")
        products_data = [
            # Enterprise Hardware (Index 0)
            ("Titan Xeon Workstation Pro", 0, "PRD-SRV-101", Decimal("2850.00"), Decimal("1950.00"), 18, 5, "Active"),
            ("Edge Blade Micro Server 2U", 0, "PRD-SRV-102", Decimal("3400.00"), Decimal("2400.00"), 12, 4, "Active"),
            ("Apex Tower Server X8", 0, "PRD-SRV-103", Decimal("4200.00"), Decimal("3100.00"), 8, 3, "Active"),
            ("Rackmount Precision Chassis", 0, "PRD-SRV-104", Decimal("850.00"), Decimal("520.00"), 24, 6, "Active"),

            # Consumer Electronics (Index 1)
            ("Aura Pro ANC Headset", 1, "PRD-ELC-201", Decimal("249.99"), Decimal("140.00"), 65, 15, "Active"),
            ("Vivid 4K Conference Cam", 1, "PRD-ELC-202", Decimal("380.00"), Decimal("220.00"), 30, 8, "Active"),
            ("Omni Beam Smart Projector", 1, "PRD-ELC-203", Decimal("699.00"), Decimal("450.00"), 14, 5, "Active"),
            ("SyncSmart Studio Microphone", 1, "PRD-ELC-204", Decimal("179.50"), Decimal("95.00"), 42, 10, "Active"),

            # Office Automation (Index 2)
            ("AeroLift Dual-Motor Sit-Stand Desk", 2, "PRD-OFC-301", Decimal("599.00"), Decimal("360.00"), 15, 5, "Active"),
            ("ErgoMesh Executive Lumbar Chair", 2, "PRD-OFC-302", Decimal("420.00"), Decimal("250.00"), 22, 6, "Active"),
            ("WorkForce Multi-Function Color Laser", 2, "PRD-OFC-303", Decimal("890.00"), Decimal("580.00"), 9, 4, "Active"),
            ("Acoustic Privacy Desk Divider", 2, "PRD-OFC-304", Decimal("120.00"), Decimal("65.00"), 35, 8, "Active"),

            # Cloud & Network Gear (Index 3)
            ("Nexus 24-Port Managed PoE Switch", 3, "PRD-NET-401", Decimal("720.00"), Decimal("460.00"), 28, 8, "Active"),
            ("Fortress Unified Security Gateway", 3, "PRD-NET-402", Decimal("1150.00"), Decimal("780.00"), 11, 4, "Active"),
            ("WaveMesh WiFi-6 Enterprise AP", 3, "PRD-NET-403", Decimal("310.00"), Decimal("180.00"), 50, 12, "Active"),
            ("FiberLink 10G SFP+ Transceiver 4-Pack", 3, "PRD-NET-404", Decimal("210.00"), Decimal("115.00"), 45, 10, "Active"),

            # Storage & Peripherals (Index 4)
            ("HyperDrive 4TB PCIe 4.0 NVMe SSD", 4, "PRD-STR-501", Decimal("320.00"), Decimal("190.00"), 40, 10, "Active"),
            ("DataVault 24TB 4-Bay NAS Enclosure", 4, "PRD-STR-502", Decimal("899.00"), Decimal("620.00"), 10, 3, "Active"),
            ("ProKey Wireless Mechanical Keyboard", 4, "PRD-STR-503", Decimal("159.00"), Decimal("85.00"), 55, 15, "Active"),
            ("UltraGlide Ergonomic Precision Mouse", 4, "PRD-STR-504", Decimal("89.99"), Decimal("42.00"), 70, 20, "Active"),
            ("Dual 4K Thunderbolt 4 Docking Station", 4, "PRD-STR-505", Decimal("280.00"), Decimal("165.00"), 25, 6, "Active"),

            # Software Licenses (Index 5)
            ("Analytics Suite Enterprise Annual Seat", 5, "PRD-SFT-601", Decimal("1450.00"), Decimal("650.00"), 100, 10, "Active"),
            ("ZeroTrust Endpoint Security 10-Seat Pack", 5, "PRD-SFT-602", Decimal("980.00"), Decimal("420.00"), 80, 10, "Active"),
            ("DB Sentinel Monitoring Pro (1-Yr)", 5, "PRD-SFT-603", Decimal("750.00"), Decimal("310.00"), 90, 10, "Active"),
            ("Legacy ERP Connector Module", 5, "PRD-SFT-604", Decimal("450.00"), Decimal("180.00"), 4, 8, "Active") # Intentionally low stock
        ]

        prod_objs = []
        for name, c_idx, sku, price, cost, stock, reorder, status in products_data:
            p = Product.query.filter_by(SKU=sku).first()
            if not p:
                p = Product(
                    product_name=name,
                    category_id=cat_objs[c_idx].category_id,
                    SKU=sku,
                    unit_price=price,
                    unit_cost=cost,
                    stock_quantity=stock,
                    reorder_level=reorder,
                    product_status=status
                )
                db.session.add(p)
                db.session.flush()
            prod_objs.append(p)
        db.session.commit()
        print(f"    Products verified: {len(prod_objs)} items in catalog.")

        # ---------------------------------------------------------------------
        # 4. Seed Customers (60 realistic business accounts)
        # ---------------------------------------------------------------------
        print("[+] Seeding customer accounts...")
        cities_states = [
            ("New York", "NY"), ("San Francisco", "CA"), ("Austin", "TX"),
            ("Chicago", "IL"), ("Seattle", "WA"), ("Boston", "MA"),
            ("Atlanta", "GA"), ("Denver", "CO"), ("Miami", "FL"),
            ("Dallas", "TX"), ("San Jose", "CA"), ("Phoenix", "AZ")
        ]
        segments = ["Enterprise", "SMB", "Retail", "Wholesale"]
        first_names = ["Apex", "Vertex", "Summit", "Nexus", "Pinnacle", "Quantum", "Cyber", "Vanguard", "Horizon", "Catalyst", "Beacon", "Omega", "Sterling", "Paramount", "Starlight", "Core", "Strata", "Aero", "Synapse", "BlueShift"]
        last_names = ["Technologies", "Logistics", "Enterprises", "Systems", "Healthcare", "Consulting", "Ventures", "Digital", "Media", "Analytics", "Networks", "Solutions", "Capital", "Holdings", "Labs"]

        cust_objs = []
        if Customer.query.count() < 40:
            for i in range(1, 65):
                name = f"{random.choice(first_names)} {random.choice(last_names)} {random.choice(['Inc', 'LLC', 'Corp', 'Group'])}"
                city, state = random.choice(cities_states)
                seg = random.choices(segments, weights=[0.25, 0.45, 0.20, 0.10])[0]
                days_ago = random.randint(120, 500)
                reg_date = (datetime.now() - timedelta(days=days_ago)).date()
                
                cust = Customer(
                    customer_name=name,
                    email=f"procurement{i}@{name.split()[0].lower()}corp.internal",
                    phone=f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                    city=city,
                    state=state,
                    customer_segment=seg,
                    registration_date=reg_date
                )
                db.session.add(cust)
                cust_objs.append(cust)
            db.session.commit()
        else:
            cust_objs = Customer.query.all()
        print(f"    Customers verified: {len(cust_objs)} accounts.")

        # ---------------------------------------------------------------------
        # 5. Seed Orders and Order Items (240+ orders over 14 months)
        # ---------------------------------------------------------------------
        print("[+] Seeding historical and recent orders...")
        if Order.query.count() < 150:
            now = datetime.now()
            order_statuses = ["Completed", "Completed", "Completed", "Completed", "Completed", "Pending", "Processing", "Cancelled", "Returned"]
            payment_methods = ["Credit Card", "Bank Transfer", "UPI/Net Banking", "Cash on Delivery"]
            
            # Generate spread across 14 months
            total_orders_to_create = 240
            for i in range(total_orders_to_create):
                # Spread distribution with monthly variations & seasonal spikes (e.g. Q4 or mid-year)
                days_offset = random.randint(3, 420)
                order_dt = now - timedelta(days=days_offset, hours=random.randint(1, 23), minutes=random.randint(1, 59))
                
                cust = random.choice(cust_objs)
                status = random.choice(order_statuses)
                
                if status == "Completed":
                    pay_status = "Paid"
                elif status in ["Pending", "Processing"]:
                    pay_status = random.choice(["Paid", "Pending"])
                elif status == "Cancelled":
                    pay_status = random.choice(["Failed", "Refunded", "Pending"])
                elif status == "Returned":
                    pay_status = "Refunded"
                else:
                    pay_status = "Paid"

                order = Order(
                    customer_id=cust.customer_id,
                    order_date=order_dt,
                    order_status=status,
                    payment_status=pay_status,
                    payment_method=random.choice(payment_methods),
                    created_by=user_objs["sales1"].user_id if random.random() > 0.4 else user_objs["sales2"].user_id
                )
                db.session.add(order)
                db.session.flush()

                # Add 1 to 4 items per order
                num_items = random.randint(1, 4)
                chosen_products = random.sample(prod_objs, num_items)
                
                for prod in chosen_products:
                    # Quantity dependent on segment
                    if cust.customer_segment == "Enterprise":
                        qty = random.randint(2, 6)
                    elif cust.customer_segment == "Wholesale":
                        qty = random.randint(4, 10)
                    else:
                        qty = random.randint(1, 3)

                    # Snapshot prices
                    price_at_sale = prod.unit_price
                    cost_at_sale = prod.unit_cost
                    
                    # Occasional line discount (0%, 5%, 10%)
                    discount = Decimal("0.00")
                    if random.random() < 0.25:
                        discount = (price_at_sale * Decimal(qty) * Decimal(random.choice(["0.05", "0.10"]))).quantize(Decimal("0.01"))

                    item = OrderItem(
                        order_id=order.order_id,
                        product_id=prod.product_id,
                        quantity=qty,
                        unit_price_at_sale=price_at_sale,
                        unit_cost_at_sale=cost_at_sale,
                        discount_amount=discount
                    )
                    db.session.add(item)
            
            db.session.commit()
        print(f"    Orders verified: {Order.query.count()} orders with {OrderItem.query.count()} line items.")

        # ---------------------------------------------------------------------
        # 6. Seed Sales Targets across 14 months
        # ---------------------------------------------------------------------
        print("[+] Seeding monthly and category sales targets...")
        current_year = datetime.now().year
        # Generate monthly target records for past 12 months up to current month
        target_months = []
        for m in range(1, 13):
            target_months.append(f"{current_year-1}-{m:02d}")
        for m in range(1, datetime.now().month + 2):
            target_months.append(f"{current_year}-{m:02d}")

        created_by_user = user_objs["manager"].user_id
        for period in target_months:
            # Overall monthly target
            existing_monthly = SalesTarget.query.filter_by(
                target_period=period, target_type="Monthly Revenue", category_id=None
            ).first()
            if not existing_monthly:
                # Target around 40,000 - 65,000 per month
                target_amt = Decimal(random.randint(40, 65) * 1000)
                st = SalesTarget(
                    target_period=period,
                    target_type="Monthly Revenue",
                    category_id=None,
                    target_amount=target_amt,
                    created_by=created_by_user
                )
                db.session.add(st)

            # Category specific targets for key categories
            for cat in cat_objs[:3]:
                existing_cat_target = SalesTarget.query.filter_by(
                    target_period=period, target_type="Category Revenue", category_id=cat.category_id
                ).first()
                if not existing_cat_target:
                    cat_amt = Decimal(random.randint(10, 25) * 1000)
                    st_cat = SalesTarget(
                        target_period=period,
                        target_type="Category Revenue",
                        category_id=cat.category_id,
                        target_amount=cat_amt,
                        created_by=created_by_user
                    )
                    db.session.add(st_cat)

        db.session.commit()
        print(f"    Sales targets verified: {SalesTarget.query.count()} targets.")

        # Ensure MySQL view exists
        try:
            db.session.execute(db.text("""
                CREATE OR REPLACE VIEW `vw_completed_sales_items` AS
                SELECT 
                    oi.order_item_id,
                    o.order_id,
                    o.order_date,
                    o.customer_id,
                    c.customer_name,
                    c.customer_segment,
                    c.city,
                    c.state,
                    p.product_id,
                    p.product_name,
                    p.category_id,
                    cat.category_name,
                    oi.quantity,
                    oi.unit_price_at_sale,
                    oi.unit_cost_at_sale,
                    oi.discount_amount,
                    ((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS line_revenue,
                    (oi.quantity * oi.unit_cost_at_sale) AS line_cogs,
                    (((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) - (oi.quantity * oi.unit_cost_at_sale)) AS line_gross_profit
                FROM `orders` o
                JOIN `customers` c ON o.customer_id = c.customer_id
                JOIN `order_items` oi ON o.order_id = oi.order_id
                JOIN `products` p ON oi.product_id = p.product_id
                JOIN `categories` cat ON p.category_id = cat.category_id
                WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid';
            """))
            db.session.commit()
            print("    Analytical view `vw_completed_sales_items` verified.")
        except Exception as e:
            print(f"    Notice: View creation skipped or handled by schema: {e}")

        print("[OK] Database initialization and seed completed successfully!")

if __name__ == "__main__":
    drop = "--drop" in sys.argv
    seed_database(drop_all=drop)
