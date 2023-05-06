import os
from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
openai_api_key = os.getenv('OPENAI_API_KEY')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '1')
service_account_key_path = os.getenv('GEE_SERVICE_ACCOUNT_KEYPATH')
