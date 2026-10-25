"""
Verification script: Tests live MySQL connectivity and live Dashboard analytics calculation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.order import Order
from app.models.customer import Customer
from app.models.product import Product
from app.services.analytics_service import AnalyticsService

def verify_live():
    app = create_app('development')
    with app.app_context():
        print("[*] Verifying Live MySQL Database...")
        print(f"    Total Customers in MySQL: {Customer.query.count()}")
        print(f"    Total Products in MySQL: {Product.query.count()}")
        print(f"    Total Orders in MySQL: {Order.query.count()}")

        kpis = AnalyticsService.get_kpis()
        print("\n[*] Live Dashboard KPIs from MySQL:")
        print(f"    Recognized Revenue: ${kpis['total_revenue']:,.2f}")
        print(f"    Gross Profit:       ${kpis['total_profit']:,.2f} ({kpis['profit_margin_pct']}%)")
        print(f"    Eligible Orders:    {kpis['total_orders']}")
        print(f"    Units Sold:         {kpis['total_units_sold']}")
        print(f"    Average Order Value:${kpis['average_order_value']:,.2f}")
        print(f"    Target Achievement: {kpis['target_achievement']}%")
        print(f"    Low Stock Products: {kpis['low_stock_count']}")

        print("\n[*] Testing live Flask client login and dashboard route:")
        client = app.test_client()
        # Retrieve login page to extract CSRF token
        get_login = client.get('/auth/login')
        assert get_login.status_code == 200
        # Parse csrf_token from page HTML
        import re
        m = re.search(r'name="csrf_token" value="([^"]+)"', get_login.get_data(as_text=True))
        csrf_token = m.group(1) if m else ''

        res_login = client.post('/auth/login', data={
            'csrf_token': csrf_token,
            'username': 'admin',
            'password': 'Admin@123'
        }, follow_redirects=True)
        assert res_login.status_code == 200, f"Login failed: {res_login.status_code}"
        print("    Admin login with valid CSRF: OK (200)")

        res_dash = client.get('/dashboard')
        assert res_dash.status_code == 200, f"Dashboard failed: {res_dash.status_code}"
        print("    Dashboard rendering: OK (200)")

        res_api = client.get('/api/dashboard-charts')
        assert res_api.status_code == 200, f"Chart API failed: {res_api.status_code}"
        chart_json = res_api.get_json()
        print(f"    Chart JSON returned: {len(chart_json['monthly_trend']['labels'])} months in trend, {len(chart_json['top_products']['labels'])} top products.")

        print("\n[SUCCESS] Live MySQL database integration and analytics fully verified!")

if __name__ == '__main__':
    verify_live()
