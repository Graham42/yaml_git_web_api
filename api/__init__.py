from flask import Flask, request, jsonify
import yaml
import os
import re
from datetime import datetime
from api.config import config, ConfigException
import api.repo
import api.utils
from werkzeug import exceptions as wz_err
from werkzeug.exceptions import default_exceptions
from uuid import uuid4

WRITE_TOKEN_HEADER = 'X-Bulk-Write-Token'

app = Flask(__name__)
app.config.from_object('api.config')


def make_json_error(err):
    response = jsonify(message=str(err))
    response.status_code = err.code if isinstance(err, wz_err.HTTPException) else 500
    if config['DEBUG']:
        response.developer_message = str(err)
    return response

for code in default_exceptions.keys():
    app.error_handler_spec[None][code] = make_json_error


@app.route('/schema', defaults={'path': ''}, methods=['GET'])
@app.route('/schema/<path:path>', methods=['GET'])
def get_schemas(path):
    # TODO serve schemas
    return utils.json_response({'TODO': 'scheme away'}, wz_err.NotImplemented)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT'])
def _data(path):
    if request.method == 'GET':
        return data_get(path)
    elif request.method == 'PUT':
        return data_put(path)
    elif request.method == 'POST':
        return data_post(path)
    else:
        raise wz_err.NotImplemented


def data_get(path):
    """
    HTTP method GET for data
    """

    metadata = {}

    file_path = os.path.join('data', path)
    latest_version = repo.get_latest_commit()
    # default request version to the latest
    version = latest_version
    # check if the request specified a version via header
    accept_pattern = re.compile('application/(.+)\+json')
    match = accept_pattern.match(request.headers['Accept'])
    if match is None:
        match = request.accept_mimetypes.best_match(['application/json'])
        if match is None:
            raise wz_err.NotAcceptable
    else:
        if match.group(2) is not None:
            cid = match.group(2)
            try:
                version = repo.get_commit(cid)
            except (KeyError, ValueError) as e:
                raise wz_err.NotAcceptable

    if repo.path_files(file_path + config['DATA_FILE_EXT'], version.id) is None:
        # .yml file doesn't exist, check if path matches a directory
        f_list = repo.path_files(file_path, version.id)
        if f_list is None:
            raise wz_err.NotFound
        data = utils.file_list_to_links(f_list, request.host_url, 'data/')

        metadata['data_type'] = 'directory listing'
    else:
        raw = repo.file_contents(file_path + config['DATA_FILE_EXT'], version.id)
        data = yaml.load(raw)
        data = utils.refs_to_links(data, request.host_url)

        metadata['data_type'] = 'file content'
        metadata['version'] = {
            'id': str(version.id),
            'date': datetime.fromtimestamp(version.commit_time).isoformat()
        }
        if version.id != latest_version.id:
            metadata['latest_version'] = {
                'id': str(latest_version.id),
                'date': datetime.fromtimestamp(latest_version.commit_time).isoformat()
            }

    ret_obj = {
        'data': data,
        'metadata': metadata
    }
    return utils.json_response(ret_obj)


def data_put(path):
    """
    Handle HTTP PUT for data

    Overwrite the existing resource or create a new one. In either case the
    received object will be validated against the schema for this resource type.
    If no schema exists, will return an error.

    Returns the path of the file that was written and a bulk write token which
    can be used to add more writes to the branch corresponding to this token.

    Example to create or update student with id 1234:
    PUT /student/1234
    """
    # check schema exists, and validate against schema
    # if ok, create resource
    data = yaml.load(request.get_json())
    # check if the request is adding to an existing branch
    if WRITE_TOKEN_HEADER in request.headers:
        token = request.headers[WRITE_TOKEN_HEADER]
    else:
        token = str(uuid4())

    file_path = os.path.join('data', path) + config['DATA_FILE_EXT']
    repo.write_file(file_path, data, token)
    return utils.json_response({'href': path, WRITE_TOKEN_HEADER: token})


def data_post(path):
    """
    Handle HTTP POST for data

    Create a new resource if it does not exist. The received object will be
    validated against the schema for this resource type. If no schema exists,
    will return an error.

    Example to create a new student (would generate id):
    POST /student/
    """
    # check if path exists
    file_path = os.path.join('data', path) + config['DATA_FILE_EXT']
    latest_version = repo.get_latest_commit()
    if repo.path_files(file_path, latest_version.id) is None:
        # check schema exists, and validate against schema
        # if ok, create new resource and return location
        pass
    else:
        # return error - already exists
        pass
    return utils.json_response({'posted': 'more stuff'})
