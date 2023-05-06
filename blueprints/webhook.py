import subprocess
from flask import Flask, request, Blueprint, app
import hmac
import hashlib
import logging

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify the signature of the request
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        logging.info("Invalid signature")
        return 'Invalid signature', 400

    signature_parts = signature.split('=', 1)
    if len(signature_parts) != 2:
        logging.info("Invalid signature")
        return 'Invalid signature', 400

    signature_type, signature_value = signature_parts
    if signature_type != 'sha1':
        logging.info("Unsupported signature type")
        return 'Unsupported signature type', 400

    secret = app.config['GITHUB_WEBHOOK_SECRET']
    mac = hmac.new(secret.encode('utf-8'), request.data, hashlib.sha1)
    expected_signature = f'sha1={mac.hexdigest()}'
    if not hmac.compare_digest(signature, expected_signature):
        logging.info("Invalid signature")
        return 'Invalid signature', 400

    # The signature is valid, handle the webhook request
    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'push':
        branch = request.json.get('ref', '').split('/')[-1]
        if branch == 'main':
            deploy()
            pass
    logging.info("Webhook received")
    return 'Webhook received', 200

def deploy():
    commands = [
        ['git', 'fetch', 'origin', 'main'],
        ['git', 'reset', '--hard', 'origin/main'],
        ['git', 'clean', '-f', '-d', '-x', '--exclude=.env', '--exclude=client_secret.json'],
        ['git', 'pull', 'origin', 'main', '--force'],
        ['pip', 'install', '-r', 'requirements.txt'],
        ['yarn', 'install'],
        ['yarn', 'build'],
        ['sudo', 'systemctl', 'restart', 'geo-gpt.service']
    ]

    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Command '{' '.join(command)}' failed with error: {result.stderr}")
            return

    logging.info("Deployment completed successfully")