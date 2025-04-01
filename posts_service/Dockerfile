FROM python:3.13

EXPOSE 8003
EXPOSE 50051

RUN python3.13 -m pip install fastapi[standard]
RUN python3.13 -m pip install uvicorn
RUN python3.13 -m pip install httpx
RUN python3.13 -m pip install psycopg2
RUN python3.13 -m pip install sqlalchemy
RUN python3.13 -m pip install grpcio grpcio-tools
RUN python3.13 -m pip install asyncpg
RUN python3.13 -m pip install grpcio-reflection

ADD . /posts-service/

WORKDIR /posts-service/
