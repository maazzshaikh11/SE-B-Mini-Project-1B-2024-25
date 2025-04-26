from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.db import execute_query
from datetime import datetime

notices = Blueprint('notices', __name__)

@notices.route('/notices/<int:community_id>')
@login_required
def view_notices(community_id):
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
    
    # Get all notices
    query = """
    SELECT n.*, u.first_name, u.last_name
    FROM notices n
    JOIN users u ON n.created_by = u.id
    WHERE n.community_id = %s
    ORDER BY n.created_at DESC
    """
    notices = execute_query(query, (community_id,))
    
    # Check if user is admin
    is_admin = current_user.is_admin
    
    return render_template(
        'notices/view.html',
        notices=notices,
        community=community,
        is_admin=is_admin
    )

@notices.route('/notices/create/<int:community_id>', methods=['GET', 'POST'])
@login_required
def create_notice(community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to create notices', 'danger')
        return redirect(url_for('notices.view_notices', community_id=community_id))
    
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
        content = request.form.get('content')
        
        # Validate form data
        if not all([title, content]):
            flash('Title and content are required', 'danger')
        else:
            # Create notice
            query = """
            INSERT INTO notices (community_id, title, content, created_by)
            VALUES (%s, %s, %s, %s)
            """
            notice_id = execute_query(query, (community_id, title, content, current_user.id), fetch=False)
            
            # Create notifications for all community members
            query = """
            SELECT user_id
            FROM community_members
            WHERE community_id = %s AND user_id != %s
            """
            members = execute_query(query, (community_id, current_user.id))
            
            for member in members:
                query = """
                INSERT INTO notifications (user_id, title, content, notification_type, reference_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (
                    member['user_id'],
                    'New Notice',
                    f'New notice posted: {title}',
                    'notice',
                    notice_id
                )
                execute_query(query, params, fetch=False)
            
            flash('Notice created successfully', 'success')
            return redirect(url_for('notices.view_notices', community_id=community_id))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    return render_template('notices/create.html', community=community)

@notices.route('/notices/delete/<int:notice_id>/<int:community_id>')
@login_required
def delete_notice(notice_id, community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to delete notices', 'danger')
        return redirect(url_for('notices.view_notices', community_id=community_id))
    
    # Delete notice
    query = """
    DELETE FROM notices
    WHERE id = %s AND community_id = %s
    """
    execute_query(query, (notice_id, community_id), fetch=False)
    
    flash('Notice deleted successfully', 'success')
    return redirect(url_for('notices.view_notices', community_id=community_id))