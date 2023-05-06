# Use the official Python base image
FROM python:3.11

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js to be able to use yarn
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

# Add the Yarn repository
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

# Update the package list and install yarn
RUN apt-get update && \
    apt-get install -y yarn

# Install yarn and build the frontend
COPY package.json yarn.lock ./
RUN yarn install
COPY . .
RUN yarn build

# Copy the start.sh script
COPY start.sh /app

# Set the entrypoint to the start.sh script
ENTRYPOINT ["./start.sh"]

# Copy the .env file into the container
COPY .env ./

# Expose the port the app runs on
EXPOSE 5000


# docker build -t earthgpt .
# docker run -p 5000:5000 -v "$(pwd)":/app earthgpt
