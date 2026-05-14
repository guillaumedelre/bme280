FROM python:3.12-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM base AS test

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

CMD ["pytest", "tests/", "-v", "--tb=short"]


FROM base AS app

COPY bme280.py sensor_api.py ./

EXPOSE 5000

CMD ["python", "sensor_api.py"]
