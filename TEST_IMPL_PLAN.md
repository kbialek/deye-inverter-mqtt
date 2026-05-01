# Test Implementation Plan — Coverage Increase

## Current State

| Metric | Value |
|--------|-------|
| **Overall coverage** | 85% (3,044 stmts / 362 missed / 326 branches) |
| **Tests collected** | 96 |
| **Tests passing** | 96 |

---

## Priority 1 — `deye_modbus.py` (78% → 95%)

### Why
The file has clear error paths that are never exercised: CRC mismatches, short frames, address/count mismatches in responses. These are easy to test with a mock connector.

### What's missing

| Lines | Description | Testability |
|-------|-------------|-------------|
| 89 | `read_registers()` returns `{}` when connector returns `None` | ✅ Mock connector |
| 109 | Short frame error in read response parsing | ✅ Mock connector returns short frame |
| 123–124 | CRC mismatch error in read response | ✅ Mock connector returns bad CRC |
| 128–131 | `__parse_modbus_write_holding_register_response` — short frame | ✅ Mock connector returns short frame |
| 155–158 | Write response CRC mismatch | ✅ Mock connector returns bad CRC |
| 162–165 | Returned address mismatch | ✅ Mock connector returns wrong address |
| 169–172 | Returned register count mismatch | ✅ Mock connector returns wrong count |
| 174–177 | Successful write (already tested — these lines are likely branch parts) | Already covered |

### Implementation Steps

#### Step 1: Test `read_registers` with no response
**File:** `tests/deye_modbus_tcp_test.py`  
**Test:** `test_read_registers_returns_empty_on_connector_failure`
- Mock connector to return `None`
- Call `modbus.read_registers(0, 5)`
- Assert result is `{}`

#### Step 2: Test read response CRC mismatch
**File:** `tests/deye_modbus_tcp_test.py`  
**Test:** `test_read_registers_crc_mismatch_returns_empty`
- Build a valid read response frame but corrupt the last 2 CRC bytes
- Mock connector to return the bad frame
- Assert result is `{}`

#### Step 3: Test short frame detection in read response
**File:** `tests/deye_modbus_tcp_test.py`  
**Test:** `test_read_registers_short_frame_returns_empty`
- Send a frame shorter than expected (e.g., just 4 bytes)
- Assert result is `{}`

#### Step 4: Test write response CRC mismatch
**File:** `tests/deye_modbus_tcp_test.py`  
**Test:** `test_write_register_crc_mismatch_returns_false`
- Build a valid write response frame but corrupt the last 2 CRC bytes
- Mock connector to return the bad frame
- Call `modbus.write_registers(0, [bytearray.fromhex("00ff")])`
- Assert result is `False`

#### Step 5: Test write response wrong address
**File:** `tests/deye_modbus_tcp_test.py`  
**Test:** `test_write_register_address_mismatch_returns_false`
- Build a valid write response frame with correct CRC, but register address field says `0x0002` instead of expected `0x0000`
- Assert result is `False`

#### Step 6: Test write response wrong register count
**File:** `tests/deye_modbus_tcp_test.py`  
**Test:** `test_write_register_count_mismatch_returns_false`
- Build a valid write response frame with correct CRC, but register count field says `1` instead of expected `2`
- Assert result is `False`

---

## Priority 2 — `deye_timeofuse_service.py` (50% → 90%)

### Why
The existing test only covers `process()` and one `handle_command()` call. The critical `write_config()` flow with its register batch writing logic is completely untested.

### What's missing

| Lines | Description | Testability |
|-------|-------------|-------------|
| 44 | Early return in `write_config` when `read_state` is empty | ✅ Direct call |
| 47 | `dry_run=True` — calls `_DeyeTimeOfUseService__write_registers` but not modbus | ✅ Mock modbus |
| 51 | `dry_run=False` — actually writes via modbus | ✅ Mock modbus, assert write call |
| 64 | `handle_control_command` with `"reset"` payload | ✅ Direct call |
| 71–77 | Register batch writing with gaps (gap triggers flush before gap) | ✅ Mock modbus, assert calls |
| 80–88 | The loop in `__write_registers` — full batch write path | ✅ Mock modbus |
| 91–107 | Various register mapping edge cases | ✅ Multiple test scenarios |

### Implementation Steps

#### Step 1: Test `write_config` with empty read state
**File:** `tests/deye_timeofuse_service_test.py`  
**Test:** `test_write_config_early_return_when_no_read_state`
- Create service, but do not call `process()` (so `read_state` is empty)
- Call `sut.write_config(dry_run=False)`
- Assert no modbus write occurred

#### Step 2: Test control command `reset`
**File:** `tests/deye_timeofuse_service_test.py`  
**Test:** `test_handle_control_command_reset_clears_modifications`
- Create service, set some modifications via `handle_command()`
- Call `handle_control_command(None, None, MQTTMessage(payload=b"reset"))`
- Assert `sut.modifications` is empty

#### Step 3: Test control command `dry-write` (dry_run=True)
**File:** `tests/deye_timeofuse_service_test.py`  
**Test:** `test_handle_control_command_dry_write_no_modbus_call`
- Set read_state and modifications
- Call `handle_control_command(None, None, MQTTMessage(payload=b"dry-write"))`
- Assert modbus `write_registers` was never called

#### Step 4: Test control command `write` (dry_run=False) — single batch
**File:** `tests/deye_timeofuse_service_test.py`  
**Test:** `test_handle_control_command_write_sends_modbus`
- Set read_state and modifications on consecutive registers (e.g., 148, 149)
- Call `handle_control_command(None, None, MQTTMessage(payload=b"write"))`
- Assert modbus `write_registers` was called with correct register address and values

#### Step 5: Test control command `write` — batch with gaps
**File:** `tests/deye_timeofuse_service_test.py`  
**Test:** `test_handle_control_command_write_handles_gaps_in_registers`
- Set modifications on non-consecutive registers (e.g., 148 and 150, but not 149)
- Call `handle_control_command(None, None, MQTTMessage(payload=b"write"))`
- Assert modbus `write_registers` was called correctly to handle the gap

---

## Priority 3 — `deye_active_power_regulation.py` (70% → 95%)

### Why
The existing tests cover valid values and out-of-range values. Missing: boundary conditions and logging paths.

### What's missing

| Lines | Description | Testability |
|-------|-------------|-------------|
| 40–41, 43–44 | Logging of regulatory action (at exact min/max boundaries) | ✅ pytest caplog |
| 48 | `max_power` parameter edge case | ✅ Direct instantiation |
| 51 | Minimum power boundary handling | ✅ Direct call with boundary value |
| 54–60 | Regulation decision logic branches | ✅ Multiple test values |
| 67–69 | Logging when regulation returns to nominal | ✅ pytest caplog |

### Implementation Steps

#### Step 1: Test exact min/max boundary values
**File:** `tests/deye_active_power_regulation_test.py`  
**Test:** `test_handle_value_at_exact_min_boundary`
- Set up regulation with min=0, max=100
- Pass value exactly equal to `min` (e.g., 0.0)
- Assert the returned regulated value is correct and logging captured

#### Step 2: Test exact max boundary value
**File:** `tests/deye_active_power_regulation_test.py`  
**Test:** `test_handle_value_at_exact_max_boundary`
- Set up regulation with min=0, max=100
- Pass value exactly equal to `max` (e.g., 100.0)
- Assert the returned regulated value is correct and logging captured

#### Step 3: Test nominal range (no regulation needed)
**File:** `tests/deye_active_power_regulation_test.py`  
**Test:** `test_handle_value_in_nominal_range_returns_unmodified`
- Set up regulation with min=10, max=90
- Pass value in middle of range (e.g., 50.0)
- Assert returned value equals input

#### Step 4: Test logging of regulatory action
**File:** `tests/deye_active_power_regulation_test.py`  
**Test:** `test_handle_value_logs_clamping_action`
- Set up regulation with min=10, max=90
- Pass value above max (e.g., 95.0)
- Assert log captured the clamping message at DEBUG/INFO level

---

## Priority 4 — `deye_config.py` (64% → 80%)

### Why
The missing lines are typed config getters (`get_optional_string`, `get_integer`) for settings-specific parameters. These aren't exercised because no active test sensor group uses the "settings" configuration path.

### What's missing

| Lines | Description | Testability |
|-------|-------------|-------------|
| 42–45, 55, 57, 59 | Optional/typed getter code paths not triggered by current config fixtures | ✅ New dedicated test class |
| 97, 101, 105, 109 | Settings-specific parameter getters | ✅ Create settings-like config fixture |
| 149, 181, 184, 186, 188 | Section parsing edge cases | ✅ New fixture |
| 199, 203, 213 | Nested section handling | ✅ New fixture |
| 244 | Missing optional string in deep path | ✅ New fixture |
| 264–287, 291, 295–312 | Settings file parsing logic | ✅ Hard — requires realistic INI content |

### Implementation Steps

#### Step 1: Test typed getters with explicit fixtures
**File:** `tests/deye_config_test.py`  
**Test:** `test_get_optional_string_returns_none_when_missing`
- Create config with section but missing key
- Call `get_optional_string("section", "missing_key")`
- Assert returns `None`

#### Step 2: Test `get_integer` with valid and invalid values
**File:** `tests/deye_config_test.py`  
**Test:** `test_get_integer_with_valid_value`, `test_get_integer_with_invalid_value_raises`
- Use a config fixture with an integer in a section
- Also test a non-integer value to trigger the exception path

#### Step 3: Test nested section handling
**File:** `tests/deye_config_test.py`  
**Test:** `test_get_integer_from_nested_section`
- Create config with `[section.subsection]` structure
- Call typed getter with nested section name

> **Note:** The settings file parsing (lines 264–312) is tied to real inverter configuration files. Consider accepting this partial coverage or adding one integration-style test with a minimal realistic INI blob.

---

## Priority 5 — `deye_sensor.py` (80% → 90%)

### Why
The missing lines correspond to sensor types and register range scenarios not exercised by the current 5 active sensor groups. The file is large (367 stmts) because it defines all base sensor class logic.

### What's missing

| Lines | Description | Testability |
|-------|-------------|-------------|
| 32–79 | Sensor `write_value` paths for various types (not exercised by read-only tests) | ✅ Create write scenario tests |
| 163, 169, 172, 175, 178 | Sensor-specific value formatting edge cases | ✅ Unit test sensor instances directly |
| 201, 209, 213, 217, 221 | Register data unpacking with different endianness | ✅ Mock register bytes |
| 316, 322, 326–327, 335 | DateTime parsing edge cases | ✅ Create datetime sensor with bad input |
| 356, 360 | Sensor reset/override logic | ✅ Unit test reset behavior |
| 379 | Sum sensor with specific register layout | ✅ Mock data |
| 407–412, 415 | Signed magnitude unpacking edge case | ✅ Mock register bytes |
| 446 | High-word-first byte order handling | ✅ Create register data with swapped words |
| 458–464 | Additional sensor type branches | ✅ Depends on which types are missing |
| 484, 490–494, 497, 501, 504 | Multi-register sensor scenarios | ✅ Create test data for these patterns |
| 529, 536, 539, 567, 573, 579 | Sensor-specific computed paths | ❌ Hard — depends on sensor groups not in tests |

### Implementation Steps

#### Step 1: Test sensor write_value for a numeric sensor
**File:** `tests/deye_sensor_test.py`  
**Test:** `test_numeric_sensor_write_value_unsigned`
- Create a `NumericSensor` with write support
- Call `write_value("255")` on it
- Assert returns correct register map

#### Step 2: Test high-word-first byte order
**File:** `tests/deye_sensor_test.py`  
**Test:** `test_double_register_high_word_first_ordering`
- Create a double-register sensor with `register_byte_swap=True`
- Feed register data where word order is swapped
- Assert correct value extraction

#### Step 3: Test signed magnitude with specific edge case
**File:** `tests/deye_sensor_test.py`  
**Test:** `test_signed_magnitude_zero_value`
- Create a signed magnitude sensor
- Feed register bytes representing zero
- Assert returned value is `0.0` (not negative zero or error)

> **Note:** Many remaining gaps in `deye_sensor.py` are tied to sensor groups (`deye_sg01hp3`, etc.) whose data is never passed through the test pipeline. Consider using `coverage: exclude` for unreachable computed-sensor paths rather than forcing integration-level tests.

---

## Summary of Expected Impact

| Priority | File | Current → Target | Tests Added | Est. Coverage Gain |
|----------|------|-------------------|-------------|--------------------|
| 1 | `deye_modbus.py` | 78% → 95% | 6 tests | +3–4% |
| 2 | `deye_timeofuse_service.py` | 50% → 90% | 5 tests | +3–4% |
| 3 | `deye_active_power_regulation.py` | 70% → 95% | 4 tests | +1–2% |
| 4 | `deye_config.py` | 64% → 80% | 4 tests | +1–2% |
| 5 | `deye_sensor.py` | 80% → 90% | 3 tests | +1% |
| **Total** | | | **~22 new tests** | **+9–13%** |

**Target: ~94–98% overall coverage**

---

## Not Worth Pursuing (Accept as-Is)

### `deye_at_connector.py` (21%)
Pure socket I/O. Already covered by `test-at-connector` integration test. Only the static method `extract_modbus_response` is unit-testable — but it already has 100% test coverage in `deye_at_connector_test.py`. The remaining lines are actual network operations that cannot be unit-tested without a real device or extensive mocking of socket internals.

**Recommendation:** Add `# pragma: no cover` to `__create_socket`, `__send_at_command`, `__receive_at_command` wrapper methods, or accept partial coverage with integration test guard.

### `deye_mqtt.py` (43%)
Requires a real MQTT broker for most code paths. The `test-mqtt` integration target exists. Unit tests already cover `build_topic_name` and `extract_command_topic_suffix`. The remaining lines are network operations (`connect()`, `publish()`, `disconnect()`).

**Recommendation:** Accept partial coverage with existing integration test guard. Add `coverage: exclude` for broker-dependent methods.

### `src/deye_config.py` settings parsing (lines 264–312)
These lines parse `.ini`-style inverter configuration files that are device-specific and large. Covering them fully would require realistic config file fixtures with dozens of settings entries.

**Recommendation:** Accept partial coverage or add one integration-style test with a minimal INI blob if time permits.

---

## Execution Order (Recommended)

1. **Priority 1** (modbus errors) — Fastest win, pure mock-based tests
2. **Priority 3** (active power regulation) — Already well-structured test file
3. **Priority 2** (timeofuse service) — Needs understanding of write_config flow
4. **Priority 4** (config typed getters) — Straightforward fixture extension
5. **Priority 5** (sensor edge cases) — Most complex, many gaps are sensor-group specific
