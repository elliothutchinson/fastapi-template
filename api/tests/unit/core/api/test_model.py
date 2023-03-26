from app.core.api import model as uut
from tests.factories.server_response_factory import ServerResponseFactory


def test_ServerResponse():
    server_response = ServerResponseFactory.build(message="testing")

    expected = server_response

    actual = uut.ServerResponse(**server_response.dict())

    assert actual == expected
