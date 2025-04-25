from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.utils.db import execute_query
from app.auth.utils import User
import os
from werkzeug.utils import secure_filename
from datetime import datetime

community = Blueprint('community', __name__)


@community.context_processor
def utility_processor():
    def now():
        return datetime.now()

    return dict(now=now)


@community.route('/dashboard')
@login_required
def dashboard():
    # Get user's communities
    query = """
    SELECT c.id, c.name
    FROM communities c
    JOIN community_members cm ON c.id = cm.community_id
    WHERE cm.user_id = %s
    """
    communities = execute_query(query, (current_user.id,))

    # If user has no communities, redirect to join/create page
    if not communities:
        return redirect(url_for('community.join_or_create'))

    # If user has only one community, set it as active
    if len(communities) == 1:
        active_community_id = communities[0]['id']
    else:
        # Get active community from session or use the first one
        active_community_id = request.args.get('community_id', communities[0]['id'])

    # Get community details
    query = """
    SELECT c.*, u.first_name, u.last_name
    FROM communities c
    JOIN users u ON c.created_by = u.id
    WHERE c.id = %s
    """
    community_details = execute_query(query, (active_community_id,))

    if not community_details:
        flash('Community not found', 'danger')
        return redirect(url_for('community.join_or_create'))

    community_details = community_details[0]

    # Get user's role in the community
    query = """
    SELECT is_admin
    FROM users
    WHERE id = %s
    """
    user_role = execute_query(query, (current_user.id,))[0]

    # Get recent notices
    query = """
    SELECT n.*, u.first_name, u.last_name
    FROM notices n
    JOIN users u ON n.created_by = u.id
    WHERE n.community_id = %s
    ORDER BY n.created_at DESC
    LIMIT 5
    """
    recent_notices = execute_query(query, (active_community_id,))

    # Get recent complaints
    query = """
    SELECT c.*, u.first_name, u.last_name,
           (SELECT COUNT(*) FROM complaint_upvotes WHERE complaint_id = c.id) as upvotes
    FROM complaints c
    JOIN users u ON c.created_by = u.id
    WHERE c.community_id = %s
    ORDER BY c.created_at DESC
    LIMIT 5
    """
    recent_complaints = execute_query(query, (active_community_id,))

    # Get upcoming events
    query = """
    SELECT e.*, u.first_name, u.last_name
    FROM events e
    JOIN users u ON e.created_by = u.id
    WHERE e.community_id = %s AND e.start_time > NOW()
    ORDER BY e.start_time ASC
    LIMIT 5
    """
    upcoming_events = execute_query(query, (active_community_id,))

    # Get pending maintenance payments
    query = """
    SELECT mp.*
    FROM maintenance_payments mp
    WHERE mp.community_id = %s AND mp.user_id = %s AND mp.payment_status = 'pending'
    ORDER BY mp.created_at DESC
    LIMIT 5
    """
    pending_payments = execute_query(query, (active_community_id, current_user.id))

    # Get unread notifications
    query = """
    SELECT *
    FROM notifications
    WHERE user_id = %s AND is_read = 0
    ORDER BY created_at DESC
    LIMIT 10
    """
    notifications = execute_query(query, (current_user.id,))

    return render_template(
        'community/dashboard.html',
        communities=communities,
        active_community=community_details,
        is_admin=user_role['is_admin'],
        notices=recent_notices,
        complaints=recent_complaints,
        events=upcoming_events,
        payments=pending_payments,
        notifications=notifications
    )


@community.route('/join-or-create')
@login_required
def join_or_create():
    return render_template('community/join_or_create.html')


@community.route('/create', methods=['GET', 'POST'])
@login_required
def create_community():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        flat_no = request.form.get('flat_no')
        floor_no = request.form.get('floor_no')

        # Validate form data
        if not all([name, address, flat_no, floor_no]):
            flash('All fields are required', 'danger')
            return render_template('community/create.html')

        try:
            # Create community
            query = """
            INSERT INTO communities (name, address, created_by)
            VALUES (%s, %s, %s)
            """
            community_id = execute_query(query, (name, address, current_user.id), fetch=False)

            # Add creator as a member and admin
            query = """
            INSERT INTO community_members (user_id, community_id, flat_no, floor_no)
            VALUES (%s, %s, %s, %s)
            """
            execute_query(query, (current_user.id, community_id, flat_no, floor_no), fetch=False)

            # Set user as admin
            query = """
            UPDATE users
            SET is_admin = TRUE, is_approved = TRUE
            WHERE id = %s
            """
            execute_query(query, (current_user.id,), fetch=False)

            flash('Community created successfully', 'success')
            return redirect(url_for('community.dashboard'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('community/create.html')


@community.route('/join', methods=['GET', 'POST'])
@login_required
def join_community():
    if request.method == 'POST':
        referral_code = request.form.get('referral_code')
        flat_no = request.form.get('flat_no')
        floor_no = request.form.get('floor_no')
        is_rented = 'is_rented' in request.form

        # Validate form data
        if not all([referral_code, flat_no, floor_no]):
            flash('All fields are required', 'danger')
            return render_template('community/join.html')

        # Find user by referral code
        referring_user = User.get_by_referral_code(referral_code)
        if not referring_user:
            flash('Invalid referral code', 'danger')
            return render_template('community/join.html')

        # Get community of referring user
        query = """
        SELECT community_id
        FROM community_members
        WHERE user_id = %s
        """
        result = execute_query(query, (referring_user.id,))

        if not result:
            flash('Referring user is not a member of any community', 'danger')
            return render_template('community/join.html')

        community_id = result[0]['community_id']

        # Check if user is already a member
        query = """
        SELECT COUNT(*) as count
        FROM community_members
        WHERE user_id = %s AND community_id = %s
        """
        result = execute_query(query, (current_user.id, community_id))

        if result[0]['count'] > 0:
            flash('You are already a member of this community', 'danger')
            return render_template('community/join.html')

        # Add user as a member (pending approval)
        query = """
        INSERT INTO community_members (user_id, community_id, flat_no, floor_no, is_rented)
        VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(query, (current_user.id, community_id, flat_no, floor_no, is_rented), fetch=False)

        # If rented, handle lease details
        if is_rented:
            lease_start = request.form.get('lease_start')
            lease_end = request.form.get('lease_end')

            if not all([lease_start, lease_end]):
                flash('Lease details are required for rented properties', 'warning')
            else:
                # Update lease details
                query = """
                UPDATE community_members
                SET lease_start_date = %s, lease_end_date = %s
                WHERE user_id = %s AND community_id = %s
                """
                execute_query(query, (lease_start, lease_end, current_user.id, community_id), fetch=False)

            # Handle rental agreement upload
            if 'rental_agreement' in request.files:
                file = request.files['rental_agreement']
                if file.filename:
                    filename = secure_filename(f"{current_user.id}_{community_id}_{file.filename}")
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'agreements', filename)

                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    file.save(file_path)

                    # Update file path in database
                    query = """
                    UPDATE community_members
                    SET rental_agreement_path = %s
                    WHERE user_id = %s AND community_id = %s
                    """
                    relative_path = os.path.join('uploads', 'agreements', filename)
                    execute_query(query, (relative_path, current_user.id, community_id), fetch=False)

        flash('Community join request submitted. Waiting for admin approval.', 'success')
        return redirect(url_for('community.dashboard'))

    return render_template('community/join.html')


@community.route('/members/<int:community_id>')
@login_required
def members(community_id):
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
    community_details = execute_query(query, (community_id,))[0]

    # Get all members
    query = """
    SELECT u.id, u.first_name, u.last_name, u.email, u.phone, u.is_admin, u.is_approved,
           cm.flat_no, cm.floor_no, cm.is_rented, cm.lease_start_date, cm.lease_end_date
    FROM users u
    JOIN community_members cm ON u.id = cm.user_id
    WHERE cm.community_id = %s
    ORDER BY u.is_admin DESC, cm.flat_no ASC
    """
    members = execute_query(query, (community_id,))

    # Check if user is admin
    is_admin = current_user.is_admin

    return render_template(
        'community/members.html',
        community=community_details,
        members=members,
        is_admin=is_admin
    )


@community.route('/approve-member/<int:user_id>/<int:community_id>')
@login_required
def approve_member(user_id, community_id):
    # Check if current user is admin
    if not current_user.is_admin:
        flash('You do not have permission to approve members', 'danger')
        return redirect(url_for('community.members', community_id=community_id))

    # Approve the member
    query = """
    UPDATE users
    SET is_approved = TRUE
    WHERE id = %s
    """
    execute_query(query, (user_id,), fetch=False)

    # Create notification for the approved user
    query = """
    INSERT INTO notifications (user_id, title, content, notification_type, reference_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        user_id,
        'Membership Approved',
        'Your community membership has been approved.',
        'community',
        community_id
    )
    execute_query(query, params, fetch=False)

    flash('Member approved successfully', 'success')
    return redirect(url_for('community.members', community_id=community_id))


@community.route('/family-members/<int:community_id>', methods=['GET', 'POST'])
@login_required
def family_members(community_id):
    # Check if user is a member of the community
    query = """
    SELECT id
    FROM community_members
    WHERE user_id = %s AND community_id = %s
    """
    result = execute_query(query, (current_user.id, community_id))

    if not result:
        flash('You are not a member of this community', 'danger')
        return redirect(url_for('community.dashboard'))

    community_member_id = result[0]['id']

    if request.method == 'POST':
        name = request.form.get('name')
        relationship = request.form.get('relationship')
        age = request.form.get('age')

        # Validate form data
        if not all([name, relationship]):
            flash('Name and relationship are required', 'danger')
        else:
            # Add family member
            query = """
            INSERT INTO family_members (community_member_id, name, relationship, age)
            VALUES (%s, %s, %s, %s)
            """
            execute_query(query, (community_member_id, name, relationship, age or None), fetch=False)

            flash('Family member added successfully', 'success')

    # Get family members
    query = """
    SELECT *
    FROM family_members
    WHERE community_member_id = %s
    """
    family_members = execute_query(query, (community_member_id,))

    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]

    return render_template(
        'community/family_members.html',
        family_members=family_members,
        community=community
    )


@community.route('/delete-family-member/<int:family_member_id>/<int:community_id>')
@login_required
def delete_family_member(family_member_id, community_id):
    # Check if user owns this family member
    query = """
    SELECT fm.*
    FROM family_members fm
    JOIN community_members cm ON fm.community_member_id = cm.id
    WHERE fm.id = %s AND cm.user_id = %s
    """
    result = execute_query(query, (family_member_id, current_user.id))

    if not result:
        flash('You do not have permission to delete this family member', 'danger')
        return redirect(url_for('community.family_members', community_id=community_id))

    # Delete family member
    query = """
    DELETE FROM family_members
    WHERE id = %s
    """
    execute_query(query, (family_member_id,), fetch=False)

    flash('Family member deleted successfully', 'success')
    return redirect(url_for('community.family_members', community_id=community_id))


@community.route('/emergency-contacts/<int:community_id>', methods=['GET', 'POST'])
@login_required
def emergency_contacts(community_id):
    # Check if user is a member of the community
    query = """
    SELECT id
    FROM community_members
    WHERE user_id = %s AND community_id = %s
    """
    result = execute_query(query, (current_user.id, community_id))

    if not result:
        flash('You are not a member of this community', 'danger')
        return redirect(url_for('community.dashboard'))

    community_member_id = result[0]['id']

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        relationship = request.form.get('relationship')

        # Validate form data
        if not all([name, phone, relationship]):
            flash('All fields are required', 'danger')
        else:
            # Add emergency contact
            query = """
            INSERT INTO emergency_contacts (community_member_id, name, phone, relationship)
            VALUES (%s, %s, %s, %s)
            """
            execute_query(query, (community_member_id, name, phone, relationship), fetch=False)

            flash('Emergency contact added successfully', 'success')

    # Get emergency contacts
    query = """
    SELECT *
    FROM emergency_contacts
    WHERE community_member_id = %s
    """
    emergency_contacts = execute_query(query, (community_member_id,))

    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]

    return render_template(
        'community/emergency_contacts.html',
        emergency_contacts=emergency_contacts,
        community=community
    )


@community.route('/delete-emergency-contact/<int:contact_id>/<int:community_id>')
@login_required
def delete_emergency_contact(contact_id, community_id):
    # Check if user owns this emergency contact
    query = """
    SELECT ec.*
    FROM emergency_contacts ec
    JOIN community_members cm ON ec.community_member_id = cm.id
    WHERE ec.id = %s AND cm.user_id = %s
    """
    result = execute_query(query, (contact_id, current_user.id))

    if not result:
        flash('You do not have permission to delete this emergency contact', 'danger')
        return redirect(url_for('community.emergency_contacts', community_id=community_id))

    # Delete emergency contact
    query = """
    DELETE FROM emergency_contacts
    WHERE id = %s
    """
    execute_query(query, (contact_id,), fetch=False)

    flash('Emergency contact deleted successfully', 'success')
    return redirect(url_for('community.emergency_contacts', community_id=community_id))
