FROM python:3.12-alpine

WORKDIR /app
COPY app/ /app/

ENV PORT=8099 DATA_DIR=/data PYTHONUNBUFFERED=1
EXPOSE 8099

CMD ["python3", "/app/server.py"]
