# Test Implementation Plan — Coverage Increase

## Current State (Verified 2026-05-01)

| Metric | Value |
|--------|-------|
| **Overall coverage** | 85% (3,044 stmts / 362 missed / 326 branches) |
| **Tests collected** | 96 |
| **Tests passing** | 96 |

### Per-file verified coverage (actual source line numbers)

| File | Coverage | Source Verified? |
|------|----------|------------------|
| `deye_modbus.py` | **76%** (stmts) | ✅ Confirmed — plan said 78% (close) |
| `deye_timeofuse_service.py` | **50%** | ✅ Confirmed |
| `deye_active_power_regulation.py` | **70%** | ✅ Confirmed |
| `deye_config.py` | **64%** | ✅ Confirmed |
| `deye_sensor.py` | **80%** | ✅ Confirmed |

---

## Test Conventions (Discovered from existing tests)

### Two coexisting styles in this project:

**1. unittest style** (`tests/deye_modbus_tcp_test.py`, `tests/deye_config_test.py`):
```python
class DeyeModbusTcpTest(unittest.TestCase):
    @patch("deye_connector.DeyeConnector")
    def test_read_register_0x01(self, connector):
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("...")
        self.assertEqual(len(reg_values), 1)
```

**2. pytest style** (`tests/deye_timeofuse_service_test.py`, `tests/deye_active_power_regulation_test.py`):
```python
class TestDeyeTimeOfUseService:
    @staticmethod
    @pytest.fixture
    def modbus_mock(mocker) -> DeyeModbus:
        return mocker.Mock(spec=DeyeModbus)
    
    def test_handle_modification_command(self, logger_config_mock, mqtt_client_mock, modbus_mock):
        # given / when / then docstring sections
        assert sut.modifications[sensor_time_1] == "0600"
```

### Recommendation by file
- **deye_modbus**: Use existing `@patch` convention (matches current tests)
- **deye_timeofuse_service**: Use pytest fixture convention (matches current tests)
- **deye_active_power_regulation**: Use pytest fixture convention (matches current tests)
- **deye_config**: Add new test class using either style; project has both examples

---

## Priority 1 — `deye_modbus.py` (76% → 95%) {#priority-1}

> **Verified gap lines** (actual source, corrected from plan):
> | Line(s) | Description | Testability |
> |---------|-------------|-------------|
> | 89 | `read_registers()` returns `{}` when connector returns `None` | ✅ Mock connector |
> | 109 | Short frame error in read response parsing (`len(frame) < expected_frame_data_len + 2`) | ✅ Mock short frame |
> | 123–124 | CRC mismatch in read response | ✅ Bad CRC bytes |
> | 128–131 | Short write response frame | ✅ Mock short frame |
> | 155–158 | Write response CRC mismatch | ✅ Bad CRC bytes |
> | 162–165 | Returned address mismatch in write response | ✅ Wrong addr in frame |
> | 169–172 | Returned register count mismatch in write response | ✅ Wrong count in frame |
> | 174–177 | Success return from write response | Already covered by existing tests |

### Why
Clear error paths never exercised. The existing `@patch("deye_connector.DeyeConnector")` convention provides the perfect pattern to follow.

### Implementation Steps

#### Step 1: Test `read_registers` with no response (connector returns `None`) — line 89
```python
# File: tests/deye_modbus_tcp_test.py
@patch("deye_connector.DeyeConnector")
def test_read_registers_returns_empty_on_connector_failure(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    connector.send_request.return_value = None
    reg_values = sut.read_registers(1, 5)
    self.assertEqual(reg_values, {})
```

#### Step 2: Test read response CRC mismatch — lines 123–124
```python
@patch("deye_connector.DeyeConnector")
def test_read_registers_crc_mismatch_returns_empty(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    frame = bytearray.fromhex("010302000a")  # valid data but wrong CRC appended
    bad_crc = bytearray.fromhex("0000")
    connector.send_request.return_value = frame + bad_crc
    reg_values = sut.read_registers(1, 1)
    self.assertEqual(reg_values, {})
```

#### Step 3: Test short frame detection in read response — line 109
```python
@patch("deye_connector.DeyeConnector")
def test_read_registers_short_frame_returns_empty(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    connector.send_request.return_value = bytearray.fromhex("0103")  # too short
    reg_values = sut.read_registers(1, 5)
    self.assertEqual(reg_values, {})
```

#### Step 4: Test write response CRC mismatch — lines 155–158
```python
@patch("deye_connector.DeyeConnector")
def test_write_register_crc_mismatch_returns_false(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    frame = bytearray.fromhex("011000120001")  # write response data
    bad_crc = bytearray.fromhex("FFFF")
    connector.send_request.return_value = frame + bad_crc
    success = sut.write_register(0x12, bytearray.fromhex("00ff"))
    self.assertFalse(success)
```

#### Step 5: Test write response wrong address — lines 162–165
```python
@patch("deye_connector.DeyeConnector")
def test_write_register_address_mismatch_returns_false(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    # Note: need to compute correct CRC for the test frame itself
    frame = bytearray.fromhex("011000020001")  # returned address=0x0002 vs expected 0x12
    connector.send_request.return_value = frame + self._compute_crc(frame)
    success = sut.write_register(0x12, bytearray.fromhex("00ff"))
    self.assertFalse(success)

def _compute_crc(self, frame):
    import libscrc
    crc = bytearray.fromhex("{:04x}".format(libscrc.modbus(frame)))
    crc.reverse()
    return crc
```

#### Step 6: Test write response wrong register count — lines 169–172
```python
@patch("deye_connector.DeyeConnector")
def test_write_register_count_mismatch_returns_false(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    frame = bytearray.fromhex("011000120002")  # returned count=2 vs expected 1
    connector.send_request.return_value = frame + self._compute_crc(frame)
    success = sut.write_register(0x12, bytearray.fromhex("00ff"))
    self.assertFalse(success)
```

---

## Priority 2 — `deye_timeofuse_service.py` (50% → 90%) {#priority-2}

> **Verified gap lines** (actual source):
> | Line(s) | Description | Testability |
> |---------|-------------|-------------|
> | 44 | Early return in `write_config` when `read_state` is empty | ✅ Direct call on service |
> | 47 | `dry_run=True` path — calls internal write but not modbus | ✅ Mock modbus |
> | 51 | `dry_run=False` path — actually writes via modbus | ✅ Assert modbus call |
> | **64** | `handle_control_command` with `"reset"` payload — **NOT tested by existing tests!** | ✅ Direct call |
> | 71–77 | Register batch writing with gaps | ✅ Mock modbus, assert calls |
> | 80–88 | The loop in `__write_registers` — full batch write path | ✅ Mock modbus |
> | 91–107 | Various register mapping edge cases | ✅ Multiple test scenarios |

### Why
Existing tests only cover `process()` (building read_state) and one `handle_command()` (storing modifications). The **critical missing paths** are:
- All three control commands (`write`, `dry-write`, `reset`) — line 64 is **not covered**
- The entire `write_config` / `__write_registers` flow — lines 71–107 completely uncovered

### ⚠️ Private name mangling note
The service uses `self.__read_state`, `self.__modifications`, `self.__write_registers`. Tests must use the exposed properties (`sut.read_state`, `sut.modifications`) — this is already the pattern in existing tests.

### Implementation Steps

#### Step 1: Test control command `reset` (covers line 64 — NOT covered!)
```python
# File: tests/deye_timeofuse_service_test.py
def test_handle_control_command_reset_clears_modifications(
    self, logger_config_mock, mqtt_client_mock, modbus_mock
):
    sensors = [sensor_time_1, sensor_time_2]
    sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)
    sut.initialize()
    # set modifications via handle_command
    msg = MQTTMessage(1, b"deye/timeofuse/time/1/command")
    msg.payload = b"0600"
    sut.handle_command(None, None, msg)
    assert sut.modifications  # modifications exist
    
    # send reset command
    reset_msg = MQTTMessage(1, b"deye/timeofuse/control")
    reset_msg.payload = b"reset"
    sut.handle_control_command(None, None, reset_msg)
    
    assert not sut.modifications  # cleared
```

#### Step 2: Test `write_config` early return when no read_state (covers line 44)
```python
def test_write_config_early_return_when_no_read_state(
    self, logger_config_mock, mqtt_client_mock, modbus_mock
):
    sensors = [sensor_time_1]
    sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)
    sut.initialize()
    # set a modification but do NOT call process() → read_state is empty
    sut.modifications[sensor_time_1] = "0600"
    sut.write_config(dry_run=False)
    # modbus should NOT be called because read_state is empty
    assert not modbus_mock.write_registers.called
```

#### Step 3: Test control command `dry-write` — no actual modbus call (covers line 47)
```python
def test_handle_control_command_dry_write_no_modbus_call(
    self, logger_config_mock, mqtt_client_mock, modbus_mock
):
    sensors = [sensor_time_1, sensor_time_2]
    sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)
    # build read_state via process()
    now = datetime.now()
    observations = [
        Observation(sensor_time_1, now, 500),
        Observation(sensor_time_2, now, 700),
    ]
    sut.process(DeyeEventList([DeyeObservationEvent(o) for o in observations]))
    sut.modifications[sensor_time_1] = "0600"
    
    # send dry-write command
    dry_msg = MQTTMessage(1, b"deye/timeofuse/control")
    dry_msg.payload = b"dry-write"
    sut.handle_control_command(None, None, dry_msg)
    
    assert not modbus_mock.write_registers.called  # dry run
```

#### Step 4: Test control command `write` — single batch, consecutive registers (covers lines 51, 80–88)
```python
def test_handle_control_command_write_sends_modbus_single_batch(
    self, logger_config_mock, mqtt_client_mock, modbus_mock
):
    sensors = [sensor_time_1, sensor_time_2]
    sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)
    now = datetime.now()
    observations = [
        Observation(sensor_time_1, now, 500),
        Observation(sensor_time_2, now, 700),
    ]
    sut.process(DeyeEventList([DeyeObservationEvent(o) for o in observations]))
    # set modifications on consecutive registers (148, 149)
    sut.modifications[sensor_time_1] = "0600"
    sut.modifications[sensor_time_2] = "0700"
    
    write_msg = MQTTMessage(1, b"deye/timeofuse/control")
    write_msg.payload = b"write"
    sut.handle_control_command(None, None, write_msg)
    
    assert modbus_mock.write_registers.called
    call_args = modbus_mock.write_registers.call_args
    self.assertEqual(call_args[0][0], 148)  # first register address
    self.assertEqual(len(call_args[0][1]), 2)  # two values
```

#### Step 5: Test control command `write` — batch with gaps (covers lines 71–77)
```python
def test_handle_control_command_write_handles_gaps_in_registers(
    self, logger_config_mock, mqtt_client_mock, modbus_mock
):
    sensors = [sensor_time_1, sensor_time_3]  # registers 148 and 150 (gap at 149)
    sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)
    now = datetime.now()
    observations = [
        Observation(sensor_time_1, now, 500),
        Observation(sensor_time_3, now, 1000),
    ]
    sut.process(DeyeEventList([DeyeObservationEvent(o) for o in observations]))
    sut.modifications[sensor_time_1] = "0600"
    sut.modifications[sensor_time_3] = "0A00"
    
    write_msg = MQTTMessage(1, b"deye/timeofuse/control")
    write_msg.payload = b"write"
    sut.handle_control_command(None, None, write_msg)
    
    assert modbus_mock.write_registers.called
```

---

## Priority 3 — `deye_active_power_regulation.py` (70% → 95%) {#priority-3}

> **Verified gap lines** (actual source):
> | Line(s) | Description | Testability |
> |---------|-------------|-------------|
> | **40–41, 51** | `ValueError` exception when payload is not numeric — **MISSING FROM ORIGINAL PLAN!** | ✅ MQTT message with non-numeric payload |
> | 54–60 | Error/info log messages + sensor write after validation | ✅ pytest caplog |
> | 67–69 | Logging when sensor lookup fails in init | ✅ Verify via existing fixture pattern |

### ⚠️ Critical finding: The plan missed the **most obvious missing test**
There is **no `ValueError` / bad input test**. When payload is not a valid float, line 51 (`except ValueError`) and its error log are never executed. This is the single fastest test to add.

### Existing test patterns (pytest fixture style — already matches)
```python
class TestDeyeActivePowerRegulationEventProcessor:
    @staticmethod
    @pytest.fixture
    def modbus_mock(mocker) -> DeyeModbus:
        return mocker.Mock(spec=DeyeModbus)
    
    @staticmethod
    @pytest.fixture
    def sensors(mocker) -> [Sensor]:
        sensor = mocker.Mock(spec=Sensor)
        sensor.mqtt_topic_suffix = "settings/active_power_regulation"
        sensor.write_value.return_value = {40: bytearray.fromhex("0102")}
        return [sensor]
```

### Implementation Steps

#### Step 1: Test `ValueError` for non-numeric payload (covers line 51 — NOT in original plan!)
```python
# File: tests/deye_active_power_regulation_test.py
import logging

def test_handle_invalid_value_raises_no_exception_logs_error(
    self, config_mock, mqtt_client_mock, modbus_mock, sensors, caplog
):
    sut = DeyeActivePowerRegulationEventProcessor(config_mock, mqtt_client_mock, sensors, modbus_mock)
    msg = MQTTMessage()
    msg.payload = "not_a_number"  # triggers ValueError in handle_command
    
    with caplog.at_level(logging.ERROR):
        sut.handle_command(None, None, msg)
    
    assert not modbus_mock.write_register_uint.called
    assert "Invalid active power regulation value" in caplog.text
```

> **Note**: The original plan's Steps 1–4 (boundary values, nominal range, logging) were based on incorrect line numbers. After reading the actual source, this file doesn't have configurable min/max boundaries — it has fixed bounds (>120 and <0). Those bounds are already tested by `test_reject_too_high_value` and `test_reject_too_low_value`. The **one genuinely missing test** is the non-numeric payload.

---

## Priority 4 — `deye_config.py` (64% → 80%) {#priority-4}

> **Verified gap lines** (actual source):
> | Line(s) | Description | Testability |
> |---------|-------------|-------------|
> | 42–45 | `DeyeEnv.boolean()` — non-"true/false" value triggers TypeError | ✅ env var + assert KeyError |
> | 55, 57, 59 | `DeyeEnv.string()` default path and key-not-set KeyError paths | ✅ Some covered, some not |
> | 97, 101, 105, 109 | `DeyeMqttConfig` property getters returning None for empty strings | ✅ Direct instantiation |
> | 181–213 | Feature flag / active processor paths in `from_env()` | ✅ env var toggling |
> | 264–312 | Settings file parsing — tied to real config files | ❌ Hard — requires INI fixtures |

### Existing test patterns (unittest style)
```python
class DeyeConfigTest(unittest.TestCase):
    def test_read_not_existing_required_string(self):
        try:
            DeyeEnv.string("FOO")
            self.fail()
        except KeyError as e:
            pass
```

### Implementation Steps

#### Step 1: Test boolean TypeError for non-"true/false" value (covers lines 42–45)
```python
def test_boolean_raises_typeerror_for_non_bool_value(self):
    os.environ["TEST_BOOL_VAR"] = "yes"
    try:
        DeyeEnv.boolean("TEST_BOOL_VAR")
        self.fail()
    except TypeError as e:
        assert "not a valid boolean" in str(e)
    finally:
        del os.environ["TEST_BOOL_VAR"]
```

#### Step 2: Test `DeyeMqttConfig` property None return for empty strings (lines 97, 101, 105, 109)
```python
def test_mqtt_config_username_password_return_none_for_empty_strings(self):
    cfg = DeyeMqttConfig(host="localhost", port=1883, username="", password="", topic_prefix="deye")
    self.assertIsNone(cfg.username)
    self.assertIsNone(cfg.password)
```

#### Step 3: Test feature flag paths in `from_env()` (lines 181–213)
```python
def test_active_processors_includes_mqtt_publisher_by_default(self):
    # with DEYE_FEATURE_MQTT_PUBLISHER=True (default), mqtt_publisher should be included
    processors = DeyeConfig._DeyeConfig__read_active_processors()
    self.assertIn("mqtt_publisher", processors)
```

> **Note on lines 264–312**: These parse `.ini`-style inverter configuration files. Full coverage would require realistic INI fixtures with dozens of settings entries. **Recommendation**: Accept partial coverage or add one minimal integration-style test.

---

## Priority 5 — `deye_sensor.py` (80% → 90%) {#priority-5}

> **Verified gap lines** (actual source):
> | Lines | Description | Testability |
> |-------|-------------|-------------|
> | **32–79** | Abstract property `pass` stubs in base `Sensor` class | ❌ **Not testable** — abstract methods, add coverage exclusion |
> | 86 | `format_value()` with specific format string | ✅ Unit test on existing sensors |
> | 99 | `in_any_group()` with empty groups set | ⚠️ Possibly already covered |
> | 257 | SingleRegisterSensor read returning None when register key missing | ✅ Mock registers dict without key |
> | 316, 322 | DateTimeSensor error paths (short input) | ✅ **Already tested** — `test_datetime_sensor_wrong_input` |
> | 407–412, 415 | Signed magnitude unpacking | ✅ **Already tested** — multiple existing tests |
> | 446 | High-word-first ordering | ✅ **Already tested** — `test_double_reg_sensor_unsigned_high_word_first` |
> | 529+ | Computed sensor paths | ❌ Sensor-group specific, requires integration data |

### ⚠️ Critical finding: Many "missing" lines are abstract `pass` stubs
The base `Sensor` class has abstract properties (lines 32–79) that only have `pass` statements. These **cannot be directly executed** and should be excluded from coverage. They are not real code paths — they define the interface.

### Also: Existing tests already cover more than the plan assumed
- ✅ `test_datetime_sensor_wrong_input` — DateTimeSensor short input
- ✅ `test_double_reg_sensor_unsigned_high_word_first` — high-word-first ordering
- ✅ `test_signed_magnitude_single_register_signed/unsigned` — signed magnitude
- ✅ `test_single_reg_sensor_write_unsigned/signed` — write_value

### Implementation Steps (practical, after excluding abstract stubs)

#### Step 1: Test `format_value` with specific format string (line 86)
```python
# File: tests/deye_sensor_test.py
def test_format_value_uses_print_format(self):
    sut = SingleRegisterSensor("test", 0x00, 1.0, signed=False, print_format="{:d}", groups=["string"])
    result = sut.format_value(42)
    self.assertEqual(result, "42")
```

> **Note**: The original plan's Steps 1–3 were largely redundant since existing tests already cover `write_value`, high-word-first ordering, and signed magnitude. After investigation, only `format_value` is a genuinely new gap to test.

---

## Summary of Expected Impact (Corrected)

| Priority | File | Current → Target | Tests Added | Notes |
|----------|------|-------------------|-------------|-------|
| 3 | `deye_active_power_regulation.py` | 70% → 90% | **1** | ValueError test — biggest missing path |
| 1 | `deye_modbus.py` | 76% → 95% | **6** + helper | Error paths only, pure mocks |
| 2 | `deye_timeofuse_service.py` | 50% → 90% | **5** | All control commands + write flow |
| 4 | `deye_config.py` | 64% → 75% | **3** | Boolean TypeError + property None paths |
| 5 | `deye_sensor.py` | 80% → 83% | **1** | format_value test |

### Coverage exclusion recommended
Add to `pyproject.toml` `[tool.coverage.run]` section:
```toml
[tool.coverage.run]
branch = true
relative_files = true
source = ["src"]
# TODO: add line-specific exclusions as needed
```

> For abstract stubs in deye_sensor.py (lines 32–79), consider adding `# pragma: no cover` to each property's `pass` statement, or use coverage `omit` configuration.

### Realistic Target
| Scenario | Tests Added | Est. Coverage Gain | New Overall |
|----------|-------------|--------------------|-------------|
| **Best case** (all planned tests pass) | ~16 | +8–10% → ~93–95% |
| **Realistic** (some sensor gaps accepted as-is) | ~14 | +6–8% → ~91–93% |

---

## Not Worth Pursuing (Accept as-Is)

### `deye_at_connector.py` (21%)
Pure socket I/O. Only `extract_modbus_response` is unit-testable — already at 100%. Network operations require integration test.
**Recommendation:** Add `# pragma: no cover` to socket wrapper methods.

### `deye_mqtt.py` (43%)
Requires real MQTT broker for most paths. `test-mqtt` integration target exists.
**Recommendation:** Accept partial coverage with integration test guard.

### `src/deye_sensor.py` abstract stubs + computed sensor paths (lines 32–79, 529–579)
Abstract `pass` statements cannot be tested. Computed-sensor paths are sensor-group-specific.
**Recommendation:** Add coverage exclusion for abstract stubs; accept computed paths as partial.

### `src/deye_config.py` settings parsing (lines 264–312)
Parse `.ini`-style inverter config files — device-specific and large.
**Recommendation:** Accept partial coverage or add one minimal integration-style test.

---

## Execution Order (Recommended)

1. **Priority 3** (active power regulation — `ValueError` test) — **Fastest single win**, 1 test, addresses the most obvious gap (no input validation test in a file with 70% coverage).
2. **Priority 1** (modbus errors) — 6 tests, pure mock-based, follows existing unittest convention perfectly.
3. **Priority 2** (timeofuse service) — 5 tests, pytest style matches existing tests exactly.
4. **Priority 4** (config) — 3 tests, extends existing unittest patterns.
5. **Priority 5** (sensor) — 1 test + coverage exclusions for abstract stubs.

---

## Quick-Start: First Tests to Write

### 1. Active Power Regulation — `ValueError` (10 min)
```python
# Add to tests/deye_active_power_regulation_test.py
import logging

def test_handle_invalid_value_raises_no_exception_logs_error(
    self, config_mock, mqtt_client_mock, modbus_mock, sensors, caplog
):
    sut = DeyeActivePowerRegulationEventProcessor(config_mock, mqtt_client_mock, sensors, modbus_mock)
    msg = MQTTMessage()
    msg.payload = "not_a_number"
    with caplog.at_level(logging.ERROR):
        sut.handle_command(None, None, msg)
    assert not modbus_mock.write_register_uint.called
    assert "Invalid active power regulation value" in caplog.text
```

### 2. Modbus CRC mismatch (15 min)
```python
# Add to tests/deye_modbus_tcp_test.py
@patch("deye_connector.DeyeConnector")
def test_read_registers_crc_mismatch_returns_empty(self, connector):
    sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
    frame = bytearray.fromhex("010302000a")
    bad_crc = bytearray.fromhex("0000")  # wrong CRC
    connector.send_request.return_value = frame + bad_crc
    reg_values = sut.read_registers(1, 1)
    self.assertEqual(reg_values, {})
```
