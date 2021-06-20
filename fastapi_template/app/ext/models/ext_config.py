from pydantic import BaseModel


class ExtConfig(BaseModel):
    graphql_path: str = "/graphql"
    graphql_debug: bool = False
    todos_path: str = "/todos"
