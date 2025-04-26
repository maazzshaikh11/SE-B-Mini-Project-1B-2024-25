from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.db import execute_query
from datetime import datetime

complaints = Blueprint('complaints', __name__)

@complaints.route('/complaints/<int:community_id>')
@login_required
def view_complaints(community_id):
    # Check if user is a member of the community
    query = """
    SELECT COUNT(*) as count
    FROM community_members
    WHERE user_id = %s AND community_id = %s
    """
    result = execute_query(query, (current_user.id, community_id))
    
    if result[0]['count'] == 0:
        flash('You are not a member of this community', 'danger')
        return redirect(url_for('community.dashboard'))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    # Get all complaints with upvote count
    query = """
    SELECT c.*, u.first_name, u.last_name,
           (SELECT COUNT(*) FROM complaint_upvotes WHERE complaint_id = c.id) as upvotes,
           (SELECT COUNT(*) FROM complaint_upvotes WHERE complaint_id = c.id AND user_id = %s) as user_upvoted
    FROM complaints c
    JOIN users u ON c.created_by = u.id
    WHERE c.community_id = %s
    ORDER BY c.status ASC, upvotes DESC, c.created_at DESC
    """
    complaints_list = execute_query(query, (current_user.id, community_id))
    
    # Check if user is admin
    is_admin = current_user.is_admin
    
    return render_template(
        'complaints/view.html',
        complaints=complaints_list,
        community=community,
        is_admin=is_admin
    )

@complaints.route('/complaints/create/<int:community_id>', methods=['GET', 'POST'])
@login_required
def create_complaint(community_id):
    # Check if user is a member of the community
    query = """
    SELECT COUNT(*) as count
    FROM community_members
    WHERE user_id = %s AND community_id = %s
    """
    result = execute_query(query, (current_user.id, community_id))
    
    if result[0]['count'] == 0:
        flash('You are not a member of this community', 'danger')
        return redirect(url_for('community.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Validate form data
        if not all([title, description, category]):
            flash('All fields are required', 'danger')
        else:
            # Create complaint
            query = """
            INSERT INTO complaints (community_id, title, description, category, created_by)
            VALUES (%s, %s, %s, %s, %s)
            """
            complaint_id = execute_query(query, (community_id, title, description, category, current_user.id), fetch=False)
            
            # Create notifications for admins
            query = """
            SELECT u.id
            FROM users u
            JOIN community_members cm ON u.id = cm.user_id
            WHERE cm.community_id = %s AND u.is_admin = TRUE AND u.id != %s
            """
            admins = execute_query(query, (community_id, current_user.id))
            
            for admin in admins:
                query = """
                INSERT INTO notifications (user_id, title, content, notification_type, reference_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (
                    admin['id'],
                    'New Complaint',
                    f'New complaint filed: {title}',
                    'complaint',
                    complaint_id
                )
                execute_query(query, params, fetch=False)
            
            flash('Complaint created successfully', 'success')
            return redirect(url_for('complaints.view_complaints', community_id=community_id))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    # Define complaint categories
    categories = [
        'Water Issues',
        'Electricity Issues',
        'Security Concerns',
        'Cleanliness',
        'Noise Complaints',
        'Maintenance',
        'Parking Issues',
        'Other'
    ]
    
    return render_template(
        'complaints/create.html',
        community=community,
        categories=categories
    )

@complaints.route('/complaints/upvote/<int:complaint_id>/<int:community_id>')
@login_required
def upvote_complaint(complaint_id, community_id):
    # Check if user has already upvoted
    query = """
    SELECT COUNT(*) as count
    FROM complaint_upvotes
    WHERE complaint_id = %s AND user_id = %s
    """
    result = execute_query(query, (complaint_id, current_user.id))
    
    if result[0]['count'] > 0:
        # Remove upvote
        query = """
        DELETE FROM complaint_upvotes
        WHERE complaint_id = %s AND user_id = %s
        """
        execute_query(query, (complaint_id, current_user.id), fetch=False)
        flash('Upvote removed', 'info')
    else:
        # Add upvote
        query = """
        INSERT INTO complaint_upvotes (complaint_id, user_id)
        VALUES (%s, %s)
        """
        execute_query(query, (complaint_id, current_user.id), fetch=False)
        flash('Complaint upvoted', 'success')
    
    return redirect(url_for('complaints.view_complaints', community_id=community_id))

@complaints.route('/complaints/update-status/<int:complaint_id>/<int:community_id>', methods=['POST'])
@login_required
def update_complaint_status(complaint_id, community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to update complaint status', 'danger')
        return redirect(url_for('complaints.view_complaints', community_id=community_id))
    
    status = request.form.get('status')
    
    # Update complaint status
    query = """
    UPDATE complaints
    SET status = %s
    """
    
    # If status is resolved, set resolved_at timestamp
    if status == 'resolved':
        query += ", resolved_at = NOW()"
    
    query += " WHERE id = %s"
    
    execute_query(query, (status, complaint_id), fetch=False)
    
    # Get complaint details
    query = """
    SELECT c.*, u.id as user_id
    FROM complaints c
    JOIN users u ON c.created_by = u.id
    WHERE c.id = %s
    """
    complaint = execute_query(query, (complaint_id,))[0]
    
    # Create notification for complaint creator
    query = """
    INSERT INTO notifications (user_id, title, content, notification_type, reference_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        complaint['user_id'],
        'Complaint Status Updated',
        f'Your complaint "{complaint["title"]}" has been marked as {status}.',
        'complaint',
        complaint_id
    )
    execute_query(query, params, fetch=False)
    
    flash(f'Complaint status updated to {status}', 'success')
    return redirect(url_for('complaints.view_complaints', community_id=community_id))