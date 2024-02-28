import sys

from mongoengine import connect, disconnect

from konbinein.settings import MONGO


class MongoConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if sys.argv[1] == "test":
            return self.get_response(request)
        else:
            connect(**MONGO["default"])
            try:
                return self.get_response(request)
            finally:
                disconnect()
