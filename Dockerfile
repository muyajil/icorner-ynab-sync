FROM python:3.11-slim

RUN pip install requests fastapi uvicorn requests-ratelimiter forex-python


COPY ./ /app

RUN pip install -e /app
ENV PYTHONUNBUFFERED=1
ENTRYPOINT [ "python", "/app/icorner_ynab_sync/main.py" ]