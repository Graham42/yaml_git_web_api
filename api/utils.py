from werkzeug.wrappers import Response
import json

ERROR_MSGS = {
    '404': 'Not found'
}


def json_response(obj, status=200):
    body = json.dumps(obj, sort_keys=True)
    resp = Response(body, status=status, mimetype='application/json')
    return resp


def err(error_code):
    data = {}
    if str(error_code) in ERROR_MSGS:
        data['error_message'] = ERROR_MSGS[str(error_code)]
    else:
        data['error_message'] = 'Unknown error'

    return json_response(data, error_code)
