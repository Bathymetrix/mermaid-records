# Unclassified LOG Triage (2026-06-16)

This document summarizes review of `log_unclassified_records.jsonl` after
dissolution of the former `log_operational_records.jsonl` family.

The goal is to identify unclassified LOG message shapes that may deserve
remapping into existing normalized families, creation of new families, or
intentional retention in the unclassified stream.

## Definite Yes

These are structured telemetry/configuration records that clearly belong in an
existing family or a narrowly scoped new family.

| Count | Example | Proposed Action |
|--------:|----------|----------------|
| 250,358 | `1527dbar, -10degC` | Routed to `log_pressure_temperature_records` |
| 76,746 | `internal pressure 78680Pa` | Routed to `log_pressure_temperature_records` |
| 23,125 | `Pext -45mbar (rng 30mbar)` | Routed to `log_pressure_temperature_records` |
| 17,821 | `Pint 76872Pa` | Routed to `log_pressure_temperature_records` |
| 23,124 | `Vbat 14681mV (min 13967mV)` | Extend `log_battery_records` |
| 88,580 | `$MEASFS,263069,6574.446777,40.013861;` | Extend `log_acquisition_records` |
| 22,476 | `Mermaid $MEASFS,...` | Same as above |
| 16,642 | `$TRIG:4,2;` | Acquisition/detection family |
| 13,770 | `$UPLOAD_MAX:150;` | Extend `log_transmission_records` |
| 5,107 | `$REQUEST:2022-01-15T04_34_53,1800,5;` | Request/transmission family |
| 5,384 | `p2t37: dp 50mbar, dt 5000mdegC` | Extend `log_parameter_records` |
| 5,384 | `coeff`, `delay`, `surface`, `ascent`, etc. parameter dump lines | Extend `log_parameter_records` |
| 16,524 | `fix 3D, 8 satellites` | Extend `log_gps_records` |
| 7,659 | `Latitude : N43deg40.956mn, Longitude :E007deg19.175mn` | Extend `log_gps_records` |
| 27,494 | `+0s diff` | GPS/time-sync family |

## Maybe Yes

These appear structured and potentially useful, but require a scope decision.

### Candidate: `log_buoyancy_records`

These represent buoyancy-engine control telemetry rather than environmental
telemetry.

| Count | Example |
|--------:|----------|
| 482,363 | `during 24042ms` |
| 249,507 | `pump during 300000ms` |
| 185,526 | `opening for 1244ms` |
| 101,263 | `valve opening 11087ms` |
| 86,061 | `need to transfer +44mL (pump during 53140ms)` |
| 64,745 | `need to transfer -20mL (valve during 11087ms)` |
| 39,250 | `filling external bladder` |
| 38,220 | `external bladder full` |
| 36,563 | `bypass opening 60000ms` |

### Other Structured Status Records

| Count | Example | Proposed Action |
|--------:|----------|----------------|
| 54,843 | `connected in 143s, signal quality 5` | Extend `log_transmission_records` |
| 50,707 | `7 cmd(s) received` | Candidate `log_command_records` |
| 10,456 | `prompt received, remote cmd end` | Command/transmission family |
| 8,210 | `emergency call` | Communication state |
| 7,027 | `<ERR>uploading failed` | Extend `log_transmission_records` |
| 5,387 | `<WARN>GPRMC ms=370 #1` | Extend `log_gps_records` |

## Maybe No

These appear to be mission-state breadcrumbs, workflow tracking, or control
logic diagnostics. They may be useful, but are less obviously durable record
families.

| Count | Example | Notes |
|--------:|----------|-------|
| 46,103 | `stage[0]` | Mission-state breadcrumb |
| 19,724 | `Stage [0] 5000mbar (+/-500mbar) 1800s ...` | Mission profile/configuration |
| 31,834 | `<WARN>stage[0] should ASCENT/DESCENT...` | Control warning |
| 7,250 | `4529mbar reached at ...` | Stage progress |
| 5,966 | `stage[0] complete 1803s after mission start` | State-machine progress |
| 5,699 | `stage[1] 10 stab done` | State-machine progress |
| 23,398 | `cycle 1` | Context-dependent |
| 23,125 | `surface` | Operational breadcrumb |
| 23,104 | `surfacing` | Operational breadcrumb |
| 23,104 | `turn off bluetooth` | Operational breadcrumb |
| 101,273 | `10 PPS detected...` | Timing/hardware status |

## Definite No

These do not appear suitable for durable normalized record families.

### Parser / Serial Noise

| Count | Example |
|--------:|----------|
| 138,543+ | `dropping spurious '1'` |
| 13,234 | `3 spurious byte(s) received` |
| 8,665 | `dropping spurious ';'` |
| 8,111 | `dropping spurious '.'` |
| 6,623 | `dropping spurious ','` |

### Boot Banners / Metadata

| Count | Example |
|--------:|----------|
| 55,204 | `Iridium...` |
| 25,349 | `soft ...` |
| 18,789 | `board ...` |
| 19,835 | Bare timestamp strings |
| 5,043 | `FreeRTOS V8.2.3` |
| 5,043 | `FatFS v11a` |
| 1,690 | `reboot code ...` |

These are best treated as banners, inventory metadata, or diagnostic text.

## Unknown / Needs Interpretation

The following shapes appear structured but their semantic meaning is not yet
understood sufficiently to propose a stable schema.

| Count | Example | Notes |
|--------:|----------|-------|
| 150,384 | `from +2mbar/s to +4mbar/s` | Buoyancy-control rates? |
| 33,425 | `Outflow calculated : 2823` | Units unknown |
| 23,010 | `630mbar reached (+13mbar/s), 7 bypass done` | Mixed control/state message |
| 13,340 | `<ERR>acq not started` | Acquisition diagnostic |
| 4,012 | `1st complete transfer` | Transfer of what? |
| 3,736 | `last almanac : 6954` | GPS-related? Units unknown |

## Recommended Immediate Actions

1. Extend `log_battery_records` for `Vbat`.
2. Extend acquisition, transmission, GPS, and parameter families for the
   structured `$...` and parameter-dump records.
3. Decide whether buoyancy-engine telemetry warrants a dedicated
   `log_buoyancy_records` family.

Everything else can remain in `log_unclassified_records.jsonl` until there is a
clear downstream use case and schema definition.

## Completed Routing Decisions

| Count | Example | Decision |
|--------:|----------|----------|
| 41,432 | `P+151590mbar` | Routed to `log_pressure_temperature_records` as generic `pressure_mbar`. |
