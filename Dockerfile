FROM python:3.10.7-alpine3.16 as builder

WORKDIR /build
RUN apk add gcc alpine-sdk linux-lts-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir --target . -r requirements.txt

FROM python:3.10.7-alpine3.16
WORKDIR /opt/deye_inverter_mqtt
ADD *.py ./
COPY --from=builder /build/ ./

CMD [ "python", "./deye_main.py" ]