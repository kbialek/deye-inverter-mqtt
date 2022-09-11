FROM python:3.10.7-alpine3.16 as builder

WORKDIR /build
RUN apk add gcc alpine-sdk linux-lts-dev
COPY requirements.txt ./
# Use symlink as a workaround for pip crashes during non x64 platform builds
RUN ln -s /bin/uname /usr/local/bin/uname \
    && pip install --no-cache-dir --target . -r requirements.txt

FROM python:3.10.7-alpine3.16
WORKDIR /opt/deye_inverter_mqtt
ADD *.py ./
COPY --from=builder /build/ ./

CMD [ "python", "./deye_main.py" ]