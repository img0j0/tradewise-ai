#!/usr/bin/env python
from flask import session
from flask_login import login_user
from app import app
from models import User
import requests

# Test login and API access
with app.app_context():
    # Get test user
    user = User.query.filter_by(username='testuser').first()
    if user:
        # Create a test client
        with app.test_client() as client:
            # Login
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            }, follow_redirects=True)
            
            print(f"Login status: {response.status_code}")
            
            # Test API endpoints
            response = client.get('/api/dashboard')
            print(f"Dashboard API status: {response.status_code}")
            if response.status_code == 200:
                print("Dashboard data received successfully")
            
            response = client.get('/api/stocks')
            print(f"Stocks API status: {response.status_code}")
            
            response = client.get('/api/alerts')
            print(f"Alerts API status: {response.status_code}")
            
            response = client.get('/api/portfolio')
            print(f"Portfolio API status: {response.status_code}")
    else:
        print("Test user not found!")