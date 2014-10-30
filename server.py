from time import sleep


class Server:
    def __init__(self, username, password):
        sleep(2)
        self._authenticate(username, password)

    def _authenticate(self, username, password):
        if username == 'test' and password == 'test':
            pass
        else:
            raise AuthError()


class AuthError(Exception):
    pass
