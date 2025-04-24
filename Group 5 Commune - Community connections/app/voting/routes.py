from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.db import execute_query
from datetime import datetime

voting = Blueprint('voting', __name__)


@voting.route('/polls/<int:community_id>')
@login_required
def view_polls(community_id):
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

    # Get active polls
    query = """
    SELECT p.*, u.first_name, u.last_name,
           (SELECT COUNT(DISTINCT user_id) FROM poll_votes pv JOIN poll_options po ON pv.poll_option_id = po.id WHERE po.poll_id = p.id) as vote_count,
           (SELECT COUNT(DISTINCT user_id) FROM poll_votes pv JOIN poll_options po ON pv.poll_option_id = po.id WHERE po.poll_id = p.id AND pv.user_id = %s) as user_voted
    FROM polls p
    JOIN users u ON p.created_by = u.id
    WHERE p.community_id = %s AND p.end_time > NOW()
    ORDER BY p.end_time ASC
    """
    active_polls = execute_query(query, (current_user.id, community_id))

    # Get past polls
    query = """
    SELECT p.*, u.first_name, u.last_name,
           (SELECT COUNT(DISTINCT user_id) FROM poll_votes pv JOIN poll_options po ON pv.poll_option_id = po.id WHERE po.poll_id = p.id) as vote_count
    FROM polls p
    JOIN users u ON p.created_by = u.id
    WHERE p.community_id = %s AND p.end_time <= NOW()
    ORDER BY p.end_time DESC
    """
    past_polls = execute_query(query, (community_id,))

    # Check if user is admin
    is_admin = current_user.is_admin

    return render_template(
        'voting/view.html',  # Changed from 'voting/polls.html'
        active_polls=active_polls,
        past_polls=past_polls,
        community=community,
        is_admin=is_admin
    )


@voting.route('/polls/create/<int:community_id>', methods=['GET', 'POST'])
@login_required
def create_poll(community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to create polls', 'danger')
        return redirect(url_for('voting.view_polls', community_id=community_id))

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
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        options = request.form.getlist('options[]')

        # Validate form data
        if not all([title, description, start_time, end_time]) or not options:
            flash('All fields are required and at least one option must be provided', 'danger')
        else:
            # Create poll
            query = """
            INSERT INTO polls (community_id, title, description, start_time, end_time, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            poll_id = execute_query(query, (community_id, title, description, start_time, end_time, current_user.id),
                                    fetch=False)

            # Add options
            for option in options:
                if option.strip():  # Only add non-empty options
                    query = """
                    INSERT INTO poll_options (poll_id, option_text)
                    VALUES (%s, %s)
                    """
                    execute_query(query, (poll_id, option.strip()), fetch=False)

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
                    'New Poll',
                    f'New poll created: {title}',
                    'poll',
                    poll_id
                )
                execute_query(query, params, fetch=False)

            flash('Poll created successfully', 'success')
            return redirect(url_for('voting.view_polls', community_id=community_id))

    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]

    return render_template('voting/create.html', community=community)


@voting.route('/polls/vote/<int:poll_id>/<int:community_id>', methods=['POST'])
@login_required
def vote_poll(poll_id, community_id):
    option_id = request.form.get('option_id')

    if not option_id:
        flash('Please select an option', 'danger')
        return redirect(url_for('voting.view_polls', community_id=community_id))

    # Check if poll is still active
    query = """
    SELECT COUNT(*) as count
    FROM polls
    WHERE id = %s AND start_time <= NOW() AND end_time > NOW()
    """
    result = execute_query(query, (poll_id,))

    if result[0]['count'] == 0:
        flash('This poll is not active', 'danger')
        return redirect(url_for('voting.view_polls', community_id=community_id))

    # Check if user has already voted
    query = """
    SELECT pv.id
    FROM poll_votes pv
    JOIN poll_options po ON pv.poll_option_id = po.id
    WHERE po.poll_id = %s AND pv.user_id = %s
    """
    result = execute_query(query, (poll_id, current_user.id))

    if result:
        # Update existing vote
        query = """
        UPDATE poll_votes
        SET poll_option_id = %s
        WHERE id = %s
        """
        execute_query(query, (option_id, result[0]['id']), fetch=False)
        flash('Your vote has been updated', 'success')
    else:
        # Create new vote
        query = """
        INSERT INTO poll_votes (poll_option_id, user_id)
        VALUES (%s, %s)
        """
        execute_query(query, (option_id, current_user.id), fetch=False)
        flash('Your vote has been recorded', 'success')

    return redirect(url_for('voting.view_polls', community_id=community_id))


@voting.route('/polls/results/<int:poll_id>/<int:community_id>')
@login_required
def poll_results(poll_id, community_id):
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

    # Get poll details
    query = """
    SELECT p.*, u.first_name, u.last_name
    FROM polls p
    JOIN users u ON p.created_by = u.id
    WHERE p.id = %s
    """
    poll = execute_query(query, (poll_id,))

    if not poll:
        flash('Poll not found', 'danger')
        return redirect(url_for('voting.view_polls', community_id=community_id))

    poll = poll[0]

    # Get poll options with vote counts
    query = """
    SELECT po.id, po.option_text,
           COUNT(pv.id) as vote_count
    FROM poll_options po
    LEFT JOIN poll_votes pv ON po.id = pv.poll_option_id
    WHERE po.poll_id = %s
    GROUP BY po.id
    ORDER BY vote_count DESC
    """
    options = execute_query(query, (poll_id,))

    # Get total votes
    total_votes = sum(option['vote_count'] for option in options)

    # Calculate percentages
    for option in options:
        if total_votes > 0:
            option['percentage'] = (option['vote_count'] / total_votes) * 100
        else:
            option['percentage'] = 0

    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]

    # Check if user has voted
    query = """
    SELECT po.id
    FROM poll_votes pv
    JOIN poll_options po ON pv.poll_option_id = po.id
    WHERE po.poll_id = %s AND pv.user_id = %s
    """
    user_vote = execute_query(query, (poll_id, current_user.id))

    user_voted_option = user_vote[0]['id'] if user_vote else None

    return render_template(
        'voting/results.html',  # Changed from 'voting/polls_result.html'
        poll=poll,
        options=options,
        total_votes=total_votes,
        community=community,
        user_voted_option=user_voted_option
    )


@voting.route('/polls/delete/<int:poll_id>/<int:community_id>')
@login_required
def delete_poll(poll_id, community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to delete polls', 'danger')
        return redirect(url_for('voting.view_polls', community_id=community_id))

    # Delete poll (cascade will delete options and votes)
    query = """
    DELETE FROM polls
    WHERE id = %s AND community_id = %s
    """
    execute_query(query, (poll_id, community_id), fetch=False)

    flash('Poll deleted successfully', 'success')
    return redirect(url_for('voting.view_polls', community_id=community_id))
