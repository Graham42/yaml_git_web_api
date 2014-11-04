# try and keep Flask imports to a minimum, going to refactor later to use
# just werkzeug, for now, prototype speed is king
from flask import Flask
from werkzeug.wrappers import Response
import json
import yaml
from api.config import config, ConfigException
from api import repo
import os

app = Flask(__name__)
app.config.from_object('api.config')


def json_response(obj, status=200):
    body = json.dumps(obj, sort_keys=True)
    resp = Response(body, status=status, mimetype='application/json')
    return resp


@app.route('/schema', defaults={'path': ''}, methods=['GET'])
@app.route('/schema/<path:path>', methods=['GET'])
def getSchemas(path):
    # TODO serve schemas
    return json_response({'win': 'scheme away'}, 200)


@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def getData(path):
    """Handle all GET requests to the api"""
    # #FUTURE
    # - git metadata
    # - get revision, default to HEAD
    # - maybe validate against schema??

    file_path = os.path.join('data', path)

    if repo.path_files(file_path + '.yml') is None:
        f_list = repo.path_files(file_path)
        if f_list is None:
            return err(404)
        data = f_list
    else:
        raw = repo.file_contents(file_path + '.yml')
        data = yaml.load(raw)

    # get git meta data here
    metadata = {}

    ret_obj = {
        'data': data,
        'metadata': metadata
    }
    return json_response(ret_obj)


ERROR_MSGS = {
    '404': 'Not found'
}


def err(error_code):
    data = {}
    if str(error_code) in ERROR_MSGS:
        data['error_message'] = ERROR_MSGS[str(error_code)]
    else:
        data['error_message'] = 'Unknown error'

    return json_response(data, error_code)
