import flask

app = flask.Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)


from . import routes
