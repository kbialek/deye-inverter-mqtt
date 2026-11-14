# Transactional SG03LP1 MQTT control

This optional controller adds four typed actions using the existing MQTT client,
Modbus connector and transaction lock. No HTTP server, second inverter connection
or additional dependency is required. Existing TOU topics keep their interface;
polling, complete TOU write batches and control transactions share the bus lock.

The supported register map is the single-phase SG03LP1 map. Hardware validation
was performed on a SUN-5K-SG03LP1. Do not enable it for a different register map.
The controller writes only registers 230 (grid-charge current), 232 bit 0 (grid
charge permission), and 244 (work mode). It preserves other bits in 232 and does
not change TOU, battery limits, SOC targets or export settings.

## Configuration

```dotenv
DEYE_FEATURE_LOCAL_CONTROL=true
DEYE_CONTROL_MODEL=sg03lp1
DEYE_CONTROL_STATE_DIR=/var/lib/deye-control
DEYE_CONTROL_WRITES_ENABLED=false
DEYE_CONTROL_MAX_CURRENT=65
DEYE_CONTROL_AUTHORITY=manual
DEYE_METRIC_GROUPS=deye_hybrid,deye_hybrid_battery,deye_hybrid_timeofuse,settings
```

Mount `STATE_DIR` as a persistent writable volume. The journal has private file
permissions, atomic replacement, fsync and a process ownership lock. Losing or
replacing this volume loses deduplication history. It must not be shared by
different bridges. A restart cancels unsent work and marks attempted unfinished
writes uncertain; it never replays a positive command or restores a manual session.

Writes require `WRITES_ENABLED=true`. With the default `AUTHORITY=manual`, they
also require an explicit five-minute session confirming an exclusive window.
This does not pause other writers. Cloud apps and external Modbus clients are
outside the local lock; coordinate them before enabling writes. `AUTHORITY=service`
is an explicit deployment choice for a sole automation authority; it disables
manual sessions and removes their time requirement. All other checks still apply.

Do not enable the old `DEYE_FEATURE_BATTERY_SETTINGS` or `DEYE_FEATURE_WORKMODE`
scalar writers together with this feature; startup rejects that combination.
They lack the transactional policy. `MAX_CURRENT` defaults to 65 A and may be
configured from 1 to 240 A; every command is also checked against the current
inverter maximum at register 210.

For multiple loggers, override settings as `DEYE_CONTROL_<index>_MODEL`,
`DEYE_CONTROL_<index>_STATE_DIR`, etc. Each enabled logger must explicitly match
the supported map. Logger zero uses `STATE_DIR` directly; other indexes use a
`logger-<index>` subdirectory. The logger's configured Modbus unit is preserved.

MQTT broker authentication and ACLs are the authority boundary. Restrict request
publication and session creation to authorized clients. Use the existing TLS
settings when required by the deployment. Control messages never use the global
retained-publication setting.

## Topics and request envelope

The prefix is `MQTT_TOPIC_PREFIX` for logger zero, or
`MQTT_TOPIC_PREFIX/<index>` for other loggers:

| Topic suffix | Direction | Meaning |
| --- | --- | --- |
| `control/request` | client → bridge | JSON RPC, QoS 1, `retain=false` |
| `control/result` | bridge → clients | Correlated RPC replies and command events, QoS 1, non-retained |
| `control/state` | bridge → clients | Current snapshot on changes and every 10 s, QoS 1, non-retained |

```json
{"schema":1,"request_id":"rpc_unique_0001","op":"status","body":{}}
```

`request_id` and command `id` use 8–80 ASCII letters, digits, `_` or `-`.
Subscribe to results before publishing. RPC replies contain `schema`, `request_id`,
`op`, `ok`, and either `result` or `error`/`status`. A broker PUBACK only confirms
transport. A successful `submit` reply means the intent was journaled; query
`get` until the command is terminal. A later event has
`{"schema":1,"event":"command","command":{...}}`; use its command ID.

The callback rejects retained deliveries, malformed/oversized messages and
queues requests without doing device I/O. OFF has reserved queue capacity and
priority. Full queues may discard a request without a reply; consult its ID
before deciding what happened. Publication never waits for a broker ACK while
holding the bus lock. State/result messages can be missed during an outage;
recover using `status` and `get` after reconnecting.

Supported operations:

| `op` | `body` | Device I/O |
| --- | --- | --- |
| `status` | `{}` | None; cached coherent acquisition |
| `preview` | Typed command | None; validates cached state/revision |
| `get` | `{"id":"command_unique_0001"}` | None; durable command result |
| `session` | `{"exclusive_window_confirmed":true}` | None; manual authority for 300 s |
| `submit` | Typed command with explicit ID and deadline | Asynchronous pre-read, write and readback |

`session` additionally requires an envelope `expires_at` between now and 60 s
in the future. Re-delivering its exact request ID returns the original response
without extending authority, including after restart. An altered payload with
the same ID conflicts. A cached expiry is not proof that a session is still active;
check `status.manual_session_active`.

## Typed commands

```json
{
  "schema": 1,
  "request_id": "rpc_unique_0002",
  "op": "submit",
  "body": {
    "id": "command_unique_0001",
    "action": "grid_on",
    "ampere": 5,
    "expected_revision": "<64 hexadecimal characters from status.sample.revision>",
    "expires_at": 0
  }
}
```

Replace `expires_at` with a Unix UTC timestamp within the next 60 s (normally
30 s), and the revision with the current configuration hash. Both ID and expiry
must be created by the publisher before its first transmission. Reuse the exact
body when recovering delivery; do not generate a new positive command after a
timeout. Duplicate IDs return the original record, even after expiry or restart;
changed payloads conflict. Unknown command fields are rejected.

| Action | Fields | Behavior |
| --- | --- | --- |
| `grid_on` | `ampere`: 1…cap, optional `work_mode`, revision | Set current/mode before enabling bit 0 |
| `grid_off` | No current/mode/revision required | Disable bit 0 before setting current to zero |
| `set_current` | `ampere`: 0…cap, revision for positive values | Preserve permission; zero becomes OFF |
| `set_mode` | `work_mode`, revision | Disable permission before changing mode, then restore it |

Modes are `SELLING_FIRST` (0), `ZERO_EXPORT_TO_LOAD` (1) and `ZERO_EXPORT_TO_CT` (2).
The live validation covered modes 1 and 2; mode 0 was not exercised.

Before a positive write the executor rereads the full relevant configuration
under the shared lock and checks its revision, grid connection, battery voltage,
SOC, current limit, authority, expiry and any queued protective OFF. OFF only
requires its own registers, so missing TOU telemetry cannot block a cut. An OFF
cancels queued positives and invalidates an in-flight positive before its next
write. It cannot undo a write already transmitted.

Each write is attempted once. A lost/invalid ACK is uncertain; it is never
silently retried. Readback may retry reads four times with short delays, retaining
strict unit/function/count/length/CRC validation. Confirmed OFF may supersede an
older local uncertain command. It says nothing about a delayed cloud command.

Terminal states are `confirmed`, `failed`, `expired`, `cancelled`, `uncertain`.
`write_attempted=false` indicates no device write was initiated by this executor.
`registers_confirmed=true` means subsequent physical reads agreed. The separate
`physical_confirmed` remains false: register agreement does not establish that
grid power actually flowed. TOU, target SOC, PV supply and BMS may prevent charge.
Never use a timeout or an uncertain result to trigger a second executor.

`status` includes physical acquisition start/end timestamps, a configuration
revision, boot ID and read sequence. Availability requires a complete acquisition
no older than 90 s from its start, with ordered timestamps and no future time.
Failure invalidates availability even when a previous sample remains visible.
These checks do not establish exclusive ownership against external writers.

## CLI

The included client reads existing MQTT configuration internally and opens no
inverter connection. For a running container named `deye-mqtt`:

```sh
docker exec deye-mqtt python -m deye_control_cli status
docker exec deye-mqtt python -m deye_control_cli preview '<command JSON>'
docker exec deye-mqtt python -m deye_control_cli session '{"exclusive_window_confirmed":true}'
docker exec deye-mqtt python -m deye_control_cli command '<command JSON>'
docker exec deye-mqtt python -m deye_control_cli get command_unique_0001
```

`command` creates a missing ID/deadline once before publication. The client sends
one RPC and waits for its correlated application reply. A timeout after publication
is reported uncertain with IDs; it does not automatically send again or fall back
to cloud. Use `--logger-index N` for another logger. Configure the same MQTT
environment when running the client outside the container.

## Validation scope

Tests use synthetic hardware and block real network connections. They exercise
durability, duplicate/restart behavior, OFF priority, expiry, readback failures,
protocol validation, authority, configuration races and shared bus locking.
The installed SUN-5K-SG03LP1 was separately validated with small current changes,
grid permission ON/OFF and modes 1↔2, restoring the initial configuration.
WAN isolation and actual grid-energy transfer remain separate operational tests.
