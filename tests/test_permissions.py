from app.services.report_service import ReportService

def test_sales_employee_forbidden_from_user_management(sales_client):
    response = sales_client.get('/users/', follow_redirects=False)
    assert response.status_code == 403

def test_sales_employee_forbidden_from_product_creation(sales_client):
    response = sales_client.get('/products/create', follow_redirects=False)
    assert response.status_code == 403

def test_manager_forbidden_from_user_management(manager_client):
    response = manager_client.get('/users/', follow_redirects=False)
    assert response.status_code == 403

def test_admin_can_access_user_management(auth_client):
    response = auth_client.get('/users/', follow_redirects=False)
    assert response.status_code == 200

def test_csv_formula_injection_sanitization():
    # If a customer or product name begins with =, +, -, @, it must be escaped with a single quote
    malicious_inputs = [
        "=SUM(A1:A10)",
        "+cmd|' /C calc'!A0",
        "-2+3*cmd",
        "@SUM(B1)"
    ]
    for inp in malicious_inputs:
        sanitized = ReportService.sanitize_csv_field(inp)
        assert sanitized.startswith("'"), f"Failed to sanitize {inp}: got {sanitized}"

    safe_text = "Standard Product 100"
    assert ReportService.sanitize_csv_field(safe_text) == "Standard Product 100"
