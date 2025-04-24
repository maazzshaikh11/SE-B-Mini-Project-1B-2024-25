from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.db import execute_query
from datetime import datetime

events = Blueprint('events', __name__)

@events.route('/events/<int:community_id>')
@login_required
def view_events(community_id):
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
    
    # Get upcoming events
    query = """
    SELECT e.*, u.first_name, u.last_name,
           (SELECT COUNT(*) FROM event_rsvps WHERE event_id = e.id AND status = 'attending') as attending_count,
           (SELECT status FROM event_rsvps WHERE event_id = e.id AND user_id = %s) as user_rsvp
    FROM events e
    JOIN users u ON e.created_by = u.id
    WHERE e.community_id = %s AND e.start_time > NOW()
    ORDER BY e.start_time ASC
    """
    upcoming_events = execute_query(query, (current_user.id, community_id))
    
    # Get past events
    query = """
    SELECT e.*, u.first_name, u.last_name,
           (SELECT COUNT(*) FROM event_rsvps WHERE event_id = e.id AND status = 'attending') as attending_count,
           (SELECT status FROM event_rsvps WHERE event_id = e.id AND user_id = %s) as user_rsvp
    FROM events e
    JOIN users u ON e.created_by = u.id
    WHERE e.community_id = %s AND e.start_time <= NOW()
    ORDER BY e.start_time DESC
    """
    past_events = execute_query(query, (current_user.id, community_id))
    
    # Check if user is admin
    is_admin = current_user.is_admin
    
    return render_template(
        'events/view.html',
        upcoming_events=upcoming_events,
        past_events=past_events,
        community=community,
        is_admin=is_admin
    )

@events.route('/events/create/<int:community_id>', methods=['GET', 'POST'])
@login_required
def create_event(community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to create events', 'danger')
        return redirect(url_for('events.view_events', community_id=community_id))
    
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
        location = request.form.get('location')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        
        # Validate form data
        if not all([title, description, location, start_time, end_time]):
            flash('All fields are required', 'danger')
        else:
            # Create event
            query = """
            INSERT INTO events (community_id, title, description, location, start_time, end_time, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            event_id = execute_query(query, (community_id, title, description, location, start_time, end_time, current_user.id), fetch=False)
            
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
                    'New Event',
                    f'New event scheduled: {title}',
                    'event',
                    event_id
                )
                execute_query(query, params, fetch=False)
            
            flash('Event created successfully', 'success')
            return redirect(url_for('events.view_events', community_id=community_id))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    return render_template('events/create.html', community=community)

@events.route('/events/rsvp/<int:event_id>/<int:community_id>', methods=['POST'])
@login_required
def rsvp_event(event_id, community_id):
    status = request.form.get('status')
    
    if not status in ['attending', 'not_attending', 'maybe']:
        flash('Invalid RSVP status', 'danger')
        return redirect(url_for('events.view_events', community_id=community_id))
    
    # Check if user already has an RSVP
    query = """
    SELECT COUNT(*) as count
    FROM event_rsvps
    WHERE event_id = %s AND user_id = %s
    """
    result = execute_query(query, (event_id, current_user.id))
    
    if result[0]['count'] > 0:
        # Update existing RSVP
        query = """
        UPDATE event_rsvps
        SET status = %s
        WHERE event_id = %s AND user_id = %s
        """
        execute_query(query, (status, event_id, current_user.id), fetch=False)
    else:
        # Create new RSVP
        query = """
        INSERT INTO event_rsvps (event_id, user_id, status)
        VALUES (%s, %s, %s)
        """
        execute_query(query, (event_id, current_user.id, status), fetch=False)
    
    flash(f'RSVP updated to {status}', 'success')
    return redirect(url_for('events.view_events', community_id=community_id))

@events.route('/events/contribute/<int:event_id>/<int:community_id>', methods=['POST'])
@login_required
def contribute_event(event_id, community_id):
    amount = request.form.get('amount')
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        flash('Invalid amount', 'danger')
        return redirect(url_for('events.view_events', community_id=community_id))
    
    # Create contribution
    query = """
    INSERT INTO event_contributions (event_id, user_id, amount)
    VALUES (%s, %s, %s)
    """
    execute_query(query, (event_id, current_user.id, amount), fetch=False)
    
    # Get event details
    query = """
    SELECT title
    FROM events
    WHERE id = %s
    """
    event = execute_query(query, (event_id,))[0]
    
    # Create notification for admins
    query = """
    SELECT u.id
    FROM users u
    JOIN community_members cm ON u.id = cm.user_id
    WHERE cm.community_id = %s AND u.is_admin = TRUE
    """
    admins = execute_query(query, (community_id,))
    
    for admin in admins:
        query = """
        INSERT INTO notifications (user_id, title, content, notification_type, reference_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            admin['id'],
            'Event Contribution',
            f'{current_user.full_name} contributed ₹{amount:.2f} to event: {event["title"]}',
            'event',
            event_id
        )
        execute_query(query, params, fetch=False)
    
    flash(f'Contribution of ₹{amount:.2f} recorded', 'success')
    return redirect(url_for('events.view_events', community_id=community_id))

@events.route('/events/delete/<int:event_id>/<int:community_id>')
@login_required
def delete_event(event_id, community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to delete events', 'danger')
        return redirect(url_for('events.view_events', community_id=community_id))
    
    # Delete event
    query = """
    DELETE FROM events
    WHERE id = %s AND community_id = %s
    """
    execute_query(query, (event_id, community_id), fetch=False)
    
    flash('Event deleted successfully', 'success')
    return redirect(url_for('events.view_events', community_id=community_id))