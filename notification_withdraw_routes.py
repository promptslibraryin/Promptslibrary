from app import app
from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Notification, WithdrawRequest, User, CoinTransaction
from datetime import datetime


@app.route('/api/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        } for n in notifications],
        'unread_count': Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).count()
    })


@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/notifications/clear-all', methods=['POST'])
@login_required
def clear_all_notifications():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/withdraw')
@login_required
def withdraw_page():
    withdraw_requests = WithdrawRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(WithdrawRequest.created_at.desc()).all()
    
    return render_template('withdraw-pixel.html', 
                         user=current_user,
                         withdraw_requests=withdraw_requests)


@app.route('/api/withdraw/request', methods=['POST'])
@login_required
def create_withdraw_request():
    data = request.get_json()
    
    coins = int(data.get('coins', 0))
    payment_method = data.get('payment_method', '')
    payment_details = data.get('payment_details', '')
    
    if coins < 100:
        return jsonify({'error': 'Minimum withdrawal is 100 coins'}), 400
    
    if current_user.coins_balance < coins:
        return jsonify({'error': 'Insufficient coin balance'}), 400
    
    amount = coins / 10
    
    withdraw_req = WithdrawRequest(
        user_id=current_user.id,
        coins=coins,
        amount=amount,
        payment_method=payment_method,
        payment_details=payment_details,
        status='pending'
    )
    
    db.session.add(withdraw_req)
    
    current_user.coins_balance -= coins
    current_user.total_spent_coins += coins
    
    transaction = CoinTransaction(
        user_id=current_user.id,
        transaction_type='withdraw_request',
        amount=-coins,
        description=f'Withdrawal request - {payment_method}'
    )
    db.session.add(transaction)
    
    notification = Notification(
        user_id=current_user.id,
        message=f'Withdrawal request for {coins} coins (₹{amount}) has been submitted. Processing time: 24-48 hours.',
        type='info'
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Withdrawal request submitted successfully!',
        'new_balance': current_user.coins_balance
    })


@app.route('/admin/withdrawals')
@login_required
def admin_withdrawals():
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('index'))
    
    status_filter = request.args.get('status', 'all')
    
    query = WithdrawRequest.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    withdrawals = query.order_by(WithdrawRequest.created_at.desc()).all()
    
    return render_template('admin_withdrawals-pixel.html', 
                         withdrawals=withdrawals,
                         status_filter=status_filter)


@app.route('/api/admin/withdrawal/<int:withdrawal_id>/approve', methods=['POST'])
@login_required
def approve_withdrawal(withdrawal_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    admin_note = data.get('admin_note', '')
    
    withdrawal = WithdrawRequest.query.get_or_404(withdrawal_id)
    withdrawal.status = 'approved'
    withdrawal.admin_note = admin_note
    withdrawal.updated_at = datetime.utcnow()
    
    notification = Notification(
        user_id=withdrawal.user_id,
        message=f'✅ Your withdrawal request for {withdrawal.coins} coins (₹{withdrawal.amount}) has been approved and processed!',
        type='success'
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/admin/withdrawal/<int:withdrawal_id>/reject', methods=['POST'])
@login_required
def reject_withdrawal(withdrawal_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    admin_note = data.get('admin_note', '')
    
    withdrawal = WithdrawRequest.query.get_or_404(withdrawal_id)
    withdrawal.status = 'rejected'
    withdrawal.admin_note = admin_note
    withdrawal.updated_at = datetime.utcnow()
    
    user = User.query.get(withdrawal.user_id)
    user.coins_balance += withdrawal.coins
    user.total_spent_coins -= withdrawal.coins
    
    transaction = CoinTransaction(
        user_id=withdrawal.user_id,
        transaction_type='withdraw_refund',
        amount=withdrawal.coins,
        description=f'Withdrawal request rejected - coins refunded'
    )
    db.session.add(transaction)
    
    notification = Notification(
        user_id=withdrawal.user_id,
        message=f'⚠️ Your withdrawal request for {withdrawal.coins} coins has been rejected. Coins have been refunded. Reason: {admin_note}',
        type='warning'
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({'success': True})


def create_notification(user_id, message, notification_type='info'):
    notification = Notification(
        user_id=user_id,
        message=message,
        type=notification_type
    )
    db.session.add(notification)
    db.session.commit()
