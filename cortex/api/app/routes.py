import flask
import bson
from pathlib import Path
from . import app
from ...net import protocol


@app.route('/users', methods=['GET'])
def get_users():
    pass


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    pass


@app.route('/users/<int:user_id>/snapshots', methods=['GET'])
def get_user_snapshots(user_id):
    pass


@app.route('/users/<int:user_id>/snapshots/<int:ss_id>', methods=['GET'])
def get_user_snapshot(user_id, ss_id):
    pass


@app.route('/users/<int:user_id>/snapshots/<int:ss_id>/<string:field>', methods=['GET'])
def get_user_snapshot_field(user_id, ss_id, field):
    pass


@app.route('/users/<int:user_id>/snapshots/<int:ss_id>/<string:field>/data', methods=['GET'])
def get_user_snapshot_field_data(user_id, ss_id, field):
    pass
