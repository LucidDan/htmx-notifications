# #######################################################################
# Docker image definitions
# #######################################################################
ARG PYTHON_VERSION=3.11.4

# #######################################################################
# wheelbuilder - build wheels we need
# #######################################################################
# Intermediate target that builds any wheels we need. These are then
# grabbed into the django image to be used in the virtualenv. We then
# avoid installing any dev tools (gcc, etc) into our main docker image
# This also eliminates most of the need to think about things like using
# any -binary packages such as psycopg2-binary/psycopg[binary].
# #######################################################################
FROM python:${PYTHON_VERSION}-slim AS wheelbuilder

RUN \
    apt-get update --yes --quiet \
    && apt-get dist-upgrade --yes \
    && apt-get install --yes --quiet --no-install-recommends git build-essential curl \
    && python -m pip install --user pipx \
    && python -m pipx ensurepath

COPY pyproject.toml pdm.lock ./

# We use pdm export, because it eliminates the need for pdm to be installed later at all. While it's useful for dev
# environments, less packaging tools is better IMO.
RUN \
    --mount=type=cache,id=pipcache,target=/root/.cache/pip \
    python -m pipx run pdm export -f requirements -o requirements.txt --prod \
    && python -m pip wheel --no-deps --no-input -r requirements.txt --wheel-dir /wheels


# #######################################################################
# basedjango - image for django
# #######################################################################
# Provides the base image for both dev and production deployment. Does not
# set the USER, that's handled in the dev and prod images which inherit
# this one.
# #######################################################################
FROM python:${PYTHON_VERSION}-slim AS django

EXPOSE 8000/tcp

RUN groupadd --gid 1181 --system django \
  && useradd --uid 1181 --system -g django --home /home/django django

ENV PATH=$PATH:/home/django/.local/bin PYTHONPYCACHEPREFIX=/home/django/pycache

RUN \
    apt-get update --yes --quiet \
    && apt-get install --yes --quiet --no-install-recommends git postgresql-client curl \
    && mkdir -p "$PYTHONPYCACHEPREFIX" \
    && mkdir /app \
    && chown django:django /app /home/django

WORKDIR /app

# Copy package spec lock file and install our packages
COPY manage.py ./

# The RUN command below temporarily mounts the wheels from wheelbuilder, so we don't have to
# keep them in our image.
RUN \
    --mount=type=cache,id=pipcache,target=/home/django/.cache/pip \
    --mount=type=bind,from=wheelbuilder,source=/wheels,target=/tmp/wheels,rw \
    python -m pip install --no-cache-dir --no-input /tmp/wheels/* \
    && mkdir -p /app/staticfiles /app/.local

# manage.py for managing the django project, pyproject because we use some data (esp project.version)
COPY pyproject.toml ./

# Pretty much the whole app lives in one directory
COPY demo ./demo

# We use our own management command to launch the ASGI server.
# It uses --insecure because we're likely running behind a traefik or similar SSL proxy
CMD ["python", "manage.py", "runasgi", "--insecure", "--noreload"]

RUN SECRET_KEY=notimportant ALLOWED_HOSTS='*' python ./manage.py collectstatic --noinput --clear --no-color

RUN chown -R django:django /app /home/django

USER django

