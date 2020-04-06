FROM python:3.7

# EXPOSE 8000 not needed here since already done in compose file

WORKDIR /rides
#app-> instance to docker

COPY . .

RUN python -m pip install -r requirements.txt

ENV TEAM_NAME = CC_186_281
ENV PYTHON_PATH /usr/local/lib/python3.7/site-packages

CMD ["python","ridemain.py"]
