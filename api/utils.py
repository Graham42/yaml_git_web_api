from werkzeug.wrappers import Response
import json
import os

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


def file_list_to_links(f_list, host_url, prefix_to_rm=''):
    new_list = []
    for item in f_list:
        # remove the file extension
        item = os.path.splitext(item)[0]
        try:
            # remove the 'data/' part of the path
            item = item[item.index(prefix_to_rm) + len(prefix_to_rm):]
        except ValueError as e:
            # if the path didn't have the prefix we don't care
            pass
        new_list.append(os.path.join(host_url, item))
    return new_list


def refs_to_links(obj, host_url):
    # treat string as scalar
    if isinstance(obj, str):
        return obj
    try:
        # try treating like a dict
        for key in obj:
            if key == 'ref':
                temp = os.path.join(host_url, obj[key])
                obj = temp
                break
            else:
                transformed = refs_to_links(obj[str(key)], host_url)
                obj[key] = transformed
        return obj
    except KeyError as e:
        # must be a list
        obj = [refs_to_links(item, host_url) for item in obj]
        return obj
    except TypeError as e:
        # not an iterable value
        return obj
