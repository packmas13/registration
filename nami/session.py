import requests
import pickle
from atomicwrites import atomic_write


class ResponseTypeError(Exception):
    """
    The response 'responseType' field is not 'OK' or 'INFO'
    """

    pass


class ResponseSuccessError(Exception):
    """
    The response 'success' field is not True
    """

    pass


class SessionExpiredError(Exception):
    """
    The session is expired
    """

    pass


class HTTPError(Exception):
    """
    The http status is not 200
    """

    pass


class Session(object):
    """
    Wrapper around requests.Session (for easy mocking).
    It automatically attempts to log-in when required.
    """

    def __init__(self, config):
        self.s = requests.Session()
        self.config = {
            "server": "https://nami.dpsg.de",
            "auth_url": "/ica/rest/nami/auth/manual/sessionStartup",
        }
        self.config.update(config)

        if self.config["session_file"]:
            try:
                with open(self.config["session_file"], "rb") as f:
                    self.s.cookies.update(pickle.load(f))
            except FileNotFoundError:
                pass

    def _check_response(self, response):
        """
        check if the response looks ok
        """
        if response.status_code != 200:
            raise HTTPError("unexpected status Code: {}".format(response.status_code))

        rjson = response.json()
        if not rjson["success"]:
            if rjson["message"] == "Session expired":
                raise SessionExpiredError
            raise ResponseSuccessError(
                "unexpected success value ({}): {}".format(rjson["message"], rjson)
            )

        # possible response types are: OK, INFO, WARN, ERROR, EXCEPTION
        if rjson["responseType"] not in ["OK", "INFO"]:
            raise ResponseTypeError(
                "unexpected responseType value: {}".format(rjson["responseType"])
            )

        return rjson["data"]

    def login(self):
        """
        Attempt an authentication. Will store the cookies in the object if successful.
        """

        payload = {
            "Login": "API",
            "username": self.config["username"],
            "password": self.config["password"],
        }

        url = self.config["server"] + self.config["auth_url"]
        r = self.s.post(url, data=payload)
        if r.status_code != 200:
            raise HTTPError(
                "authentication failure: unexpected status Code: {}".format(
                    r.status_code
                )
            )

        rjson = r.json()
        if rjson["statusCode"]:
            raise ResponseTypeError(
                "authentication failure: non-null statusCode ({}): {} - {}".format(
                    rjson["statusCode"], rjson["statusMessage"], rjson
                )
            )

        if self.config["session_file"]:
            with atomic_write(
                self.config["session_file"], mode="wb", overwrite=True
            ) as f:
                pickle.dump(self.s.cookies, f)

        return self.s

    def get(self, uri, params=None):
        """
        Perform a get query.
        """
        r = self.s.get(self.config["server"] + uri, params=params)
        try:
            return self._check_response(r)
        except SessionExpiredError:
            self.login()
            r = self.s.get(self.config["server"] + uri, params=params)
            return self._check_response(r)
