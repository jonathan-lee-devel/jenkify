FROM python:3.12-alpine3.18

RUN pip install poetry==1.5.1

# A locale needs to be installed and set for later use by some python packages like click
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Prevents run-time type-checking causing issues in production
ENV PYTHONOPTIMIZE=true

# Store all of the packages under the /usr/src/app/ directory
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app
COPY poetry.lock pyproject.toml /usr/src/app/

# We turn off virtual env as not needed inside the container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rptrc code into the image
COPY jenkify /usr/src/app/jenkify/

# Run the rptrc
ENTRYPOINT ["python", "-m", "jenkify"]
