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

import sys
import logging

from deye_cli import main as cli_main
from deye_daemon import main as daemon_main
from deye_config import DeyeConfig, LOG_DEST_STDOUT, LOG_DEST_STDERR


def setupLogging(config: DeyeConfig):
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    supported_log_streams = {
        LOG_DEST_STDOUT: sys.stdout,
        LOG_DEST_STDERR: sys.stderr,
    }
    if config.log_stream not in supported_log_streams.keys():
        err = f"Unsupported log stream {config.log_stream}, supported: {','.join(supported_log_streams.keys())}"
        raise ValueError(err)

    logging.basicConfig(
        stream=supported_log_streams.pop(config.log_stream),
        format=log_format,
        level=logging.getLevelName(config.log_level),
    )


def main():
    try:
        setupLogging(DeyeConfig.from_env())
    except Exception as e:
        print(f"Error setting up logging: {e}", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    if len(args) > 0:
        cli_main()
    else:
        daemon_main()


if __name__ == "__main__":
    main()
