FROM python:3.12-slim
LABEL maintainer="Dmitry Muzyka"

RUN pip install --no-cache-dir influxdb==5.3.2 numpy

COPY nginx2influx.py /app/

ENTRYPOINT ["python3", "/app/nginx2influx.py"]
CMD ["/var/log/monitored/access.log"]
