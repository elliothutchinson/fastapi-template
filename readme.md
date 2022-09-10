# todo:
* fire event when login fail attempt
* partial update support
* get_verified_token check for redacted tokens (nonexpired redacted token, user disabled)
* catch up on tests
* reconsider how logging works
* use token for token obj, and access_token for str
* create default admin user, temp token first startup, require pw change
* support admin provision user for others
* admin endpoint
* look into rate limit
* lock after n failed login attemps
* transaction support
* perf tests


# testing with coverage
`pytest --cov=app tests --cov-branch --cov-report term-missing`
`pytest --cov=app tests --cov-branch --cov-report html:coverage`

# mutation testing
`mutmut run`
`mutmut html`

# generate docs
`pdoc --html --output-dir docs app`

# before docker compose
`rm -r ../_tmp/html/`