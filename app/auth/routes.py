from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, Blueprint, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth.forms import LoginForm, RegistrationForm, OTPVerificationForm
from app.models import User
import pyotp
import qrcode
import io
import base64

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        total_user = User.query.count()

        if total_user == 0:
            role = "superadmin"
        elif total_user == 1:
            role = "staf"
        else:
            role = "user"

        user = User(
            username=form.username.data,
            role=role
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'Registrasi berhasil! Akun Anda terdaftar sebagai {role}. Silakan login.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            # Check if account is locked out
            if user.lockout_until and user.lockout_until > datetime.utcnow():
                remaining_time = user.lockout_until - datetime.utcnow()
                flash(f'Akun Anda terkunci. Coba lagi setelah {int(remaining_time.total_seconds() / 60)} menit.', 'error')
                return redirect(url_for('auth.login'))

            if user.check_password(form.password.data):
                # Successful login: reset failed attempts and lockout
                user.failed_login_attempts = 0
                user.lockout_until = None
                db.session.commit()

                session['temp_user_id'] = user.id

                if user.otp_enabled:
                    return redirect(url_for('auth.verify_2fa_login'))
                else:
                    login_user(user)
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        if user.role == 'superadmin':
                            next_page = url_for('admin.dashboard')
                        elif user.role == 'admin':
                            next_page = url_for('admin.dashboard')
                        elif user.role in ['staf', 'pending']:
                            next_page = url_for('staf.dashboard')
                        else:
                            next_page = url_for('main.index')
                    return redirect(next_page)
            else:
                # Failed password: increment failed attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user.lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    flash(f'Terlalu banyak percobaan login gagal. Akun Anda telah dikunci selama {LOCKOUT_DURATION_MINUTES} menit.', 'error')
                else:
                    flash('Username atau password tidak valid.', 'error')
                db.session.commit()
                return redirect(url_for('auth.login'))
        else:
            # User not found: provide generic error
            flash('Username atau password tidak valid.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/verify_2fa_login', methods=['GET', 'POST'])
def verify_2fa_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if 'temp_user_id' not in session:
        flash('Silakan login ulang.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['temp_user_id'])
    if not user:
        flash('Verifikasi 2FA tidak diperlukan atau tidak diaktifkan.', 'error')
        session.pop('temp_user_id', None)
        return redirect(url_for('auth.login'))

    # Check if account is locked out for 2FA verification as well
    if user.lockout_until and user.lockout_until > datetime.utcnow():
        remaining_time = user.lockout_until - datetime.utcnow()
        flash(f'Akun Anda terkunci. Coba lagi setelah {int(remaining_time.total_seconds() / 60)} menit.', 'error')
        session.pop('temp_user_id', None) # Clear session to force re-login attempt
        return redirect(url_for('auth.login'))

    if not user.otp_enabled:
        flash('Verifikasi 2FA tidak diperlukan atau tidak diaktifkan.', 'error')
        session.pop('temp_user_id', None)
        return redirect(url_for('auth.login'))

    form = OTPVerificationForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(form.otp_code.data):
            # Successful 2FA verification: reset failed attempts and lockout
            user.failed_login_attempts = 0
            user.lockout_until = None
            db.session.commit()

            login_user(user)
            session.pop('temp_user_id', None)

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.role == 'superadmin':
                    next_page = url_for('admin.dashboard')
                elif user.role == 'admin':
                    next_page = url_for('admin.dashboard')
                elif user.role in ['staf', 'pending']:
                    next_page = url_for('staf.dashboard')
                else:
                    next_page = url_for('main.index')
            return redirect(next_page)
        else:
            # Failed OTP: increment failed attempts
            MAX_FAILED_ATTEMPTS = 5 # Use same constants as login
            LOCKOUT_DURATION_MINUTES = 30 # Use same constants as login

            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                flash(f'Kode OTP tidak valid dan terlalu banyak percobaan. Akun Anda telah dikunci selama {LOCKOUT_DURATION_MINUTES} menit.', 'error')
                session.pop('temp_user_id', None) # Clear session to prevent further 2FA attempts
            else:
                flash('Kode OTP tidak valid.', 'error')
            db.session.commit()
    
    return render_template('auth/verify_2fa_login.html', title='Verifikasi 2FA', form=form)


@auth_bp.route('/setup_2fa', methods=['GET'])
@login_required
def setup_2fa():
    if current_user.otp_enabled:
        flash('2FA sudah diaktifkan.', 'message')
        return redirect(url_for('main.index'))

    # Generate a random secret for the user
    secret = pyotp.random_base32()
    session['otp_secret'] = secret # Store secret in session temporarily

    # Generate the OTPAuth URI (Google Authenticator compatible)
    # Issuer should be the app name, current_user.username is the account name
    issuer_name = 'KonterHP'
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.username,
        issuer_name=issuer_name
    )

    # Generate QR code image
    img = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('auth/setup_2fa.html', 
                           title='Setup 2FA', 
                           qr_code=qr_code_base64,
                           secret=secret)

@auth_bp.route('/verify_2fa_setup', methods=['GET', 'POST'])
@login_required
def verify_2fa_setup():
    if current_user.otp_enabled:
        flash('2FA sudah diaktifkan.', 'message')
        return redirect(url_for('main.index'))

    secret = session.get('otp_secret')
    if not secret:
        flash('Silakan mulai setup 2FA lagi.', 'error')
        return redirect(url_for('auth.setup_2fa'))

    form = OTPVerificationForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(secret)
        if totp.verify(form.otp_code.data):
            current_user.otp_secret = secret
            current_user.otp_enabled = True
            db.session.commit()
            session.pop('otp_secret', None) # Clear secret from session
            flash('2FA berhasil diaktifkan!', 'message')
            return redirect(url_for('main.index'))
        else:
            flash('Kode OTP tidak valid.', 'error')
    
    return render_template('auth/verify_2fa_setup.html', title='Verifikasi Setup 2FA', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
