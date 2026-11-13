# Communication recovery and TOU readback

## Why a connected logger can still produce stale data

A logger can accept a TCP connection and then stop responding. Previously each
request allowed five independent ten-second receive waits. A poll continued
through its other register blocks even when one failed, and its next periodic
deadline was computed before doing the work. A slow failed poll could therefore
be followed immediately by another. TCP is a byte stream: a successful `recv()`
can also contain just part of a response, which is not a complete Modbus frame.

The endpoint lock introduced in #323 remains shared by connectors using the
same IP and port, including distinct Modbus unit IDs behind a gateway. This
change adds bounded recovery and coherent polling on top of that serialization.

## Deadlines and snapshots

* TCP connect and send each use at most ten seconds. All response fragments
  share one ten-second monotonic receive deadline. A timeout, EOF, transport
  failure or invalid declared frame length ends that exchange and closes its
  socket. A write is sent once; losing its acknowledgement never causes a resend.
* Both proprietary logger frames and standard Modbus/TCP frames are assembled
  using their declared lengths, with finite size bounds. Protocol validation
  remains in the existing adapters.
* `DEYE_DATA_READ_TIMEOUT` defaults to 60 seconds. One cooperative I/O budget
  covers waiting for transaction/endpoint locks and reading all blocks. TCP
  socket timeouts and AT socket waits/sleeps consume that same remaining budget.
  OS hostname resolution is outside Python's socket timeout guarantees; configure
  the logger's IP address when deterministic network timing matters.
* A failed, short or late block aborts the poll and discards all its partial
  observations. No previous values are relabelled as fresh and no zeros are
  invented. Every configured readiness sensor must be present and nonzero.
* Logger status still means reachability: a valid earlier block can leave it
  online even if the whole poll is incomplete. Check `Acquisition complete=...`
  and `ready=...` in the logs for completeness. Status alone is not a fresh-data
  guarantee. Even with publish-on-change, processors receive failed polls and the
  first successful recovery, including unchanged values.
* Processors and MQTT publication run after releasing the acquisition's I/O
  lock. A complete poll and a multi-batch TOU write use the same per-Modbus-client
  transaction lock, so their register blocks cannot interleave.

## Scheduling and confirmation

Successful periodic polls wait `DEYE_DATA_READ_INTERVAL` seconds from completion.
Failures wait 5, 10, 20 and then at most 30 seconds; a success resets that sequence.
Refresh requests coalesce and cannot bypass a failure cooldown. A physical
post-write confirmation has priority over that cooldown. Requests arriving
during a poll are preserved when another confirmation is still needed.

TOU writes run outside the MQTT callback. The worker holds one executing request
and at most one replaceable pending request, rather than replaying an unbounded
queue. A newer pending request replaces the older one, including its captured
modifications. Send the whole intended modification set in each request.
`reset` clears staged modifications and the pending request; an executing write
is already committed to execution and cannot be cancelled.

Before a write, the baseline must contain every TOU sensor enabled for that
inverter model. No particular model's slot count or voltage sensors are assumed.
The first failed write batch stops the remaining batches. After any attempted
write, the baseline is invalidated and a physical read is requested only after
write completion, including failures with an uncertain hardware outcome.
An incomplete baseline causes rejection and a generic refresh, with no delayed
automatic replay. Resubmit only after observing the actual inverter state.

Acquisition start/completion use process-local monotonic timestamps internally.
A read that began before write completion cannot restore the invalidated TOU
baseline. Confirmation is published even when its values are unchanged and
publish-on-change is enabled. A requested read or successful write acknowledgement
does not itself prove the requested values match: controllers must compare the
fresh read values against their intended configuration.

## Configuration and upgrades

The existing register-range setting is retained with its default of 256:

```dotenv
DEYE_DATA_READ_TIMEOUT=60
DEYE_LOGGER_MAX_REG_RANGE_LENGTH=64
```

For indexed loggers use `DEYE_LOGGER_1_MAX_REG_RANGE_LENGTH=64` (and the
corresponding index for other loggers). The size 64 is an example for a logger
that struggles with large replies, not a universal requirement. Smaller blocks
reduce response sizes but increase transactions and connections. Measure on the
actual device, and increase the total budget if legitimate full acquisitions
need longer. Do not infer a hardware, Wi-Fi or firmware root cause from a timeout.

When upgrading an installation with local overrides:

1. Wait for a released image containing the merged change and verify its commit
   or release notes. An open PR, merge alone or unrelated image tag is insufficient.
2. Preserve the effective block size explicitly through the existing range
   setting. A local `DEYE_ACQUISITION_MAX_REGISTERS` setting is not an upstream
   variable and is not introduced by this change.
3. Compare each override to the released sources. Independent HA control logic,
   custom MQTT provenance/heartbeat protocols and optimizer policies are outside
   this change; do not remove such overrides just because this PR is merged.
4. Keep rollback copies and observe fresh measurements, a natural TOU write and
   its actual readback before retiring the matching communication overrides.

Offline tests exercise framing, budgets, partial snapshots, lock release,
scheduling, callback responsiveness and write/read races without contacting an
inverter. Short healthy field observations motivated this contribution; they
do not establish that all communication failures or provider-side errors are fixed.
