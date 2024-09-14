FROM python:3.10-slim

RUN mkdir delivery_fastapi
WORKDIR delivery_fastapi
ADD requirements.txt /delivery_fastapi/
RUN pip install -r requirements.txt
ADD . /delivery_fastapi/
ADD .env.docker /online_store_bot/.env
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload