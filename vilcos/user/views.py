from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, request, session, url_for, current_app
from vilcos.extensions import supabase
from gotrue.errors import AuthApiError

bp_user = Blueprint('users', __name__, url_prefix='/auth', static_folder='../static')

def set_user_session(session_data):
    session['access_token'] = session_data['access_token']
    session['refresh_token'] = session_data['refresh_token']
    session['expires_at'] = session_data.get('expires_at')
    session['user'] = {
        'id': session_data['user'].id,
        'email': session_data['user'].email,
        'role': session_data['user'].role,
        'last_sign_in_at': session_data['user'].last_sign_in_at
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        access_token = session.get('access_token')

        if not user or not access_token:
            return redirect(url_for('users.signin', next=request.url))

        try:
            # Verify the access token with Supabase
            verified_user = supabase.client.auth.get_user(access_token)

            # Check if the user_id in the session matches the one from the token
            if verified_user.user.id != user['id']:
                raise ValueError("User ID mismatch")

        except Exception as e:
            # If verification fails, clear the session and redirect to login
            session.clear()
            return redirect(url_for('users.signin', next=request.url))

        return f(*args, **kwargs)

    return decorated_function

@bp_user.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        data = request.get_json()
        try:
            response = supabase.client.auth.sign_in_with_password(
                credentials={"email": data.get('email'), "password": data.get('password')}
            )
            set_user_session({
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token,
                'expires_at': response.session.expires_at,
                'user': response.user
            })
            return {"success": True, "message": "Login successful", "redirect": '/dashboard'}
        except AuthApiError as e:
            return {"success": False, "message": str(e)}, 400

    return render_template('auth/signin.html')

@bp_user.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        try:
            response = supabase.client.auth.sign_up(
                credentials={
                    "email": data.get('email'),
                    "password": data.get('password'),
                    "options": {"data": {"username": data.get('username')}}
                }
            )
            return {
                "success": True,
                "message": "Please check your email to verify your account.",
                "redirect": url_for('users.signin')
            }
        except AuthApiError as e:
            return {"success": False, "message": str(e)}, 400

    return render_template('auth/signup.html')

@bp_user.route('/signout', methods=['GET', 'POST'])
def signout():
    if request.method == 'POST':
        supabase.client.auth.sign_out()
        session.clear()
        return redirect(url_for('users.signin'))
    return render_template('auth/signout.html')

@bp_user.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.get_json()
        try:
            supabase.client.auth.reset_password_for_email(email=data.get('email'))
            return {
                "success": True,
                "message": "Please check your email for a password reset link.",
                "redirect": url_for('users.signin')
            }
        except AuthApiError as e:
            return {"success": False, "message": str(e)}, 400

    return render_template('auth/forgot-password.html')

@bp_user.route("/signin/github")
def signin_with_github():
    resp = supabase.client.auth.sign_in_with_oauth(
        {
            "provider": "github",
            "options": {"redirect_to": f"{request.url_root}auth/callback"}
        }
    )
    return redirect(resp.url)

@bp_user.route("/callback")
def callback():
    return render_template('auth/callback.html')


@bp_user.post('/process-tokens')
def process_tokens():
    data = request.json
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')

    if access_token and refresh_token:
        # Fetch the user information using the access token
        user_info = supabase.client.auth.get_user(access_token)

        if user_info.user is None:  # Check if user_info.user exists
            return {"success": False, "message": "Failed to retrieve user info"}, 400

        set_user_session({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_info.user
        })

        return {"success": True, "redirect": "/dashboard"}

    return {"success": False, "message": "Missing token data"}, 400


@bp_user.route('/dashboard')
@login_required
def dashboard():
    user = session.get('user')
    if user is None:
        return {"success": False, "message": "Not authenticated"}, 401
    return render_template('user/dashboard.html', user=user)
