#!/usr/bin/env python3
"""Minimal login test to isolate the issue"""

import requests

# Create a session to maintain cookies
session = requests.Session()

print("=== Testing Login Flow ===")

# 1. Get login page
response = session.get('http://localhost:5000/login')
print(f"1. Login page status: {response.status_code}")

# 2. Submit login
login_data = {
    'username': 'testuser',
    'password': 'password123'
}
response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
print(f"2. Login POST status: {response.status_code}")
print(f"   Redirect location: {response.headers.get('Location', 'None')}")
print(f"   Cookie set: {'session' in response.cookies}")

# 3. Follow redirect
if response.status_code == 302:
    response = session.get('http://localhost:5000' + response.headers['Location'])
    print(f"3. After redirect status: {response.status_code}")

# 4. Check authentication
response = session.get('http://localhost:5000/debug-auth')
if response.status_code == 200:
    auth_data = response.json()
    print(f"4. Authentication check:")
    print(f"   Authenticated: {auth_data.get('authenticated')}")
    print(f"   Username: {auth_data.get('username')}")
    
# 5. Try accessing protected route
response = session.get('http://localhost:5000/api/dashboard')
print(f"5. Protected route status: {response.status_code}")

print("\n=== Session Cookies ===")
for cookie in session.cookies:
    print(f"   {cookie.name}: {cookie.value[:20]}... (domain: {cookie.domain}, path: {cookie.path})")