FROM python:3.7-alpine

RUN apk --no-cache add \
    build-base \
    libffi-dev postgresql-dev

ADD brewlog /app/brewlog/
COPY requirements*.txt manage.py /app/

WORKDIR /app

RUN pip install -U pip && \
    pip install -U -r requirements-docker.txt

ENV IN_CONTAINER=yes
ENV FLASK_ENV=development
ENV AUTHLIB_INSECURE_TRANSPORT=1

ENTRYPOINT ["gunicorn", "--access-logfile", "-", "--reload", "brewlog.wsgi:application", "--bind=0.0.0.0:8080"]
