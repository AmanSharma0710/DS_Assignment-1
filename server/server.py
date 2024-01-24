from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# For testing purposes, you can set the server ID as an environment variable while running the container instance of the server.
# os.environ['SERVER_ID'] = '1231'

'''
(/home,method=GET): This endpoint returns a greeting message from the server instance.
The message includes the server ID, which is set as an environment variable when running the container instance of the server.
No request payload is required.
Sample response:
{
    "message": "Hello from Server: 1231",
    "status": "successful"
}
'''
@app.route('/home', methods=['GET'])
def home():
    message = 'Hello from Server: ' + str(os.environ['SERVER_ID'])
    return jsonify({'message': message, 'status': 'successful'}), 200

'''
(/heartbeat,method=GET): This endpoint is used for health checks of the server instance.
No request payload is required and it returns an empty response with a 200 status code.
'''
@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return '', 200

'''
(/<path>,method=GET): This endpoint is a catch-all for any undefined routes.
It returns an error message indicating that the requested endpoint does not exist in the server replicas.
No request payload is required.
Sample response for a request to '/undefined_endpoint':
{
    "message": "<ERROR> 'undefined_endpoint' endpoint does not exist in server replicas",
    "status": "failure"
}
'''
@app.route('/<path>', methods=['GET'])
def no_endpoint(path):
    message = '<ERROR> \'{}\' endpoint does not exist in server replicas'.format(path)
    return jsonify({'message': message, 'status': 'failure'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)