from flask import Flask, render_template, jsonify, session
from flask_login import login_user
from app import app
from models import User

@app.route('/test_tabs')
def test_tabs():
    # Auto-login for testing
    user = User.query.filter_by(username='testuser').first()
    if user:
        login_user(user)
        session['user_id'] = user.id
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, port=5001)