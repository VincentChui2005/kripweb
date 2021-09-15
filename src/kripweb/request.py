from typing import Any


class Request:
    def __init__(self, scope):
        # Usually useful information
        self.form = {}
        self.query_string = {}
        self.host = ""
        self.kwargs = {}

        # Debug information
        self.client = f"{scope['client'][0]}:{scope['client'][1]}"
        self.method = scope['method']
        self.path = scope["path"] if scope["query_string"] == b"" else f"{scope['path']}?{scope['query_string'].decode()}"
        self.http_version = scope["http_version"]

        # Reference
        self._scope = scope

    @classmethod
    async def assemble(cls, scope, receive):
        request = cls(scope)

        # receive -> body -> form
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        if body != b"":
            request.set_form_from_body(body)

        request.set_query_string()
        request.set_host()

        return request

    def set_query_string(self):
        for data in self._scope["query_string"].decode().split("&"):
            if data.find("=") != 1: continue
            k, v = data.split("=")
            self.query_string[k] = v

    def set_form_from_body(self, body: bytes):
        body_str = body.decode()
        things = body_str.split("&")
        for t in things:
            k, v = t.split("=")
            self.form[k] = v

    def set_host(self):
        for item in self._scope["headers"]:
            if item[0] == b"host":
                self.host = item[1].decode()
                break

    def set_extra_url(self, arg_dict: dict[Any]):
        self.kwargs = arg_dict