#!/bin/sh

# Start the frontend
yarn watch &

# Start the Flask app with auto-reloading
flask run --host 0.0.0.0 --reload
