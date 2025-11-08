
import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify,session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app
import razorpay
from extensions import db
from models import User, Category, Prompt, SavedPrompt, Sponsorship, CoinTransaction, Circle
import uuid

# SMTP config (use env vars in production)
SMTP_SENDER_EMAIL = os.environ.get('SMTP_SENDER_EMAIL', 'promptslibrary.in@gmail.com')
SMTP_SENDER_PASSWORD = os.environ.get('SMTP_SENDER_PASSWORD', 'yyvjblqqvwwpbfod')

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_live_RMas2O1baWS96w')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'pWyiHH9vjXOJmHN8EgPiwPAy')
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
app.permanent_session_lifetime = timedelta(days=7) 

@app.before_request
def check_subscription():
    if current_user.is_authenticated:
        if current_user.is_subscribed and current_user.subscription_expiry:
            print(current_user.subscription_expiry,datetime.now())
            if current_user.subscription_expiry <= datetime.utcnow():
                print("Subscription expired for user:", current_user.username)
                # Subscription expired → reset
                current_user.is_subscribed = 0
                current_user.subscription_expiry = None
                db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    category_id = request.args.get('category', type=int)
    # Sponsorships
    sponsorships = Sponsorship.query.filter(
        Sponsorship.is_active == True,
        db.or_(Sponsorship.expires_at.is_(None), Sponsorship.expires_at > datetime.utcnow())
    ).all()
    page = request.args.get('page', 1, type=int)   # default = page 1                                  # show 9 prompts at once
    per_page =28-len(sponsorships)
    categories = Category.query.all()

    query = Prompt.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    prompts = query.order_by(Prompt.id.desc()).paginate(page=page, per_page=per_page)

    return render_template(
        'gallery-pixel.html',
        prompts=prompts,
        categories=categories,
        selected_category=category_id,
        sponsorships=sponsorships
    )


@app.route('/category/<slug>')
def category_page(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 28
    sponsorships = Sponsorship.query.filter(
        Sponsorship.is_active == True,
        db.or_(Sponsorship.expires_at.is_(None), Sponsorship.expires_at > datetime.utcnow())
    ).all()
    per_page = max(1, per_page - len(sponsorships))
    prompts = Prompt.query.filter_by(category_id=category.id).order_by(Prompt.id.desc()).paginate(page=page, per_page=per_page)
    categories = Category.query.all()
    return render_template(
        'gallery-pixel.html',
        prompts=prompts,
        categories=categories,
        selected_category=category.id,
        selected_category_slug=category.slug,
        sponsorships=sponsorships
    )


@app.route('/prompts/<slug>')
def prompt_detail_by_slug(slug):
    prompt = Prompt.query.filter_by(slug=slug).first_or_404()
    is_saved = False
    in_circle = False
    can_view_prompt = False
    
    if current_user.is_authenticated:
        is_saved = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt.id).first() is not None
        in_circle = Circle.query.filter_by(user_id=current_user.id, creator_id=prompt.user_id).first() is not None
        
        if prompt.access_level == 'exclusive':
            is_creator = current_user.id == prompt.user_id
            can_view_prompt = is_creator or in_circle
        else:
            can_view_prompt = True
    else:
        can_view_prompt = prompt.access_level == 'basic'
    
    response_data = {
        'id': prompt.id,
        'slug': prompt.slug,
        'title': prompt.title,
        'description': prompt.description,
        'image_url': prompt.image_url,
        'category': prompt.category.name,
        'category_slug': prompt.category.slug,
        'creator': prompt.creator.username,
        'creator_id': prompt.creator.id,
        'creator_role': prompt.creator.user_role,
        'created_at': prompt.created_at.strftime('%B %d, %Y'),
        'creator_profile_pic': prompt.creator.profile_pic,
        'creator_instagram': prompt.creator.instagram_id,
        'is_saved': is_saved,
        'in_circle': in_circle,
        'access_level': prompt.access_level,
        'can_view_prompt': can_view_prompt,
        'can_edit': current_user.is_authenticated and prompt.user_id == current_user.id,
        'can_view_details': current_user.is_authenticated and (current_user.is_subscribed or (current_user.subscription_expiry and current_user.subscription_expiry > datetime.utcnow())),
        'can_start_trial': current_user.is_authenticated and (not current_user.is_subscribed)
    }
    
    if can_view_prompt or prompt.access_level == 'basic':
        response_data['prompt_text'] = prompt.prompt_text
    else:
        response_data['prompt_text'] = 'Join this creator\'s circle to access this exclusive prompt! (50 coins)'
    
    return jsonify(response_data)


 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['username']
        password = request.form['password']
        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()
        # print(user.is_otp_verified)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if not user.is_otp_verified:
                # Generate and send OTP automatically
                import random
                import smtplib
                from email.mime.text import MIMEText
                from datetime import datetime
                
                otp_code = str(random.randint(100000, 999999))
                user.otp_code = otp_code
                user.last_otp_sent = datetime.utcnow()
                db.session.commit()
                
                # Send OTP email
                sender_email = SMTP_SENDER_EMAIL
                sender_password = SMTP_SENDER_PASSWORD
                receiver_email = user.email
                subject = "Your OTP for Prompt Gallery Verification"
                body = f"""
                Hello {user.username},

                Your OTP for verification is: {otp_code}

                Please enter this OTP to verify your account.

                Regards,
                Prompt Gallery Team
                """
                
                try:
                    msg = MIMEText(body, 'plain')
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['Subject'] = subject
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                    server.quit()
                    flash('Please verify your OTP. We have sent a new OTP to your email.', 'info')
                except Exception as e:
                    print('OTP email send error:', e)
                    flash('Please verify your OTP. Failed to send new OTP email. Please use resend option.', 'error')
                
                return redirect(url_for('otp_verify'))
            session.permanent = True
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login-pixel.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        import re
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            flash('Username can only contain letters, numbers, and underscores!', 'error')
            return render_template('register-pixel.html')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register-pixel.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register-pixel.html')
        import random
        otp_code = str(random.randint(100000, 999999))
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            otp_code=otp_code,
            is_otp_verified=False
        )
        db.session.add(user)
        db.session.commit()

        # Send OTP email using smtplib
        import smtplib
        from email.mime.text import MIMEText
        sender_email = SMTP_SENDER_EMAIL
        sender_password = SMTP_SENDER_PASSWORD
        receiver_email = email
        subject = "Your OTP for Prompt Gallery Registration"
        body = f"""
        Hello {username},

        Your OTP for registration is: {otp_code}

        Please enter this OTP to verify your account.

        Regards,
        Prompt Gallery Team
        """
        try:
            msg = MIMEText(body, 'plain')
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            # Use SSL connection on port 465 for reliability
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            flash('Registration successful! OTP sent to your email.', 'success')
        except Exception as e:
            print('OTP email send error:', e)
            flash('Registration successful, but failed to send OTP email. Please contact support or try again.', 'error')

        login_user(user)
        return redirect(url_for('otp_verify'))
    return render_template('register-pixel.html')

@app.route('/otp_verify', methods=['GET', 'POST'])
@login_required
def otp_verify():
    error = None
    user = current_user
    if user.is_otp_verified:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.form.get('resend_otp'):
            import random
            import smtplib
            from email.mime.text import MIMEText
            otp_code = str(random.randint(100000, 999999))
            user.otp_code = otp_code
            db.session.commit()
            sender_email = SMTP_SENDER_EMAIL
            sender_password = SMTP_SENDER_PASSWORD
            receiver_email = user.email
            subject = "Your OTP for Prompt Gallery Verification"
            body = f"""
            Hello {user.username},

            Your OTP for verification is: {otp_code}

            Please enter this OTP to verify your account.

            Regards,
            Prompt Gallery Team
            """
            try:
                msg = MIMEText(body, 'plain')
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = subject
                # Use SSL connection on port 465 for reliability
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                server.quit()
                flash('OTP sent to your email.', 'success')
            except Exception as e:
                print('OTP resend error:', e)
                flash('Failed to send OTP email. Please contact support or try again.', 'error')
        else:
            otp_input = request.form.get('otp')
            if otp_input == user.otp_code:
                user.is_otp_verified = True
                user.otp_code = None
                db.session.commit()
                flash('OTP verified successfully!', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid OTP. Please try again.'
    return render_template('otp-verify-pixel.html', error=error)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            import random
            import smtplib
            from email.mime.text import MIMEText
            from datetime import datetime
            
            otp_code = str(random.randint(100000, 999999))
            user.otp_code = otp_code
            user.last_otp_sent = datetime.utcnow()
            db.session.commit()
            
            sender_email = SMTP_SENDER_EMAIL
            sender_password = SMTP_SENDER_PASSWORD
            receiver_email = user.email
            subject = "Password Reset OTP - Prompt Gallery"
            body = f"""
            Hello {user.username},

            Your OTP for password reset is: {otp_code}

            Please enter this OTP to reset your password.

            Regards,
            Prompt Gallery Team
            """
            
            try:
                msg = MIMEText(body, 'plain')
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = subject
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                server.quit()
                
                flash('OTP sent to your email. Please check your inbox.', 'success')
                return redirect(url_for('reset_password', email=email))
            except Exception as e:
                print('OTP email send error:', e)
                flash('Failed to send OTP email. Please try again.', 'error')
        else:
            flash('Email not found. Please check your email address.', 'error')
    
    return render_template('forgot-password-pixel.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email', '')
    
    if not email:
        flash('Email parameter is missing.', 'error')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        otp = request.form['otp']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not user.otp_code:
            flash('OTP has expired or is invalid. Please request a new one.', 'error')
            return redirect(url_for('forgot_password'))
        
        if otp != user.otp_code:
            flash('Invalid OTP. Please try again.', 'error')
            return render_template('reset-password-pixel.html', email=email)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset-password-pixel.html', email=email)
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.otp_code = None
        db.session.commit()
        
        flash('Password reset successful. You can now login with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset-password-pixel.html', email=email)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/add_prompt', methods=['GET', 'POST'])
@login_required
def add_prompt():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        prompt_text = request.form['prompt_text']
        category_id = request.form['category_id']
        
        # Handle image - either upload or URL
        image_url = ''
        image_source = request.form.get('image_source', 'url')
        
        if image_source == 'upload' and 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4()}{ext}"
                
                # Ensure uploads directory exists
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'prompts')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                image_url = f'/static/uploads/prompts/{unique_filename}'
            else:
                flash('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP)', 'error')
                return render_template('add_prompt-pixel.html', categories=categories)
        else:
            image_url = request.form.get('image_url', '')
        
        if not image_url:
            flash('Please provide an image URL or upload an image file', 'error')
            return render_template('add_prompt-pixel.html', categories=categories)
        
        access_level = request.form.get('access_level', 'basic')
        if access_level == 'exclusive' and current_user.user_role not in ['creator', 'admin']:
            access_level = 'basic'
        
        prompt = Prompt(
            title=title,
            description=description,
            prompt_text=prompt_text,
            image_url=image_url,
            user_id=current_user.id,
            category_id=category_id,
            access_level=access_level
        )
        
        db.session.add(prompt)
        db.session.commit()
        
        flash('Prompt added successfully!', 'success')
        return redirect(url_for('my_prompts'))
    
    return render_template('add_prompt-pixel.html', categories=categories)


@app.route('/my_prompts')
@login_required
def my_prompts():
    category_id = request.args.get('category', type=int)
    categories = Category.query.all()
    
    query = Prompt.query.filter_by(user_id=current_user.id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    prompts = query.all()
    
    return render_template('my_prompts-pixel.html', prompts=prompts[::-1], categories=categories, selected_category=category_id)


@app.route('/prompts/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_prompt_by_slug(slug):
    prompt = Prompt.query.filter_by(slug=slug).first_or_404()
    
    # Check if user owns this prompt
    if prompt.user_id != current_user.id and not current_user.is_admin:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        flash('You are not authorized to edit this prompt', 'error')
        return redirect(url_for('gallery'))
    
    if request.method == 'POST':
        # Handle image update
        image_url = prompt.image_url  # Keep existing by default
        
        # Check if new image file was uploaded
        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{uuid.uuid4()}{ext}"
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'prompts')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            image_url = f'/static/uploads/prompts/{unique_filename}'
        # Check if new image URL was provided
        elif request.form.get('new_image_url'):
            image_url = request.form.get('new_image_url')
        # Otherwise use the existing image_url from form
        elif request.form.get('image_url'):
            image_url = request.form.get('image_url')
        
        access_level = request.form.get('access_level', prompt.access_level)
        if access_level == 'exclusive' and current_user.user_role not in ['creator', 'admin']:
            access_level = 'basic'
        
        prompt.title = request.form['title']
        prompt.description = request.form['description']
        prompt.prompt_text = request.form['prompt_text']
        prompt.image_url = image_url
        prompt.category_id = request.form['category_id']
        prompt.access_level = access_level
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Prompt updated successfully'})
    
    # GET request - show edit form
    categories = Category.query.all()
    return render_template('edit_prompt-pixel.html', prompt=prompt, categories=categories)


@app.route('/edit_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def edit_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if user owns this prompt
    if prompt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    file = request.files['image_file']
    if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename
            name, ext = os.path.splitext(filename)
            unique_filename = f"{uuid.uuid4()}{ext}"
            # Ensure uploads directory exists
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'prompts')
            os.makedirs(upload_dir, exist_ok=True)
                
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
                
            image_url = f'/static/uploads/prompts/{unique_filename}'

    access_level = request.form.get('access_level', prompt.access_level)
    if access_level == 'exclusive' and current_user.user_role not in ['creator', 'admin']:
        access_level = 'basic'
    
    prompt.title = request.form['title']
    prompt.description = request.form['description']
    prompt.prompt_text = request.form['prompt_text']
    prompt.image_url = image_url if file and file.filename else request.form['image_url']
    prompt.category_id = request.form['category_id']
    prompt.access_level = access_level
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Prompt updated successfully'})


@app.route('/delete_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def delete_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if user owns this prompt
    if prompt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db.session.delete(prompt)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Prompt deleted successfully'})


@app.route('/saved_prompts')
@login_required
def saved_prompts():
    saved = db.session.query(Prompt).join(SavedPrompt).filter(SavedPrompt.user_id == current_user.id).all()
    return render_template('saved-prompts-pixel.html', prompts=saved[::-1])


@app.route('/save_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def save_prompt(prompt_id):
    # Check if already saved
    existing = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt_id).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Prompt already saved'})
    
    saved_prompt = SavedPrompt(user_id=current_user.id, prompt_id=prompt_id)
    db.session.add(saved_prompt)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Prompt saved successfully'})


@app.route('/unsave_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def unsave_prompt(prompt_id):
    saved_prompt = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt_id).first()
    
    if saved_prompt:
            db.session.delete(saved_prompt)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Prompt removed from saved'})
    
    return jsonify({'success': False, 'message': 'Prompt not found in saved'})


@app.route('/subscription',methods=['GET','POST'])
def subscription():
    if request.method=='POST':
        return render_template('subscription-pixel.html')
    return render_template('subscription-pixel.html')


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        plan = request.form.get('plan')
        amount = int(request.form.get('amount'))
        duration = int(request.form.get('duration', '1'))
        
        plan_names = {'monthly': 'Monthly', 'quarterly': 'Quarterly'}
        plan_name = plan_names.get(plan) if plan else 'Unknown'
        
        order = razorpay_client.order.create(dict(
            amount=amount*100,
            currency="INR",
            payment_capture="1"
        ))

        return render_template('payment-pixel.html', 
                                plan=plan, 
                                plan_name=plan_name,
                                amount=amount, 
                                duration=duration,
                                order_id=order['id'],
                                razorpay_key=RAZORPAY_KEY_ID)
    return redirect(url_for('subscription'))


@app.route('/process_payment')
@login_required
def process_payment():
    success = request.args.get('success') == 'true'
    plan = request.args.get('plan')
    duration = int(request.args.get('duration', 1))
    
    if success:
        # Update user subscription
        current_user.is_subscribed = True
        current_user.subscription_expiry = datetime.utcnow() + timedelta(days=30 * duration)
        db.session.commit()
        
        flash(f'Payment successful! Your subscription is now active. for {plan.capitalize()} plan', 'success')
    else:
        flash('Payment failed. Please try again.', 'error')
    
    return redirect(url_for('index'))


@app.route('/buy-coins')
@login_required
def buy_coins():
    return render_template('buy-coins-pixel.html')


@app.route('/create-coin-order', methods=['POST'])
@login_required
def create_coin_order():
    data = request.get_json()
    coin_package = data.get('package')
    
    packages = {
        '200': {'coins': 200, 'amount': 49},
        '1000': {'coins': 1000, 'amount': 199}
    }
    
    if coin_package not in packages:
        return jsonify({'error': 'Invalid package'}), 400
    
    package_info = packages[coin_package]
    
    
    try:
        order = razorpay_client.order.create({
            'amount': package_info['amount'] * 100,
            'currency': 'INR',
            'payment_capture': '1'
        })
        return jsonify({
            'orderId': order['id'],
            'amount': package_info['amount'],
            'coins': package_info['coins'],
            'razorpayKey': RAZORPAY_KEY_ID
        })
        
    except Exception as e:
        print('error',e)
        return jsonify({'error': str(e)}), 500


@app.route('/verify-coin-payment', methods=['POST'])
@login_required
def verify_coin_payment():
    data = request.get_json()
    
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        coins = int(data['coins'])
        amount = int(data['amount'])
        
        current_user.coins_balance += coins
        current_user.total_earned_coins += coins
        
        transaction = CoinTransaction(
            user_id=current_user.id,
            transaction_type='add',
            amount=coins,
            description=f'Purchased {coins} PM Coins for \u20b9{amount}'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{coins} coins added successfully!', 'newBalance': current_user.coins_balance})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/become-creator', methods=['POST'])
@login_required
def become_creator():
    CREATOR_COST = 400
    
    if current_user.user_role == 'creator' or current_user.user_role == 'admin':
        return jsonify({'success': False, 'message': 'You are already a creator!'}), 400
    
    if current_user.coins_balance < CREATOR_COST:
        return jsonify({'success': False, 'message': f'You need {CREATOR_COST} coins to become a creator. You have {current_user.coins_balance} coins.'}), 400
    
    current_user.coins_balance -= CREATOR_COST
    current_user.total_spent_coins += CREATOR_COST
    current_user.user_role = 'creator'
    
    transaction = CoinTransaction(
        user_id=current_user.id,
        transaction_type='spend',
        amount=CREATOR_COST,
        description='Upgraded to Creator status'
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Congratulations! You are now a Creator!', 'newBalance': current_user.coins_balance})


@app.route('/join-circle/<int:creator_id>', methods=['POST'])
@login_required
def join_circle(creator_id):
    CIRCLE_COST = 50
    
    if creator_id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot join your own circle!'}), 400
    
    creator = User.query.get_or_404(creator_id)
    
    if creator.user_role not in ['creator', 'admin']:
        return jsonify({'success': False, 'message': 'This user is not a creator!'}), 400
    
    existing_circle = Circle.query.filter_by(user_id=current_user.id, creator_id=creator_id).first()
    if existing_circle:
        return jsonify({'success': False, 'message': 'You are already in this circle!'}), 400
    
    if current_user.coins_balance < CIRCLE_COST:
        return jsonify({'success': False, 'message': f'You need {CIRCLE_COST} coins to join this circle. You have {current_user.coins_balance} coins.'}), 400
    
    current_user.coins_balance -= CIRCLE_COST
    current_user.total_spent_coins += CIRCLE_COST
    
    creator.coins_balance += CIRCLE_COST
    creator.total_earned_coins += CIRCLE_COST
    
    user_transaction = CoinTransaction(
        user_id=current_user.id,
        transaction_type='spend',
        amount=CIRCLE_COST,
        description=f'Joined {creator.username}\'s circle'
    )
    
    creator_transaction = CoinTransaction(
        user_id=creator.id,
        transaction_type='add',
        amount=CIRCLE_COST,
        description=f'{current_user.username} joined your circle'
    )
    
    new_circle = Circle(user_id=current_user.id, creator_id=creator_id)
    
    from models import Notification
    user_notification = Notification(
        user_id=current_user.id,
        message=f'🎉 You joined {creator.username}\'s Circle! You now have access to their exclusive content.',
        type='success'
    )
    
    creator_notification = Notification(
        user_id=creator.id,
        message=f'🎉 {current_user.username} joined your Circle! You earned {CIRCLE_COST} PM Coins.',
        type='success'
    )
    
    db.session.add(user_transaction)
    db.session.add(creator_transaction)
    db.session.add(new_circle)
    db.session.add(user_notification)
    db.session.add(creator_notification)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Successfully joined {creator.username}\'s circle!', 'newBalance': current_user.coins_balance})


@app.route('/leave-circle/<int:creator_id>', methods=['POST'])
@login_required
def leave_circle(creator_id):
    circle = Circle.query.filter_by(user_id=current_user.id, creator_id=creator_id).first()
    
    if not circle:
        return jsonify({'success': False, 'message': 'You are not in this circle!'}), 400
    
    db.session.delete(circle)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Successfully left the circle!'})


@app.route('/check-circle/<int:creator_id>')
@login_required
def check_circle(creator_id):
    is_member = Circle.query.filter_by(user_id=current_user.id, creator_id=creator_id).first() is not None
    return jsonify({'isMember': is_member})


@app.route('/my-circles')
@login_required
def my_circles():
    circles = Circle.query.filter_by(user_id=current_user.id).all()
    creators = [User.query.get(c.creator_id) for c in circles]
    return render_template('my-circles-pixel.html', circles=circles, creators=creators)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create unique filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4()}{ext}"

                # Ensure uploads directory exists
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)

                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)

                # Store relative path in database
                current_user.profile_pic = f'/static/uploads/profiles/{unique_filename}'

        # Update Instagram ID
        instagram_id = request.form.get('instagram_id', '').strip()
        current_user.instagram_id = instagram_id if instagram_id else None

        # Update bio
        bio = request.form.get('bio', '').strip()
        current_user.bio = bio if bio else None

        # Update social links
        github_url = request.form.get('github_url', '').strip()
        current_user.github_url = github_url if github_url else None

        linkedin_url = request.form.get('linkedin_url', '').strip()
        current_user.linkedin_url = linkedin_url if linkedin_url else None

        twitter_url = request.form.get('twitter_url', '').strip()
        current_user.twitter_url = twitter_url if twitter_url else None

        portfolio_url = request.form.get('portfolio_url', '').strip()
        current_user.portfolio_url = portfolio_url if portfolio_url else None

        username = request.form.get('username', '').strip()
        if current_user.username!=username:
            import re
            if not re.match(r'^[A-Za-z0-9_]+$', username):
                flash('Username can only contain letters, numbers, and underscores!', 'error')
            elif User.query.filter_by(username=username).first():
                flash('Username already exists!', 'error')
            else:
                current_user.username= username

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile-pixel.html')


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/get_prompt/<int:prompt_id>')
def get_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    is_saved = False
    
    if current_user.is_authenticated:
        is_saved = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt_id).first() is not None
    
    return jsonify({
        'id': prompt.id,
        'slug': prompt.slug,
        'title': prompt.title,
        'description': prompt.description,
        'prompt_text': prompt.prompt_text,
        'image_url': prompt.image_url,
        'category': prompt.category.name,
        'category_slug': prompt.category.slug,
        'creator': prompt.creator.username,
        'created_at': prompt.created_at.strftime('%B %d, %Y'),
        'creator_profile_pic': prompt.creator.profile_pic,
        'creator_instagram': prompt.creator.instagram_id,
        'is_saved': is_saved,
        'can_edit': current_user.is_authenticated and prompt.user_id == current_user.id,
        'can_view_details': current_user.is_authenticated and (current_user.is_subscribed or (current_user.subscription_expiry and current_user.subscription_expiry > datetime.utcnow())),
        'can_start_trial': current_user.is_authenticated and (not current_user.is_subscribed)
    })


@app.route('/upgrade_subscription', methods=['POST'])
@login_required
def upgrade_subscription():
    # In a real app, this would integrate with a payment processor
    current_user.is_subscribed = True
    db.session.commit()
    
    flash('Subscription upgraded successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/start_trial', methods=['POST'])
@login_required
def start_trial():
    # Allow a one-time 30-day free trial for each user
    if current_user.is_subscribed:
        flash('You already have an active subscription.', 'info')
        return redirect(url_for('index'))

    # Grant trial
    current_user.is_subscribed = True
    current_user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
    db.session.commit()

    flash('1-month free trial activated! Enjoy premium access for 30 days.', 'success')
    return redirect(url_for('index'))


# Admin routes
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    total_users = User.query.count()
    total_creators = User.query.filter_by(user_role='creator').count()
    total_circles = Circle.query.count()
    total_prompts = Prompt.query.count()
    exclusive_prompts = Prompt.query.filter_by(access_level='exclusive').count()
    
    total_coins_circulation = db.session.query(db.func.sum(User.coins_balance)).scalar() or 0
    total_coins_earned = db.session.query(db.func.sum(User.total_earned_coins)).scalar() or 0
    
    recent_transactions = CoinTransaction.query.order_by(CoinTransaction.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_creators': total_creators,
        'total_circles': total_circles,
        'total_prompts': total_prompts,
        'exclusive_prompts': exclusive_prompts,
        'total_coins_circulation': int(total_coins_circulation),
        'total_coins_earned': int(total_coins_earned),
        'recent_transactions': recent_transactions,
        'recent_users': recent_users
    }
    
    return render_template('admin_dashboard-pixel.html', stats=stats)


@app.route('/admin/transactions')
@login_required
def admin_transactions():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    transaction_type = request.args.get('type', None)
    
    query = CoinTransaction.query
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    transactions = query.order_by(CoinTransaction.created_at.desc()).paginate(page=page, per_page=50)
    
    total_adds = CoinTransaction.query.filter_by(transaction_type='add').count()
    total_spends = CoinTransaction.query.filter_by(transaction_type='spend').count()
    total_earns = CoinTransaction.query.filter_by(transaction_type='earn').count()
    
    return render_template('admin_transactions-pixel.html',
                         transactions=transactions,
                         total_adds=total_adds,
                         total_spends=total_spends,
                         total_earns=total_earns,
                         transaction_type=transaction_type)


@app.route('/admin/sponsorships')
@login_required
def admin_sponsorships():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    sponsorships = Sponsorship.query.order_by(Sponsorship.created_at.desc()).all()
    return render_template('admin_sponsorships-pixel.html', sponsorships=sponsorships)


@app.route('/admin/add_sponsorship', methods=['GET', 'POST'])
@login_required
def add_sponsorship():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        client_name = request.form['client_name']
        redirect_url = request.form['redirect_url']
        expires_at = request.form.get('expires_at')
        
        # Handle image - either upload or URL
        image_url = ''
        image_source = request.form.get('image_source', 'url')
        
        if image_source == 'upload' and 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4()}{ext}"
                
                # Ensure uploads directory exists
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'sponsorships')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                image_url = f'/static/uploads/sponsorships/{unique_filename}'
            else:
                flash('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP)', 'error')
                return render_template('add_sponsorship.html')
        else:
            image_url = request.form.get('image_url', '')
        
        if not image_url:
            flash('Please provide an image URL or upload an image file', 'error')
            return render_template('add_sponsorship.html')
        
        # Parse expiry date if provided
        expires_at_date = None
        if expires_at:
            try:
                expires_at_date = datetime.strptime(expires_at, '%Y-%m-%d')
            except ValueError:
                flash('Invalid expiry date format', 'error')
                return render_template('add_sponsorship.html')
        
        sponsorship = Sponsorship(
            title=title,
            description=description,
            image_url=image_url,
            client_name=client_name,
            redirect_url=redirect_url,
            expires_at=expires_at_date,
            admin_id=current_user.id
        )
        
        db.session.add(sponsorship)
        db.session.commit()
        
        flash('Sponsorship added successfully!', 'success')
        return redirect(url_for('admin_sponsorships'))
    
    return render_template('add_sponsorship.html')


@app.route('/admin/toggle_sponsorship/<int:sponsorship_id>', methods=['POST'])
@login_required
def toggle_sponsorship(sponsorship_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
    sponsorship.is_active = not sponsorship.is_active
    db.session.commit()
    
    status = 'activated' if sponsorship.is_active else 'deactivated'
    return jsonify({'success': True, 'message': f'Sponsorship {status} successfully'})


@app.route('/admin/delete_sponsorship/<int:sponsorship_id>', methods=['POST'])
@login_required
def delete_sponsorship(sponsorship_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
    db.session.delete(sponsorship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Sponsorship deleted successfully'})


@app.route('/sponsorship/<int:sponsorship_id>')
def view_sponsorship(sponsorship_id):
    sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
    
    if not sponsorship.is_active:
        flash('This sponsorship is no longer available.', 'error')
        return redirect(url_for('index'))
    
    # Check if expired
    if sponsorship.expires_at and sponsorship.expires_at < datetime.utcnow():
        flash('This sponsorship has expired.', 'error')
        return redirect(url_for('index'))
    
    return render_template('sponsorship_detail.html', sponsorship=sponsorship)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-conditions')
def terms_conditions():
    return render_template('terms-conditions.html')

@app.route('/shipping-delivery')
def shipping_delivery():
    return render_template('shipping-delivery.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

@app.route('/cancellation-refund')
def cancellation_refund():
    return render_template('cancellation-refund.html')

@app.route('/user/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    prompts = Prompt.query.filter_by(user_id=user.id).order_by(Prompt.created_at.desc()).limit(12).all()
    total_prompts = Prompt.query.filter_by(user_id=user.id).count()
    
    circle_members = []
    circle_count = 0
    if user.user_role == 'creator':
        circles = Circle.query.filter_by(creator_id=user.id).all()
        circle_count = len(circles)
        circle_members = [circle.member for circle in circles[:12]]
    
    return render_template('public_profile-pixel.html', 
                         user=user, 
                         prompts=prompts, 
                         total_prompts=total_prompts,
                         circle_members=circle_members,
                         circle_count=circle_count)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = User.query

    if search_query:
        search_filter = f'%{search_query}%'
        query = query.filter(
            (User.username.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )

    users_pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)

    total_users = User.query.count()
    subscribed_users = User.query.filter_by(is_subscribed=True).count()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_signups = User.query.filter(User.created_at >= seven_days_ago).count()

    return render_template('admin_users-pixel.html',
                         users=users_pagination,
                         total_users=total_users,
                         subscribed_users=subscribed_users,
                         recent_signups=recent_signups,
                         search_query=search_query)

@app.route('/sitemap.xml')
def sitemap():
    pages = []

    pages.append({
        'loc': url_for('index', _external=True),
        'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '1.0'
    })

    pages.append({
        'loc': url_for('subscription', _external=True),
        'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
        'changefreq': 'weekly',
        'priority': '0.8'
    })

    categories = Category.query.all()
    for category in categories:
        if category.slug:
            pages.append({
                'loc': url_for('category_page', slug=category.slug, _external=True),
                'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '0.9'
            })

    users = User.query.filter_by(is_otp_verified=True).all()
    for user in users:
        pages.append({
            'loc': url_for('public_profile', username=user.username, _external=True),
            'lastmod': user.created_at.strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.7'
        })

    # Include recent prompts by slug
    recent_prompts = Prompt.query.order_by(Prompt.created_at.desc()).limit(1000).all()
    for p in recent_prompts:
        if p.slug:
            pages.append({
                'loc': url_for('prompt_detail_by_slug', slug=p.slug, _external=True),
                'lastmod': p.created_at.strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.6'
            })

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>{page["loc"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        sitemap_xml += f'    <priority>{page["priority"]}</priority>\n'
        sitemap_xml += '  </url>\n'

    sitemap_xml += '</urlset>'

    from flask import Response
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    robots_txt = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /profile
Disallow: /saved_prompts
Disallow: /my_prompts

Sitemap: {sitemap_url}
""".format(sitemap_url=url_for('sitemap', _external=True))

    from flask import Response
    return Response(robots_txt, mimetype='text/plain')
