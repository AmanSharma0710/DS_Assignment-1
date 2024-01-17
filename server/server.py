from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# For testing purposes, you can set the server ID as an environment variable while running the container instance of the server.
os.environ['SERVER_ID'] = '1'


@app.route('/home', methods=['GET'])
def home():
    message = 'Hello from Server: ' + str(os.environ['SERVER_ID'])
    return jsonify({'message': message, 'status': 'successful'}), 200


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return '', 200