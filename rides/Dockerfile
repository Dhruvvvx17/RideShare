FROM python:3.7

EXPOSE 8080

RUN mkdir -p /rides
WORKDIR /rides

COPY ./requirements.txt ./rides

RUN python -m pip install -r requirements.txt

CMD ["/usr/local/bin/gunicorn"]