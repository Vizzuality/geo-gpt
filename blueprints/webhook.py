import subprocess
from flask import Flask, request, Blueprint, app
import hmac
import hashlib
import logging
from config import webhook_secret
from sh import Command
import sh
import os

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

    secret = webhook_secret
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
    os.environ['GIT_SSH_COMMAND'] = '/usr/bin/ssh'
    git = Command('/usr/bin/git')
    pip = Command('/home/ubuntu/.pyenv/versions/3.11.1/bin/pip')
    yarn = Command('/home/ubuntu/.nvm/versions/node/v18.16.0/bin/yarn')
    sudo = Command('/usr/bin/sudo')

    commands = [
        (git, ['fetch', 'origin', 'main']),
        (git, ['reset', '--hard', 'origin/main']),
        (git, ['clean', '-f', '-d', '-x', '--exclude=.env', '--exclude=client_secret.json']),
        (git, ['pull', 'origin', 'main', '--force']),
        (pip, ['install', '-r', 'requirements.txt']),
        (yarn, ['install']),
        (yarn, ['build']),
        (sudo, ['systemctl', 'restart', 'geo-gpt.service'])
    ]

    for cmd, args in commands:
        try:
            cmd(*args, _err_to_out=True, _out=logging.info, _bg_exc=False)
        except sh.ErrorReturnCode as e:
            logging.error(f"Command '{cmd} {' '.join(args)}' failed with error: {e.stderr}")
            return

    logging.info("Deployment completed successfully")