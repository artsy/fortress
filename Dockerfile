FROM python:3.10-alpine

RUN adduser --disabled-password --gecos '' deploy
RUN mkdir -p /app
RUN chown deploy:deploy /app

RUN pip --no-cache-dir install poetry

RUN apk --no-cache --quiet add \
  make

WORKDIR /app

COPY . /app

RUN poetry install --without dev

USER deploy
ENV USER deploy
ENV HOME /home/deploy

CMD ["python"]
