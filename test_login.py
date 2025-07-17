#!/usr/bin/env python3
"""Test login functionality directly"""

from app import app, db
from models import User
from flask import session

with app.app_context():
    # Check if test user exists
    user = User.query.filter_by(username='testuser').first()
    if user:
        print(f"Test user found: {user.username}")
        print(f"Password check for 'password123': {user.check_password('password123')}")
    else:
        print("Test user not found!")
        
    # Test the app with test client
    with app.test_client() as client:
        # Clear any existing session
        client.get('/logout')
        
        # Try to login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=False)
        
        print(f"\nLogin response status: {response.status_code}")
        print(f"Redirect location: {response.location}")
        print(f"Set-Cookie header: {response.headers.get('Set-Cookie')}")
        
        # Check if we're authenticated
        response = client.get('/debug-auth')
        data = response.get_json()
        print(f"\nAuthentication status after login:")
        print(f"  Authenticated: {data.get('authenticated')}")
        print(f"  Username: {data.get('username')}")
        print(f"  Session data: {data.get('session')}")