import logging

from ariadne import ObjectType

from app.core.models.utils import PydanticModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_populated_object_type(model: PydanticModel) -> ObjectType:
    object_type = ObjectType(model.__name__)
    map_fields_to_resolvers(object_type=object_type, model=model)
    return object_type


def map_fields_to_resolvers(object_type: ObjectType, model: PydanticModel):
    for field in model.__fields__:
        map_field_to_resolver(object_type, field)


def map_field_to_resolver(object_type: ObjectType, field_name: str):
    # field_name_cc = camelize(field_name)

    @object_type.field(field_name)
    def resolve_field(obj, info):
        return getattr(obj, field_name)
