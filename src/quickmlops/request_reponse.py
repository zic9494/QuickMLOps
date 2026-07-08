from starlette.types import Scope

class Request:
    def __init__(self, scope: Scope):
        self.scope = scope
        self.path = scope["path"]


class Response:
    def __init__(self):
        pass
    