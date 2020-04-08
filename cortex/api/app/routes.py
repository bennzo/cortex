import datetime

import bson
from flask import jsonify, request

from pathlib import Path
from . import app
from ...net import protocol


@app.route('/users', methods=['GET'])
def get_users():
    user_list = app.config['DB_CLIENT'].get_users()
    return jsonify(user_list)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = app.config['DB_CLIENT'].get_user(user_id)
    if isinstance(user['birthday'], datetime.datetime):
        user['birthday'] = user['birthday'].strftime('%Y/%m/%d')
    return jsonify(user)


@app.route('/users/<int:user_id>/snapshots', methods=['GET'])
def get_user_snapshots(user_id):
    snapshot_list = app.config['DB_CLIENT'].get_user_snapshots(user_id)
    for snap in snapshot_list:
        if isinstance(snap['datetime'], datetime.datetime):
            snap['datetime'] = snap['datetime'].strftime('%Y/%m/%d %H:%M:%S:%f')
    return jsonify(snapshot_list)


@app.route('/users/<int:user_id>/snapshots/<int:ss_id>', methods=['GET'])
def get_user_snapshot(user_id, ss_id):
    user_snapshot = app.config['DB_CLIENT'].get_user_snapshot(user_id, ss_id)
    return jsonify(user_snapshot)


@app.route('/users/<int:user_id>/snapshots/<int:ss_id>/<string:field>', methods=['GET'])
def get_user_snapshot_field(user_id, ss_id, field):
    _data_fields = {'image_color', 'image_depth'}
    result = app.config['DB_CLIENT'].get_user_snapshot_field(user_id, ss_id, field)
    if field in _data_fields:
        result[field] = request.base_url + '/data'
    return jsonify(result)


@app.route('/users/<int:user_id>/snapshots/<int:ss_id>/<string:field>/data', methods=['GET'])
def get_user_snapshot_field_data(user_id, ss_id, field):
    data = app.config['DB_CLIENT'].get_user_snapshot_field_data(user_id, ss_id, field)
    return data
