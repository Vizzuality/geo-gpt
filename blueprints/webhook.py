import subprocess
from flask import Flask, request, Blueprint, app
import hmac
import hashlib

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify the signature of the request
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        return 'Invalid signature', 400

    signature_parts = signature.split('=', 1)
    if len(signature_parts) != 2:
        return 'Invalid signature', 400

    signature_type, signature_value = signature_parts
    if signature_type != 'sha1':
        return 'Unsupported signature type', 400

    secret = app.config['GITHUB_WEBHOOK_SECRET']
    mac = hmac.new(secret.encode('utf-8'), request.data, hashlib.sha1)
    expected_signature = f'sha1={mac.hexdigest()}'
    if not hmac.compare_digest(signature, expected_signature):
        return 'Invalid signature', 400

    # The signature is valid, handle the webhook request
    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'push':
        branch = request.json.get('ref', '').split('/')[-1]
        if branch == 'production':
            deploy()
            pass

    return 'Webhook received', 200

def deploy():
    subprocess.run(['git', 'fetch', 'origin', 'production'])
    subprocess.run(['git', 'reset', '--hard', 'origin/production'])
    subprocess.run(['git', 'clean', '-f', '-d', '-x', '--exclude=.env', '--exclude=client_secret.json'])
    subprocess.run(['git', 'pull', 'origin', 'production', '--force', '--exclude=.env', '--exclude=client_secret.json'])
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    subprocess.run(['yarn', 'install'])
    subprocess.run(['yarn', 'build'])