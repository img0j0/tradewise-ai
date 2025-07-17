#!/usr/bin/env python3
"""Direct login script to bypass browser issues"""

from app import app, db
from models import User
from flask import session
from flask_login import login_user

with app.app_context():
    # Try to login as trader1
    user = User.query.filter_by(username='trader1').first()
    if user:
        print(f"Found user: {user.username}")
        # Create a test request context
        with app.test_request_context('/'):
            login_user(user)
            print("User logged in successfully via script")
            print(f"Session: {dict(session)}")
    else:
        print("User not found!")