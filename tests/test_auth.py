def test_login_successful(client):
    response = client.post('/auth/login', data={'username': 'admin_test', 'password': 'AdminPass123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back' in response.data or b'Dashboard' in response.data

def test_login_invalid_password(client):
    response = client.post('/auth/login', data={'username': 'admin_test', 'password': 'WrongPassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(auth_client):
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data

def test_unauthenticated_redirect(client):
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
