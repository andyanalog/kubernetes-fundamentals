FROM alpine:3.18

RUN apk add --no-cache \
    ffmpeg \
    python3 \
    py3-pip \
    py3-requests

COPY worker.py /app/worker.py
COPY requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["python3", "worker.py"]
