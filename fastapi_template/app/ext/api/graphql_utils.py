from ariadne import ObjectType

from app.core import logger as trace
from app.core.logger import get_logger
from app.core.models.utils import PydanticModel
from app.core.security.security import get_user_or_error
from app.ext.models.graphql import SecureGraphql

logger = get_logger(__name__)


@trace.debug(logger)
def get_populated_object_type(model: PydanticModel) -> ObjectType:
    object_type = ObjectType(model.__name__)
    map_fields_to_resolvers(object_type=object_type, model=model)
    return object_type


@trace.debug(logger)
def map_fields_to_resolvers(object_type: ObjectType, model: PydanticModel):
    for field in model.__fields__:
        map_field_to_resolver(object_type, field)


@trace.debug(logger)
def map_field_to_resolver(object_type: ObjectType, field_name: str):
    @object_type.field(field_name)
    def resolve_field(obj, info):
        return getattr(obj, field_name)


@trace.debug(logger)
async def secure_graphql(info, doc_model):
    request = info.context["request"]
    errors = []
    user, error = await get_user_or_error(request)
    secure = SecureGraphql(user=user)
    if error:
        errors.append(error)
        secure.error = doc_model(errors=errors)
    return secure
