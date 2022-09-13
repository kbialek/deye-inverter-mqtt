# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

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