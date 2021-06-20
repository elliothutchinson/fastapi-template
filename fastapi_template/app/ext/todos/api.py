from ariadne import MutationType, QueryType, make_executable_schema
from ariadne.asgi import GraphQL
from fastapi import APIRouter

from app.core.logger import get_logger
from app.ext.config import ext_config
from app.ext.todos import graphql as todos

logger = get_logger(__name__)

query = QueryType()
mutation = MutationType()

todos.populate_query(query)
todos.populate_mutation(mutation)

schema = make_executable_schema(todos.type_defs, query, mutation, *todos.types)

graphql_router = APIRouter()
graphql_router.add_route(
    ext_config.graphql_path,
    GraphQL(schema, debug=ext_config.graphql_debug),
)
