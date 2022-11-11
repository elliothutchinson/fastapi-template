from app.core.api import model as uut


def test_ServerResponse():
    server_response_dict = {"message": "test"}

    actual = uut.ServerResponse(**server_response_dict)

    assert actual.dict() == server_response_dict
