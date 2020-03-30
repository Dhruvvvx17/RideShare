FROM python:3.7

EXPOSE 8080

RUN mkdir -p /users
WORKDIR /users

COPY ./requirements.txt ./users

RUN python -m pip install -r requirements.txt

CMD ["/usr/local/bin/gunicorn"]