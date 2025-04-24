from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.utils import User
from app.utils.db import execute_query

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('community.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Validate form data
        if not all([email, password, confirm_password, first_name, last_name, phone]):
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user_id = User.create_user(email, password, first_name, last_name, phone)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('community.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Validate form data
        if not all([email, password]):
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html')
        
        # Check if user exists
        user_data = User.get_by_email(email)
        if not user_data or not User.verify_password(user_data['password'], password):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
        
        # Create user object and log in
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            is_admin=user_data['is_admin'],
            is_approved=user_data['is_approved'],
            referral_code=user_data['referral_code']
        )
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('community.dashboard'))
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Update user profile
        query = """
        UPDATE users
        SET first_name = %s, last_name = %s, phone = %s
        WHERE id = %s
        """
        execute_query(query, (first_name, last_name, phone, current_user.id), fetch=False)
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    # Get user's community memberships
    query = """
    SELECT c.id, c.name, cm.flat_no, cm.floor_no, cm.is_rented
    FROM communities c
    JOIN community_members cm ON c.id = cm.community_id
    WHERE cm.user_id = %s
    """
    communities = execute_query(query, (current_user.id,))
    
    return render_template('auth/profile.html', communities=communities)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('auth/change_password.html')
        
        # Check current password
        user_data = User.get_by_email(current_user.email)
        if not User.verify_password(user_data['password'], current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(new_password)
        
        query = """
        UPDATE users
        SET password = %s
        WHERE id = %s
        """
        execute_query(query, (hashed_password, current_user.id), fetch=False)
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')