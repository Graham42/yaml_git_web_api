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
    body = json.dumps(obj)
    resp = Response(body, status=status, mimetype='application/json')
    return resp


@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def get(path):
    """Handle all GET requests to the api"""
    # pseudo ish idea of what this function should do
    # get request path
    # get revision, default to HEAD
    # set metadata part of the reponse body
    # check if path + '.yml' exists at that revision
    #   if not, return 404
    # if exists, convert load yaml file
    # maybe validate against schema??
    # convert to json and set as data part of the body

    file_path = os.path.join('data', path + '.yml')

    try:
        raw = repo.file_contents(file_path)
    except:
        return json_response({"error": "not found"}, 404)

    data = yaml.load(raw)
    # get git meta data here
    metadata = {}

    ret_obj = {
        'data': data,
        'metadata': metadata
    }
    return json_response(data)
