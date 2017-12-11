#!flask/bin/python
import uuid

from flask import Flask, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from flask_pymongo import PyMongo

app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()

admins = {
    "admin": "admin"
}

@auth.get_password
def get_pw(username):
    if username in admins:
        return admins.get(username)
    return None

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://192.168.99.100:32769/prtdb'
mongo_mgr = PyMongo(app)

@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

required = ['firstname', 'lastname', 'latitude', 'longitude']

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/prt/api/v1.0/users', methods=['GET'])
@auth.login_required
def get_users():
    """
    Update this to return a json stream defining a listing of the users
    Note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    output = []
    for user in users.find():
        output.append({
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'latitude': user['latitude'],
            'longitude': user['longitude'],
            'id': user['id'],
        })
    return jsonify({'result' : output})


@app.route('/prt/api/v1.0/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    users = mongo_mgr.db.users
    output = []
    user = users.find_one({'id': str(user_id)})
    if not user:
        raise InvalidUsage('User with ID %d not found' % user_id , status_code=404)
    output.append({
        'firstname': user['firstname'],
        'lastname': user['lastname'],
        'latitude': user['latitude'],
        'longitude': user['longitude'],
        'id': user['id'],
    })
    return jsonify({'result': output})


def get_user_data(request_data):
    missing = []
    data = {}
    for r in required:
        if r not in request_data or not request_data[r]:
            missing.append(r)
        else:
            data[r] = request_data[r]
    if missing:
        raise InvalidUsage('Missing user data: %s' % ', '.join(missing), status_code=400)
    return data

@app.route('/prt/api/v1.0/users', methods=['POST'])
@auth.login_required
def create_user():
    """
    Should add a new user to the users collection, with validation
    note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    data = get_user_data(request.get_json())
    data['id'] = str(uuid.uuid4().int)
    users.insert(data)
    del data['_id']
    return jsonify({'result': data}), 201


@app.route('/prt/api/v1.0/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    """
    Update user specified with user ID and return updated user contents
    Note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    user = users.find_one({'id': str(user_id)})
    if not user:
        raise InvalidUsage('User with ID %d not found' % user_id, status_code=404)
    data = get_user_data(request.get_json())
    mongo_mgr.db.users.update_one({
        '_id': user['_id']
    }, {
        '$set': data
    }, upsert=False)
    return jsonify({'result': data})


@app.route('/prt/api/v1.0/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    """
    Delete user specified in user ID
    Note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    user = users.find_one({'id': str(user_id)})
    if not user:
        raise InvalidUsage('User with ID %d not found' % user_id, status_code=404)
    mongo_mgr.db.users.remove({'_id': user['_id']})
    return jsonify({'result': 'User with ID %d deleted.' % user_id})

@app.route('/prt/api/v1.0/distances', methods=['GET'])
@auth.login_required
def get_distances(user_id):
    """
    Each user has a lat/lon associated with them.  Determine the distance
    between each user pair, and provide the min/max/average/std as a json response.
    This should be GET only.
    You can use numpy or whatever suits you
    """
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
