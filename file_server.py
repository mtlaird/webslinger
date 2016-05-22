from wsgiref.simple_server import make_server
from httpclasses import HTTPRequest, HTTPResponse, serve_file, not_found
import os.path
from router import *


def filebrowser(response, request):
    path = request.path_info
    local_path = 'M:'
    full_path = local_path + path
    if os.path.isfile(full_path):
        return serve_file(response, request, local_path)
    elif os.path.isdir(full_path):
        return show_directory(response, request, local_path)
    else:
        return not_found(response)


def show_directory(response, request, local_path='/'):
    path = request.path_info
    full_path = local_path + path
    dir_contents = os.listdir(full_path)
    for c in dir_contents:
        if '.' not in c:
            dir_content_str = c+'/'
        else:
            dir_content_str = c
        response.add_body('- <a href="{}">{}</a><br>'.format(dir_content_str, dir_content_str))
    return response


def application(environ, start_response):

    rt = RouteTable()

    rt.add_route('any', filebrowser)

    request = HTTPRequest(environ)
    response = HTTPResponse()
    response = rt.eval_route(request)(response, request)

    response.make_headers()
    start_response(response.status, response.headers)

    return response.response


def run_server():
    httpd = make_server('', 8088, application)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
