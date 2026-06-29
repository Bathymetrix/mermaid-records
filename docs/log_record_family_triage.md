# LOG Record Family Triage (refreshed 2026-06-29)

This note is now a backlog for LOG message shapes that still need a
normalization/no-normalization decision. Counts are from the original
2026-06-16 unclassified-output review and should be treated as approximate
historical scale indicators, not current post-routing counts.

The current LOG family source of truth is `docs/log_record_family_schemas.md`
and `src/mermaid_records/normalize_log.py`.

## Recently Resolved

These shapes were present in the original triage, but are now routed by current
normalization code.

| Count | Example | Current routing |
|--------:|----------|-----------------|
| 250,358 | `1527dbar, -10degC` | `log_pressure_temperature_records` |
| 76,746 | `internal pressure 78680Pa` | `log_pressure_temperature_records` |
| 41,432 | `P+151590mbar` | `log_pressure_temperature_records` |
| 23,125 | `Pext -45mbar (rng 30mbar)` | `log_pressure_temperature_records` |
| 17,821 | `Pint 76872Pa` | `log_pressure_temperature_records` |
| 23,124 | `Vbat 14681mV (min 13967mV)` | `log_battery_records` as `vbat_summary` |
| 55,204 | `Iridium...` | `log_iridium_records` session start |
| 54,843 | `connected in 143s, signal quality 5` | `log_iridium_records` event |
| 50,707 | `7 cmd(s) received` | `log_iridium_records` event |
| 13,770 | `$UPLOAD_MAX:150;` | `log_iridium_records` command event |
| 10,456 | `prompt received, remote cmd end` | `log_iridium_records` event |
| 7,027 | `<ERR>uploading failed` | `log_iridium_records` event |
| 5,384 | `p2t37: dp 50mbar, dt 5000mdegC` | `log_parameter_records` grouped parameter episode |
| 5,384 | `coeff`, `delay`, `surface`, `ascent`, etc. parameter dump lines | `log_parameter_records` grouped parameter episode |
| 7,659 | `Latitude : N43deg40.956mn, Longitude :E007deg19.175mn` | `log_gps_records` as `fix_position` |

## Strong Candidates

These look structured enough to tackle next, provided the scope stays literal
and avoids interpretation.

### GPS / Time-Sync Extensions

Current `log_gps_records` covers `GPS fix...`, compact and verbose
latitude/longitude lines, `hdop`/`vdop`, `GPSACK`, and `GPSOFF`. These
remaining examples look GPS-adjacent but use different text shapes.

| Count | Example | Possible action |
|--------:|----------|-----------------|
| 16,524 | `fix 3D, 8 satellites` | Add a GPS status/fix-detail kind with literal satellite count. |
| 5,387 | `<WARN>GPRMC ms=370 #1` | Add a GPS diagnostic kind if examples are consistent. |
| 3,736 | `last almanac : 6954` | Possible GPS/almanac diagnostic, but units and meaning need confirmation. |
| 27,494 | `+0s diff` | Possible time-sync record; needs surrounding-line context before routing. |

Recommendation: GPS extensions are the cleanest next small slice if we inspect
several raw examples first and keep the schema source-literal.

### Iridium / Command Follow-Up

Current `log_iridium_records` captures explicit sessions and standalone
event-sequences for command-like `$NAME:payload;` lines. These should be
sampled before deciding whether they belong in Iridium or a separate request
family.

| Count | Example | Possible action |
|--------:|----------|-----------------|
| 5,107 | `$REQUEST:2022-01-15T04_34_53,1800,5;` | Likely already fits Iridium command parsing; verify with generated outputs. |
| 8,210 | `emergency call` | Possible Iridium/communication event; needs context. |
| 4,012 | `1st complete transfer` | Transfer event, but source workflow needs confirmation. |

Recommendation: audit current `log_iridium_records` output before adding more
communication predicates. Some of this may already be captured as
`session_line` inside explicit Iridium sessions.

## Larger Design Decision

### Candidate: `log_buoyancy_records`

These represent buoyancy-engine control telemetry rather than environmental
telemetry. They are high-volume and structured, but defining the family risks
creeping from parsing into state-machine interpretation.

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
| 150,384 | `from +2mbar/s to +4mbar/s` |
| 33,425 | `Outflow calculated : 2823` |
| 23,010 | `630mbar reached (+13mbar/s), 7 bypass done` |

Recommendation: do not fold this into pressure/temperature records. If tackled,
create a literal buoyancy/control family with event kinds and raw values only.
Avoid inferred stage state, durations beyond explicit fields, and workflow
interpretation.

## Probably Keep Unclassified For Now

These are mission breadcrumbs, firmware/boot metadata, parser noise, or
diagnostics without a stable schema need yet.

### Mission / State Breadcrumbs

| Count | Example | Notes |
|--------:|----------|-------|
| 46,103 | `stage[0]` | Mission-state breadcrumb. |
| 19,724 | `Stage [0] 5000mbar (+/-500mbar) 1800s ...` | Mission profile/configuration; possible future family, but not urgent. |
| 31,834 | `<WARN>stage[0] should ASCENT/DESCENT...` | Control warning. |
| 7,250 | `4529mbar reached at ...` | Stage progress. |
| 5,966 | `stage[0] complete 1803s after mission start` | State-machine progress. |
| 5,699 | `stage[1] 10 stab done` | State-machine progress. |
| 23,398 | `cycle 1` | Context-dependent. |
| 23,125 | `surface` | Operational breadcrumb. |
| 23,104 | `surfacing` | Operational breadcrumb. |
| 23,104 | `turn off bluetooth` | Operational breadcrumb. |
| 101,273 | `10 PPS detected...` | Timing/hardware status; maybe useful, but not a current family. |

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
| 25,349 | `soft ...` |
| 18,789 | `board ...` |
| 19,835 | Bare timestamp strings |
| 5,043 | `FreeRTOS V8.2.3` |
| 5,043 | `FatFS v11a` |
| 1,690 | `reboot code ...` |

## Needs Domain Decision

These may be meaningful, but the parser should not guess.

| Count | Example | Open question |
|--------:|----------|---------------|
| 88,580 | `$MEASFS,263069,6574.446777,40.013861;` | Is this a command/config line, acquisition evidence, or higher-level detection/acquisition configuration? |
| 22,476 | `Mermaid $MEASFS,...` | Same as above, but with a prose prefix. |
| 16,642 | `$TRIG:4,2;` | Currently command-shaped for Iridium when parsed as `$NAME:payload;`; should any trigger command also feed an acquisition/request family? |
| 13,340 | `<ERR>acq not started` | Acquisition diagnostic; likely not transition evidence. |

Recommendation: do not add these to acquisition records until the field
contract is explicit. `acq started` / `acq stopped` should remain the only
transition evidence in normalization.

## Suggested Next Slices

1. GPS alternate text shapes: `fix 3D`, `Latitude : ...`, maybe `GPRMC ms=...`.
2. Audit current `log_iridium_records` for `$REQUEST` and `emergency call`
   coverage before adding more predicates.
3. Decide whether `log_buoyancy_records` is worth a literal event-only family.
4. Leave mission breadcrumbs, boot banners, parser noise, and ambiguous
   acquisition diagnostics in `log_unclassified_records` for now.
