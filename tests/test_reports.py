import pytest

def test_all_report_views(manager_client):
    report_types = [
        'monthly_sales',
        'product_performance',
        'category_revenue',
        'customer_sales',
        'profitability',
        'inventory',
        'sales_targets'
    ]
    for r_type in report_types:
        response = manager_client.get(f'/reports/?report_type={r_type}')
        assert response.status_code == 200, f"Report {r_type} crashed with status {response.status_code}"
        assert b'Report Records:' in response.data or b'table' in response.data

def test_all_csv_exports(manager_client):
    report_types = [
        'monthly_sales',
        'product_performance',
        'category_revenue',
        'customer_sales',
        'profitability',
        'inventory',
        'sales_targets'
    ]
    for r_type in report_types:
        response = manager_client.get(f'/reports/?report_type={r_type}&export=1')
        assert response.status_code == 200, f"CSV Export {r_type} crashed with status {response.status_code}"
        assert response.content_type.startswith('text/csv')
        assert 'attachment;filename=' in response.headers.get('Content-Disposition', '')
        assert len(response.data) > 0
