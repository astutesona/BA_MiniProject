from datetime import date
from app.services.analytics_service import AnalyticsService

def test_kpi_calculations_and_cancelled_order_exclusion(app):
    with app.app_context():
        # In conftest fixture:
        # Order 1: Completed & Paid. 2 * 2000 - 100 = 3900 rev. Cost = 2 * 1200 = 2400. Profit = 1500.
        # Order 2: Cancelled & Refunded. 5 * 500 = 2500. Excluded!
        kpis = AnalyticsService.get_kpis()

        assert kpis['total_revenue'] == 3900.00
        assert kpis['total_profit'] == 1500.00
        assert kpis['total_orders'] == 1
        assert kpis['total_units_sold'] == 2
        assert kpis['average_order_value'] == 3900.00

def test_target_achievement_calculation(app):
    with app.app_context():
        # Target for 2026-02 is 5000.00. Revenue is 3900.00.
        # Achievement = (3900 / 5000) * 100 = 78.0%
        filters = {'month': 2, 'year': 2026}
        kpis = AnalyticsService.get_kpis(filters)
        assert kpis['target_amount'] == 5000.00
        assert kpis['target_achievement'] == 78.0

def test_category_revenue_aggregation(app):
    with app.app_context():
        cat_data = AnalyticsService.get_category_revenue()
        assert len(cat_data['labels']) > 0
        assert 'Hardware' in cat_data['labels']
        hw_idx = cat_data['labels'].index('Hardware')
        assert cat_data['revenue'][hw_idx] == 3900.00
        assert cat_data['profit'][hw_idx] == 1500.00
