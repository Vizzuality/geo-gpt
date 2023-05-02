from flask import Blueprint, jsonify, request, redirect, url_for, session, make_response
from flask_login import login_required, login_user, UserMixin, logout_user
from flask_jwt_extended import jwt_required, create_access_token
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

oauth_bp = Blueprint("oauth", __name__)

class User(UserMixin):
    def __init__(self, email):
        self.email = email
        self.id = email

def init_oauth_bp(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)
    
@oauth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    response = make_response(jsonify({"redirect_url": url_for("routes.index")}))
    response.delete_cookie("access_token")
    return response
    
@oauth_bp.route("/authorize")
def authorize():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    client_secrets_path = os.path.join(script_dir, 'client_secret.json')

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'openid'],
        redirect_uri=url_for("oauth.oauth2callback", _external=True),
    )
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@oauth_bp.route("/oauth2callback")
def oauth2callback():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    client_secrets_path = os.path.join(script_dir, 'client_secret.json')

    state = session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'openid'],
        state=state,
        redirect_uri=url_for("oauth.oauth2callback", _external=True),
    )

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session["credentials"] = credentials_to_dict(credentials)

    # Get user email
    userinfo = googleapiclient.discovery.build("oauth2", "v2", credentials=credentials).userinfo().get().execute()
    user_email = userinfo["email"]

    # Log in the user
    user = User(user_email)
    login_user(user)

    # Create an access token for the API
    access_token = create_access_token(identity=user_email)

    # Store the access token in a cookie
    response = make_response(redirect(url_for("routes.index")))
    response.set_cookie("access_token", access_token)

    return response

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
