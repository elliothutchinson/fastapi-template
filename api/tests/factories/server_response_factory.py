from factory import Faker

from app.core.api.model import ServerResponse

from .base_factory import BaseFactory


class ServerResponseFactory(BaseFactory):
    message = Faker("pystr")

    class Meta:
        model = ServerResponse
