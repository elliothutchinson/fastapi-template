FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# postgres dependencies
RUN pip install asyncpg

# general dependencies
RUN pip install \
    requests \
    pyjwt \
    passlib[bcrypt] \
    python-multipart \
    tenacity \
    email_validator \
    requests_oauthlib \
    google-auth \
    aiofiles \
    jinja2 \
    emails \
    graphql-core==3.0.0 \
    ariadne \
    starlette-context \
    pyhumps

# app to serve
COPY ./app /app/app
COPY ./start_reload.sh /start_reload.sh
RUN chmod +x /start_reload.sh

# dev dependencies
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs

RUN pip --disable-pip-version-check --no-cache-dir install pylint \
    black \
    vulture \
    isort \
    flake8 \
    autoflake \
    pytest \
    pytest-asyncio

RUN apt-get update \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME\
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/
