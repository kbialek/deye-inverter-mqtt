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

"""Cooperative monotonic I/O budgets shared by a poll and its connector calls."""

from contextlib import contextmanager
import threading
import time


class IoBudgetExpired(TimeoutError):
    pass


_state = threading.local()


def io_timeout(maximum: float) -> float:
    deadline = getattr(_state, "deadline", None)
    remaining = maximum if deadline is None else min(maximum, deadline - time.monotonic())
    if remaining <= 0:
        raise IoBudgetExpired("Acquisition I/O budget expired")
    return remaining


@contextmanager
def io_budget(seconds: float):
    previous = getattr(_state, "deadline", None)
    deadline = time.monotonic() + seconds
    _state.deadline = min(previous, deadline) if previous is not None else deadline
    try:
        yield
    finally:
        _state.deadline = previous


@contextmanager
def io_lock(lock, maximum: float = 60):
    if not lock.acquire(timeout=io_timeout(maximum)):
        raise IoBudgetExpired("Timed out waiting for an I/O lock")
    try:
        io_timeout(maximum)
        yield
    finally:
        lock.release()
