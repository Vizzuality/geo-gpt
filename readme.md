
  

# GeoGPT
  
GeoGPT is a web application that provides land cover analysis and descriptions based on user-inputted geographic locations. It uses Google Earth Engine and OpenAI GPT-3.5 to generate comprehensive reports.

 ## Using docker
 Download and install docker:  https://docs.docker.com/get-docker/
Run:

    docker build -t earthgpt .
    docker run -p 5000:5000 -v "$(pwd)":/app earthgpt

Navigate to http://localhost:5000
  
## No docker

  **Environment and secrets**

Copy your google_service.json into your app dir.

Create your .env in your app dir, it should look like:

    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=your_flask_sectret_key (any hex(16) or hex(24) char
    OAUTHLIB_INSECURE_TRANSPORT=1
    OPENAI_API_KEY=your_open_ai_api_key
    FLASK_DEBUG=1
    GEE_SERVICE_ACCOUNT_KEYPATH=./google_service.json


 **Python Dependencies**

  

To install the required Python dependencies, first create a virtual environment and then run the following command:

  

  
  

    pip install -r requirements.txt

  

**Requirements**

  

The requirements.txt file includes the following dependencies:

  
  
    openai
    flask
    python-dotenv
    langchain
    gcloud
    earthengine-api
    google-auth
    google-auth-httplib2
    google-api-python-client
    flask_httpauth
    geopy
    flask-login
    flask-jwt-extended
    google-auth-oauthlib
    shapely
    pyproj


**Front-end Dependencies**

For the front-end, this project uses Tailwind CSS. To set up Tailwind, follow the instructions in the Tailwind CSS installation guide.

**Running the Application**

After installing the dependencies, you can run the application by executing the following command:
 

    yarn install
    yarn build
	flask run
Navigate to http://localhost:5000