from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.utils.db import execute_query
import os
from werkzeug.utils import secure_filename
from datetime import datetime

payments = Blueprint('payments', __name__)

@payments.route('/payments/<int:community_id>')
@login_required
def view_payments(community_id):
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
    
    # Get user's pending payments
    query = """
    SELECT *
    FROM maintenance_payments
    WHERE community_id = %s AND user_id = %s AND payment_status = 'pending'
    ORDER BY month DESC
    """
    pending_payments = execute_query(query, (community_id, current_user.id))
    
    # Get user's completed payments
    query = """
    SELECT *
    FROM maintenance_payments
    WHERE community_id = %s AND user_id = %s AND payment_status = 'completed'
    ORDER BY payment_date DESC
    """
    completed_payments = execute_query(query, (community_id, current_user.id))
    
    # Check if user is admin
    is_admin = current_user.is_admin
    
    # If admin, get all payments
    if is_admin:
        query = """
        SELECT mp.*, u.first_name, u.last_name
        FROM maintenance_payments mp
        JOIN users u ON mp.user_id = u.id
        WHERE mp.community_id = %s
        ORDER BY mp.payment_status ASC, mp.month DESC
        """
        all_payments = execute_query(query, (community_id,))
    else:
        all_payments = []
    
    return render_template(
        'payments/view.html',
        pending_payments=pending_payments,
        completed_payments=completed_payments,
        all_payments=all_payments,
        community=community,
        is_admin=is_admin
    )

@payments.route('/payments/create/<int:community_id>', methods=['GET', 'POST'])
@login_required
def create_payment(community_id):
    # Check if user is admin
    if not current_user.is_admin:
        flash('You do not have permission to create payment requests', 'danger')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    if request.method == 'POST':
        month = request.form.get('month')
        amount = request.form.get('amount')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            flash('Invalid amount', 'danger')
            return render_template('payments/create.html', community_id=community_id)
        
        # Get all community members
        query = """
        SELECT user_id
        FROM community_members
        WHERE community_id = %s
        """
        members = execute_query(query, (community_id,))
        
        # Create payment requests for all members
        for member in members:
            # Check if payment request already exists
            query = """
            SELECT COUNT(*) as count
            FROM maintenance_payments
            WHERE community_id = %s AND user_id = %s AND month = %s
            """
            result = execute_query(query, (community_id, member['user_id'], month))
            
            if result[0]['count'] == 0:
                # Create payment request
                query = """
                INSERT INTO maintenance_payments (community_id, user_id, amount, month)
                VALUES (%s, %s, %s, %s)
                """
                payment_id = execute_query(query, (community_id, member['user_id'], amount, month), fetch=False)
                
                # Create notification
                query = """
                INSERT INTO notifications (user_id, title, content, notification_type, reference_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (
                    member['user_id'],
                    'New Maintenance Payment',
                    f'Maintenance payment of ₹{amount:.2f} for {month} is due.',
                    'payment',
                    payment_id
                )
                execute_query(query, params, fetch=False)
        
        flash('Payment requests created successfully', 'success')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    return render_template('payments/create.html', community=community)

@payments.route('/payments/pay/<int:payment_id>/<int:community_id>', methods=['GET', 'POST'])
@login_required
def pay_maintenance(payment_id, community_id):
    # Check if payment belongs to user
    query = """
    SELECT *
    FROM maintenance_payments
    WHERE id = %s AND user_id = %s
    """
    payment = execute_query(query, (payment_id, current_user.id))
    
    if not payment:
        flash('Payment not found or does not belong to you', 'danger')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    payment = payment[0]
    
    if payment['payment_status'] == 'completed':
        flash('This payment has already been completed', 'info')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    if request.method == 'POST':
        # In a real application, this would integrate with a payment gateway
        # For demo purposes, we'll just mark it as paid
        
        # Update payment status
        query = """
        UPDATE maintenance_payments
        SET payment_status = 'completed', payment_date = NOW()
        WHERE id = %s
        """
        execute_query(query, (payment_id,), fetch=False)
        
        # Generate receipt
        receipt_filename = f"receipt_{payment_id}_{current_user.id}.pdf"
        receipt_path = os.path.join('uploads', 'receipts', receipt_filename)
        
        # In a real application, this would generate a PDF receipt
        # For demo purposes, we'll just store the path
        
        # Update receipt path
        query = """
        UPDATE maintenance_payments
        SET receipt_path = %s
        WHERE id = %s
        """
        execute_query(query, (receipt_path, payment_id), fetch=False)
        
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
                'Payment Received',
                f'Maintenance payment of ₹{payment["amount"]:.2f} for {payment["month"]} received from {current_user.full_name}.',
                'payment',
                payment_id
            )
            execute_query(query, params, fetch=False)
        
        flash('Payment completed successfully', 'success')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    return render_template('payments/pay.html', payment=payment, community=community)

@payments.route('/payments/receipt/<int:payment_id>/<int:community_id>')
@login_required
def view_receipt(payment_id, community_id):
    # Check if payment belongs to user or user is admin
    query = """
    SELECT mp.*, u.first_name, u.last_name
    FROM maintenance_payments mp
    JOIN users u ON mp.user_id = u.id
    WHERE mp.id = %s AND (mp.user_id = %s OR %s = TRUE)
    """
    payment = execute_query(query, (payment_id, current_user.id, current_user.is_admin))
    
    if not payment:
        flash('Receipt not found or you do not have permission to view it', 'danger')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    payment = payment[0]
    
    if payment['payment_status'] != 'completed':
        flash('This payment has not been completed yet', 'info')
        return redirect(url_for('payments.view_payments', community_id=community_id))
    
    # Get community details
    query = """
    SELECT *
    FROM communities
    WHERE id = %s
    """
    community = execute_query(query, (community_id,))[0]
    
    return render_template('payments/receipt.html', payment=payment, community=community)