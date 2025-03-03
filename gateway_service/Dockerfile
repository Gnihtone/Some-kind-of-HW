FROM python:3.13

EXPOSE 8001

RUN python3.13 -m pip install fastapi[standard]
RUN python3.13 -m pip install uvicorn
RUN python3.13 -m pip install httpx

ADD src/ /gateway-service/

WORKDIR /gateway-service/
