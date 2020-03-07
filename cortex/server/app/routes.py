import flask
import bson
from . import app
from ...net import protocol


@app.route('/config', methods=['GET'])
def get_config():
    config_string = protocol.Config(app.config['PARSERS']).serialize()
    return config_string


@app.route('/snapshot', methods=['POST'])
def post_snapshot():
    # TODO: Support async snapshot posting - user should get an OK response after the snapshot was saved but it shouldn't hold up other users
    # TODO: Confirm saving files to drive is thread safe with flask
    user_snapshot = bson.decode(flask.request.data)
    user = protocol.Snapshot.deserialize(user_snapshot['user'])
    snapshot = protocol.Snapshot.deserialize(user_snapshot['snapshot'])
    # Save raw data to disk
    # Add path to message
    # Publish message
    return ''
