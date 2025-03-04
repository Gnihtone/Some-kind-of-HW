FROM python:3.13

EXPOSE 8002

RUN python3.13 -m pip install fastapi[standard]
RUN python3.13 -m pip install uvicorn
RUN python3.13 -m pip install httpx
RUN python3.13 -m pip install psycopg2
RUN python3.13 -m pip install sqlalchemy

ADD src/ /userdata-service/

WORKDIR /userdata-service/
