from datetime import datetime
from beanie import Document, Indexed
from pydantic import BaseModel


"""
"home": [
    {
        "task": "wash dog",
        "completed": false,
    }
]
"""

"""
user use cases:
register
login
logout
update user info
view user info

todos use cases:
create todo
update todo
delete todo
view todos

lists use cases:
create list
update list
view todo lists
delete list with todos


get all todos
GET
/todos
optional filter
?list=asdf&include_complete=false

create todo
POST
/todos

update todo
PUT
/todos/<todo_id>

delete todo
DELETE
/todos/<todo_id>

get all lists
GET
/lists

create list
POST
/lists

update list
PUT
/lists/<list_id>

delete list
DELETE
/lists/<list_id>


get all lists
get all todos w/ filter
delete list deletes all todos from list
crud list
crud todo

filter:
list
include_complete


todo_public:
todo_id
list_id
task


todo_db:
todo_id
list_id
username
task
completed
date_created
date_modified


todo list:
list_id
username
list_name
date_created
date_modified
"""


class TodoListDb(BaseModel):
    todo_list_id: Indexed(str, unique=True)
    username: str
    name: str
    date_created: datetime
    date_modified: datetime = None





class Todo(BaseModel):
    todo_id: str
    todo_list_id: str
    task: str
    completed: bool


class TodoDb(Document):
    todo_id: Indexed(str, unique=True)
    todo_list_id: str
    username: str
    task: str
    completed: bool
    date_created: datetime
    date_modified: datetime = None
