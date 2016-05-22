import os
from pprint import pformat
import urlparse


class HTTPContentType:
    def __init__(self, content_type, media, binary=False):
        self.content_type = content_type
        self.media = media
        self.binary = binary


class HTTPRequest:
    def __init__(self, environ):
        self.remote_address = environ['REMOTE_ADDR']
        self.content_length = environ['CONTENT_LENGTH']
        self.server_protocol = environ['SERVER_PROTOCOL']
        self.server_port = environ['SERVER_PORT']
        self.query_string = environ['QUERY_STRING']
        self.request_method = environ['REQUEST_METHOD']
        self.path_info = environ['PATH_INFO']
        headers = {}
        for key in environ.keys():
            if key[0:5] == 'HTTP_':
                headers[key[5:].replace('_', '-').title()] = environ[key]
        self.headers = headers
        if 'wsgi.input' in environ.keys() and self.content_length:
            self.input = environ['wsgi.input'].read(int(self.content_length))
        else:
            self.input = None

    def get_form_data(self):
        form_data = pformat(self.input)
        form_data = form_data.replace("'", "")
        form_data = urlparse.parse_qs(form_data)
        for d in form_data:
            if type(form_data[d]) is list:
                form_data[d] = form_data[d][0]
        return form_data


class HTTPResponse:
    def __init__(self, params=None):
        if not params:
            params = {}
        self.head = []
        self.body = []
        self.content_type = 'html'
        self.status = '200 OK'
        self.headers = []
        self.response = []
        if 'html_wrapper_open' in params:
            self.html_wrapper_open = self._listify(params['html_wrapper_open'])
        else:
            self.html_wrapper_open = []
        if 'html_wrapper_close' in params:
            self.html_wrapper_close = self._listify(params['html_wrapper_close'])
        else:
            self.html_wrapper_close = []
        if 'bootstrap' in params:
            self.add_head([
                '<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">'
                '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>'
                '<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>'])
        self.raw_html_body = False
        self.known_content_types = {'html': HTTPContentType('html', 'text'), 'css': HTTPContentType('css', 'text'),
                                    'jpeg': HTTPContentType('jpeg', 'image', binary=True),
                                    'png': HTTPContentType('png', 'image', binary=True),
                                    'gif': HTTPContentType('gif', 'image', binary=True),
                                    'pdf': HTTPContentType('pdf', 'application', binary=True),
                                    'xml': HTTPContentType('xml', 'application'),
                                    'json': HTTPContentType('json', 'application'),
                                    'javascript': HTTPContentType('javascript', 'application'),
                                    'plain': HTTPContentType('plain', 'text')}
        self.alternate_content_type_extensions = {'jpg': 'jpeg', 'js': 'javascript'}

    @staticmethod
    def _listify(content):
        if type(content) == list:
            return content
        elif type(content) == str:
            return [content]
        else:
            return []

    def normalize_content_type(self, content_type):
        content_type = content_type.lower()
        if content_type in self.known_content_types:
            return content_type
        elif content_type in self.alternate_content_type_extensions:
            return self.alternate_content_type_extensions[content_type]
        else:
            return False

    def set_status(self, given_return_status):
        status_list = {'OK': '200 OK', 'Not Found': '404 Not Found', 'Forbidden': '403 Forbidden',
                       'Server Error': '500 Internal Server Error', 'Not Implemented': '501 Not Implemented'}
        if given_return_status in status_list:
            self.status = status_list[given_return_status]
        else:
            self.status = status_list['Server Error']

    def set_content_type(self, given_content_type):
        if given_content_type in self.known_content_types:
            self.content_type = given_content_type

    def make_response(self):
        if self.content_type == 'html' and not self.raw_html_body:
            output = ['<html>']
            if self.head:
                output.append('<head>')
                output.extend(self.head)
                output.append('</head>')
        else:
            output = []
        if self.body:
            if self.content_type == 'html' and not self.raw_html_body:
                output.append('<body>')
                output.extend(self.html_wrapper_open)
            output.extend(self.body)
            if self.content_type == 'html' and not self.raw_html_body:
                output.extend(self.html_wrapper_close)
                output.append('</body>')
        if self.content_type == 'html' and not self.raw_html_body:
            output.append('</html>')
        self.response = output

    def make_headers(self):
        self.make_response()
        media_type = self.known_content_types[self.content_type].media
        headers = [('Content-type', '%s/%s' % (media_type, self.content_type)),
                   ('Content-Length', '%s' % self.get_response_length())]
        self.headers = headers

    def get_response_length(self):
        return sum(len(line) for line in self.response)

    def add_body(self, body_text):
        self.body.extend(self._listify(body_text))

    def add_head(self, head_text):
        self.head.extend(self._listify(head_text))


def serve_file(response, request, local_path='/'):
    path = request.path_info
    full_path = local_path + path

    if os.path.isfile(full_path):
        file_extension = local_path.split('.')[-1]
        content_type = response.normalize_content_type(file_extension)
        if content_type:
            response.set_content_type(content_type)
            if file_extension == 'html':
                response.raw_html_body = True
        else:
            return unsupported_type(response)

        if response.known_content_types[response.content_type].binary:
            with open(full_path, 'rb') as f:
                response.add_body(f.read())
        else:
            with open(full_path, 'r') as f:
                response.add_body(f.readlines())

    else:
        return not_found(response)

    return response


def not_found(*args):
    response = args[0]
    response.add_body('Not found.')
    response.set_status('Not Found')
    return response


def unsupported_type(*args):
    response = args[0]
    response.add_body('Media type not implemented.')
    response.set_status('Not Implemented')
    return response
