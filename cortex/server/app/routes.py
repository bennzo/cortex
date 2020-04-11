import flask
import bson
from pathlib import Path
from . import app
from ...net import protocol


@app.route('/config', methods=['GET'])
def get_config():
    config_string = protocol.Config(app.config['PARSERS']).to_bson()
    return bson.encode(config_string)


@app.route('/snapshot', methods=['POST'])
def post_snapshot():
    data = bson.decode(flask.request.data)
    try:
        user, snapshot = data['user'], data['snapshot']
        fields = app.config['PARSERS']
        data_dir = Path(app.config['DATA_FOLDER'])
        user_dir = data_dir / str(user['uid']) / snapshot['timestamp_ms'].strftime('%Y-%m-%d_%H-%M-%S-%f')
        user_dir.mkdir(parents=True, exist_ok=True)

        if 'image_color' in fields:
            image_path = user_dir / 'image_color.raw'
            with image_path.open(mode='wb') as fd:
                fd.write(snapshot['image_color']['image_color'])
            snapshot['image_color']['image_color'] = str(image_path)

        if 'image_depth' in fields:
            image_path = user_dir / 'image_depth.raw'
            with image_path.open(mode='wb') as fd:
                fd.write(snapshot['image_depth']['image_depth'])
            snapshot['image_depth']['image_depth'] = str(image_path)

        app.config['PUBLISH_MESSAGE'](data)
    except Exception as e:
        print(e)
    return ''
