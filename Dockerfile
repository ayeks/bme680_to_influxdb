FROM python:3.9.18-slim
WORKDIR /opt/bme
COPY requirements.txt ./

RUN apt-get update -y && \
    apt-get install -y gcc make python3-dotenv && \
    pip3 install -r requirements.txt && \
    apt-get purge -y gcc make && \
    rm -rf /root/.cache/ && \
    rm -rf /var/lib/apt /var/lib/dpkg

COPY senddata.py .
CMD ["python3", "/opt/bme/senddata.py", "/opt/bme/config.ini"]