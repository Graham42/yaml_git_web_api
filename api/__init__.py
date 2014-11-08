# try and keep Flask imports to a minimum, going to refactor later to use
# just werkzeug, for now, prototype speed is king
from flask import Flask, request
import yaml
import os
import re
from datetime import datetime
from api.config import config, ConfigException
import api.repo
import api.utils


app = Flask(__name__)
app.config.from_object('api.config')


@app.route('/schema', defaults={'path': ''}, methods=['GET'])
@app.route('/schema/<path:path>', methods=['GET'])
def get_schemas(path):
    # TODO serve schemas
    return utils.json_response({'win': 'scheme away'}, 200)


@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def get_data(path):
    """Handle all GET requests to the api"""

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
            return utils.err(406)
    else:
        if match.group(2) is not None:
            cid = match.group(2)
            try:
                version = repo.get_commit(cid)
            except (KeyError, ValueError) as e:
                return utils.err(406)

    if repo.path_files(file_path + config['DATA_FILE_EXT'], version.id) is None:
        # .yml file doesn't exist, check if path matches a directory
        f_list = repo.path_files(file_path, version.id)
        if f_list is None:
            return utils.err(404)
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


@app.errorhandler(Exception)
def unknown_err(error):
    data = {
        'status': 500,
        'error_message': 'Unknown Internal Server Error'
    }
    return utils.json_response(data, 500)


@app.errorhandler(405)
def http_errs(error):
    data = {
        'status': error.code,
        'error_message': error.name
    }
    return utils.json_response(data, error.code)
