import inspect
from datetime import datetime
from typing import Any

from pydantic import BaseModel

EVENT_DOC_TYPE = "event"


class EventDb(BaseModel):
    type: str = EVENT_DOC_TYPE
    event_id: str
    event_name: str
    username: str = None
    payload: Any
    date_created: datetime


"""
login success event:
user logs in successfully
submit login success event
save event in db ->
{
  name: LOGIN_SUCCESS
  username: tester
  date_created: 2022-06-06
  payload: null
}
process event -> update user last login date
------------------------

login fail event:
user login invalid credential
exception handler
submit login fail event
save event in db ->
{
  name: LOGIN_FAIL
  username: tester
  date_created: 2022-06-06
  payload: null
}
process event -> noop atm, may implement temp disable, block ip, etc
------------------------

user registered event:
user signs up
submit user register event
save event in db
{
  name: USER_REGISTERED
  username: tester
  date_created: 2022-06-06
  payload: {
      email: tester@example.com
  }
}
process event -> send welcome email, provision s3 bucket folder, etc
------------------------

user forgot password:
user clicks forgot password
submit forgot password event
{
  name: FORGOT_PASSWORD
  username: tester
  date_created: 2022-06-06
  payload: null
}
process event -> send email reset token
------------------------

admin creates user/admin user:
admin creates user
submit admin created user event
{
  name: ADMIN.USER_REGISTERED
  username: tester
  date_created: 2022-06-06
  payload: {
      email: tester@example.com
  }
}
process event -> send welcome email create password
------------------------

"""


class EventProcessor:
    def __init__(self):
        self.events = {}

    def add_event_handler(self, event_name, handler):
        handlers = self.events.get(event_name, set())
        handlers.add(handler)

        if event_name not in self.events:
            self.events[event_name] = handlers

    def default_event_not_supported(self, payload):
        pass

    async def process_event(self, event_name, payload):
        handlers = self.events.get(event_name, {self.default_event_not_supported})

        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
