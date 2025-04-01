FROM python:3.13

EXPOSE 8001

RUN python3.13 -m pip install fastapi[standard]
RUN python3.13 -m pip install uvicorn
RUN python3.13 -m pip install httpx
RUN python3.13 -m pip install grpcio grpcio-tools
RUN python3.13 -m pip install asyncpg
RUN python3.13 -m pip install grpcio-reflection
RUN python3.13 -m pip install pytest

RUN curl -L https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.14/grpc_health_probe-linux-amd64 -o /bin/grpc_health_probe && chmod +x /bin/grpc_health_probe

ADD . /gateway-service/

WORKDIR /gateway-service/
