# LOG Record Family Schemas

This is a developer-facing reference for LOG-derived JSONL families emitted by
`mermaid-records`. Filename examples below use base family filenames such as
`log_gps_records.jsonl`; pipeline outputs normally include the instrument serial
before `.jsonl`, for example `log_gps_records.467.174-T-0100.jsonl`.

The source of truth is `src/mermaid_records/normalize_log.py`.
This document is a generated/audited companion to that source: update it
whenever LOG family filenames, emitted fields, grouping behavior, classifier
hit rules, or exclusivity behavior change. The documented `Hits:` examples are
covered by tests so classifier drift should fail loudly.

## Shared LOG Parsing Contract

Ordinary LOG family classification starts only after a raw line parses as one of
these tagged LOG forms:

```text
^(?P<time>.+?):\[(?P<tag>[^\]]+)\](?P<message>.*)$
^(?P<time>.+?):(?P<prefix><(?:ERR|WARN|WRN)>)\[(?P<tag>[^\]]+)\](?P<message>.*)$
```

For tagged lines, `tag` is split on the first comma into `subsystem` and
nullable `code`. Wrapped severity prefixes are prepended to `message`, so:

```text
1700000000:<ERR>[MODEM ,0347]ping error
```

becomes message `<ERR>ping error`.

Grouped families (`log_parameter_records.jsonl`, `log_ctd_records.jsonl`, and
`log_testmode_records.jsonl`) are resolved before ordinary tagged-line
classification. Other ordinary tagged lines are checked against specific
families in this order:

```text
acquisition, ascent_request, gps, transmission, pressure_temperature, battery
```

Zero specific matches routes the line to `log_unclassified_records.jsonl`. Two
or more specific matches is a normalization bug and raises
`Operational derived-family multi-match`.

## Common Single-Line Fields

These fields appear on every single-line family:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `instrument_id` | string | no | Canonical station/instrument identifier. | n/a | Pipeline context or fallback from LOG path. |
| `instrument_serial` | string | no | Full hardware/dataset serial used in output filenames. | n/a | Pipeline context or fallback from LOG path. |
| `source_file` | string | no | Basename of the source LOG file. | n/a | `entry.source_file.name`; never a full path. |
| `source_container` | string | no | Source container kind. Always `log`. | n/a | Constant. |
| `record_time` | string | no | UTC ISO8601 timestamp with six fractional digits and `Z`. | UTC time | Parsed from raw LOG timestamp. |
| `log_epoch_time` | string | no | Original raw LOG timestamp text. | source literal | Raw text before the first timestamp separator. |
| `subsystem` | string | no | LOG subsystem tag. | n/a | Parsed tag before comma. |
| `code` | string or null | yes | LOG code tag. | n/a | Parsed tag after comma, or null when absent. |
| `message` | string | no | Parsed LOG message. | n/a | Text after tag; wrapped severity prefix is retained. |
| `source_line_number` | integer | no | 1-based line number in the source LOG file. | lines | File reader enumeration. |
| `raw_line` | string | no | Complete raw source LOG line without newline. | n/a | Source line. |

## Common Grouped-Episode Fields

These fields appear on grouped episode families. Grouped episode records do not
currently include `source_container`, `subsystem`, `code`, `message`, or
`raw_line`.

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `instrument_id` | string | no | Canonical station/instrument identifier. | n/a | Pipeline context or fallback from LOG path. |
| `instrument_serial` | string | no | Full hardware/dataset serial used in output filenames. | n/a | Pipeline context or fallback from LOG path. |
| `source_file` | string | no | Basename of the source LOG file. | n/a | Source LOG path basename. |
| `episode_index` | integer | no | Zero-based episode number within the source file and family. | n/a | Incremented by grouped parser. |
| `line_start_index` | integer | no | 1-based source line number for the first timestamped line in the episode. | lines | First grouped line with parsed time. |
| `line_end_index` | integer | no | 1-based source line number for the last timestamped line in the episode. | lines | Last grouped line with parsed time. |
| `source_line_numbers` | array of integers | no | 1-based source line numbers included in the episode. | lines | All grouped lines, including blank testmode lines. |
| `start_record_time` | string | no | UTC ISO8601 time for first timestamped line. | UTC time | Parsed first timestamped grouped line. |
| `end_record_time` | string | no | UTC ISO8601 time for last timestamped line. | UTC time | Parsed last timestamped grouped line. |
| `start_log_epoch_time` | string | no | Raw timestamp text for first timestamped line. | source literal | Source line timestamp. |
| `end_log_epoch_time` | string | no | Raw timestamp text for last timestamped line. | source literal | Source line timestamp. |
| `raw_lines` | array of strings | no | Raw source lines in the episode without newlines. | n/a | Source lines. |

## `log_acquisition_records.jsonl`

Purpose / scope: explicit acquisition state evidence lines only. This family
preserves the distinction between state transitions and state assertions.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_acq.LOG","source_container":"log","record_time":"2023-11-14T22:13:20.000000Z","log_epoch_time":"1700000000","subsystem":"MRMAID","code":"0002","message":"acq started","source_line_number":1,"acquisition_state":"started","acquisition_evidence_kind":"transition","raw_line":"1700000000:[MRMAID,0002]acq started"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `acquisition_state` | string | no | `started` or `stopped`. | n/a | Literal message map. |
| `acquisition_evidence_kind` | string | no | `transition` for exact start/stop, `assertion` for already-started/stopped. | n/a | Literal message map. |

Classifier hit rules:

Literal messages are normalized with `" ".join(message.lower().split())` and
must exactly equal one of:

```text
acq started          -> acquisition_state=started, acquisition_evidence_kind=transition
acq stopped          -> acquisition_state=stopped, acquisition_evidence_kind=transition
acq already started  -> acquisition_state=started, acquisition_evidence_kind=assertion
acq already stopped  -> acquisition_state=stopped, acquisition_evidence_kind=assertion
```

Hits:

```text
1700000000:[MRMAID,0002]acq started
1700000002:[MRMAID,0184]acq already started
```

Non-hits:

```text
1700000000:[MRMAID,0002]acq start
1700000000:[MAIN  ,0007]acquisition started
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. These lines previously would have
been ordinary/base operational rows before `log_operational_records` was
dissolved.

Known gaps / edge cases: message matching is intentionally literal after
lowercasing and whitespace collapse; no intervals are inferred from assertions.

## `log_ascent_request_records.jsonl`

Purpose / scope: explicit ascent-request outcomes only.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_ascent.LOG","source_container":"log","record_time":"2023-11-14T22:13:20.000000Z","log_epoch_time":"1700000000","subsystem":"MRMAID","code":"0583","message":"ascent request accepted","source_line_number":1,"ascent_request_state":"accepted","raw_line":"1700000000:[MRMAID,0583]ascent request accepted"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `ascent_request_state` | string | no | `accepted` or `rejected`. | n/a | Literal message map. |

Classifier hit rules:

Literal messages are normalized with `" ".join(message.lower().split())` and
must exactly equal one of:

```text
ascent request accepted -> ascent_request_state=accepted
ascent request rejected -> ascent_request_state=rejected
```

Hits:

```text
1700000000:[MRMAID,0583]ascent request accepted
1700000001:[MRMAID,0005]ascent request rejected
```

Non-hits:

```text
1700000000:[MRMAID,0583]ascent accepted
1700000000:[MRMAID,0583]ascent requested
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. These lines previously would have
been ordinary/base operational rows before `log_operational_records` was
dissolved.

Known gaps / edge cases: no ascent-request state is inferred from other
ascent-related lines.

## `log_battery_records.jsonl`

Purpose / scope: literal battery telemetry lines with voltage/current or
VIT-like voltage/minimum-voltage summaries.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_battery.LOG","source_container":"log","record_time":"2023-11-14T22:13:23.000000Z","log_epoch_time":"1700000003","subsystem":"MONITR","code":"0461","message":"battery 14685mV,   12688uA","source_line_number":4,"battery_record_kind":"voltage_current","voltage_mv":14685,"current_ua":12688,"minimum_voltage_mv":null,"raw_line":"1700000003:[MONITR,0461]battery 14685mV,   12688uA"}
{"instrument_id":"P0026","instrument_serial":"452.020-P-0026","source_file":"0026_5D48EAB8.LOG","source_container":"log","record_time":"2019-08-07T02:57:30.000000Z","log_epoch_time":"1565146650","subsystem":"MAIN","code":"498","message":"Vbat 14681mV (min 13967mV)","source_line_number":1,"battery_record_kind":"vbat_summary","voltage_mv":14681,"current_ua":null,"minimum_voltage_mv":13967,"raw_line":"1565146650:[MAIN  ,498]Vbat 14681mV (min 13967mV)"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `battery_record_kind` | string | no | Source shape discriminator: `voltage_current` or `vbat_summary`. | none | Classifier branch. |
| `voltage_mv` | integer | no | Battery voltage. | mV | Regex group `mv`. |
| `current_ua` | integer | yes | Battery current when present. | uA | Regex group `ua` for `voltage_current`; otherwise `null`. |
| `minimum_voltage_mv` | integer | yes | Minimum battery voltage when present. | mV | Regex group `minimum_mv` for `vbat_summary`; otherwise `null`. |

Classifier hit rules:

Regexes, case-insensitive, searched anywhere in `message`:

```text
\bbattery\s+(?P<mv>[+-]?\d+)mV,\s+(?P<ua>[+-]?\d+)uA\b
\bVbat\s+(?P<mv>[+-]?\d+)mV\s+\(min\s+(?P<minimum_mv>[+-]?\d+)mV\)
```

Hits:

```text
1700000003:[MONITR,0461]battery 14685mV,   12688uA
1700000003:[MONITR,0461]Battery -1mV, +2uA
1565146650:[MAIN  ,498]Vbat 14681mV (min 13967mV)
```

Non-hits:

```text
1700000003:[MONITR,0461]battery 14685mV
1700000003:[MONITR,0461]bat 14685mV, 12688uA
1565146650:[MAIN  ,498]Vbat 14681mV
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. Battery hits previously would have
been ordinary/base operational rows before `log_operational_records` was
dissolved.

Known gaps / edge cases: voltage-only `battery ...mV` or `Vbat ...mV` lines
without the paired `min ...mV` source value are not classified as battery
records.

## `log_gps_records.jsonl`

Purpose / scope: one record per clearly GPS-related tagged LOG line. It does
not group lines into a fix or compute derived coordinates.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_gps.LOG","source_container":"log","record_time":"2023-11-14T22:13:21.000000Z","log_epoch_time":"1700000001","subsystem":"SURF","code":"0082","message":"N35deg19.262mn, E139deg39.043mn","source_line_number":2,"gps_record_kind":"fix_position","raw_values":{"latitude":"N35deg19.262mn","longitude":"E139deg39.043mn"},"raw_line":"1700000001:[SURF  ,0082]N35deg19.262mn, E139deg39.043mn"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `gps_record_kind` | string | no | One of `fix_attempt`, `fix_position`, `dop`, `gps_ack`, `gps_off`. | n/a | First matching GPS predicate. |
| `raw_values` | object or null | yes | Parsed raw GPS scalar strings, or null for fix attempts. The key is always emitted. | source literal | Regex capture groups. |

Classifier hit rules:

The stripped message is checked in this order:

```text
"GPS fix..." substring -> gps_record_kind=fix_attempt, raw_values=null
(?P<latitude>[NS]\d+deg\d+(?:\.\d+)?mn)\s*,\s*(?P<longitude>[EW]\d+deg\d+(?:\.\d+)?mn)
\bhdop\s+(?P<hdop>[+-]?\d+(?:\.\d+)?)       # case-insensitive
\bvdop\s+(?P<vdop>[+-]?\d+(?:\.\d+)?)       # case-insensitive
\$?GPSACK:(?P<payload>[^;]+)
\$?GPSOFF:(?P<offset>[+-]?\d+)
```

For DOP lines, `hdop` and `vdop` are both captured when present in the same
message. Position wins over DOP if a message happens to contain both.

Hits:

```text
1700000000:[SURF  ,0022]GPS fix...
1700000001:[SURF  ,0082]N35deg19.262mn, E139deg39.043mn
1700000002:[SURF  ,0084]hdop 0.820, vdop 1.180
1700000003:[MRMAID,0052]$GPSACK:+0,+0,+0,+0,+0,+0,-30;
1700000004:[MRMAID,0052]$GPSOFF:3686327;
```

Non-hits:

```text
1700000000:[SURF  ,0022]GPS fixed
1700000001:[SURF  ,0082]35.321, 139.651
1700000002:[SURF  ,0084]pdop 1.0
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. These lines previously would have
been ordinary/base operational rows before `log_operational_records` was
dissolved.

Known gaps / edge cases: coordinates are preserved as raw strings. No fix
assembly, coordinate conversion, or timing inference is performed.

## `log_parameter_records.jsonl`

Purpose / scope: grouped timestamped parameter/configuration output lines that
share a known parameter prefix. These lines are not tagged LOG entries.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_params.LOG","episode_index":0,"line_start_index":2,"line_end_index":5,"source_line_numbers":[2,3,4,5],"start_record_time":"2023-11-14T22:13:21.000000Z","end_record_time":"2023-11-14T22:13:21.000000Z","start_log_epoch_time":"1700000001","end_log_epoch_time":"1700000001","raw_lines":["1700000001:    bypass 20000ms 120000ms (10000ms 200000ms stored)","1700000001:    valve 60000ms 12750 (60000ms 12750 stored)","1700000001:    stage[0] 150000mbar (+/-5000mbar) 60000s (<60000s)","1700000001:    stage[1] 150000mbar (+/-5000mbar) 648000s (<708000s)"]}
```

Field table: common grouped-episode fields only.

Classifier hit rules:

The line must first match timestamped non-tagged syntax:

```text
^(?P<time>.+?):(?P<content>.*)$
```

Then `content` must match this case-insensitive prefix regex:

```text
^\s*(?:bypass(?:\s|$)|valve(?:\s|$)|pump(?:\s|$)|rate(?:\s|$)|surface(?:\s|$)|near(?:\s|$)|far(?:\s|$)|ascent(?:\s|$)|dead(?:\s|$)|coeff(?:\s|$)|stab(?:\s|$)|delay(?:\s|$)|mmtime(?:\s|$)|p2t37:|stage\[0\](?:\s|$)|stage\[1\](?:\s|$))
```

Contiguous parameter lines are grouped into one episode. A blank line, tagged
LOG line, rollover banner, malformed line, or other non-parameter timestamped
line ends the current episode.

Hits:

```text
1700000001:    bypass 20000ms 120000ms (10000ms 200000ms stored)
1700000003:    rate 2mbar/s (2mbar/s stored)
1700000005:    ascent 8mbar/s (8mbar/s stored)
```

Non-hits:

```text
1700000000:[MAIN  ,0593]internal pressure 85448Pa
1700000006:Command list
1700000007:    pressure 123mbar
```

Overlap / exclusivity: grouped before ordinary classification and mutually
exclusive by source line. Matching lines do not also appear in unclassified.
They previously would have been part of broad operational preservation before
`log_operational_records` was dissolved.

Known gaps / edge cases: the record preserves grouped raw lines only; it does
not parse individual parameter values. A visually similar timestamped line with
an unknown prefix is malformed or a boundary, not a parameter record.

## `log_pressure_temperature_records.jsonl`

Purpose / scope: literal pressure/temperature and pressure-only telemetry
observations in the units used by the source LOG line.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_press.LOG","source_container":"log","record_time":"2023-11-14T22:13:22.000000Z","log_epoch_time":"1700000002","subsystem":"PRESS","code":"0038","message":"P+20179mbar,T+32767mdegC","source_line_number":3,"pressure_mbar":20179,"temperature_mdegc":32767,"raw_line":"1700000002:[PRESS ,0038]P+20179mbar,T+32767mdegC"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `pressure_mbar` | integer | yes | Generic source-literal pressure value for `P...mbar,T...mdegC` and standalone `P...mbar` observations. | mbar | Regex group `pressure_mbar`; emitted only for matching source lines. |
| `temperature_mdegc` | integer | yes | Temperature value for `P...mbar,T...mdegC` observations. | mdegC | Regex group `temperature_mdegc`; emitted only for matching source lines. |
| `pressure_dbar` | integer | yes | Pressure value for `...dbar, ...degC` observations. | dbar | Regex group `pressure_dbar`; emitted only for matching source lines. |
| `temperature_degc` | integer | yes | Temperature value for `...dbar, ...degC` observations. | degC | Regex group `temperature_degc`; emitted only for matching source lines. |
| `internal_pressure_pa` | integer | yes | Internal pressure value from `internal pressure ...Pa` or `Pint ...Pa` observations. | Pa | Regex group `internal_pressure_pa`; emitted only for matching source lines. |
| `external_pressure_mbar` | integer | yes | External pressure value from `Pext ...mbar` observations. | mbar | Regex group `external_pressure_mbar`; emitted only for matching source lines. |
| `external_pressure_range_mbar` | integer | yes | External pressure range value from `Pext ... (rng ...mbar)` observations. | mbar | Regex group `external_pressure_range_mbar`; emitted only for matching source lines. |

Classifier hit rules:

Regexes, case-sensitive, searched anywhere in `message`:

```text
\bP\s*(?P<pressure_mbar>[+-]?\d+)mbar,\s*T\s*(?P<temperature_mdegc>[+-]?\d+)mdegC\b
^P\s*(?P<pressure_mbar>[+-]?\d+)mbar$
\b(?P<pressure_dbar>[+-]?\d+)dbar,\s*(?P<temperature_degc>[+-]?\d+)degC\b
\binternal pressure\s+(?P<internal_pressure_pa>[+-]?\d+)Pa\b
\bPint\s+(?P<internal_pressure_pa>[+-]?\d+)Pa\b
\bPext\s+(?P<external_pressure_mbar>[+-]?\d+)mbar\s+\(rng\s+(?P<external_pressure_range_mbar>[+-]?\d+)mbar\)
```

Hits:

```text
1700000002:[PRESS ,0038]P+20179mbar,T+32767mdegC
1700000000:[PRESS ,0081]P    +0mbar,T-10881mdegC
1700000000:[BUOY  ,0656]P+151590mbar
1535842096:[MRMAID,565]1523dbar, -11degC
1564269461:[MAIN  ,408]internal pressure 78680Pa
1696784664:[MAIN  ,498]Pint 84535Pa
1565146653:[MAIN  ,507]Pext -45mbar (rng 30mbar)
```

Non-hits:

```text
1700000004:[MAIN  ,0007]New pressure offset: 40mbar
1700000006:[MAIN  ,0007]P +12,T -34,S +56
1688207849:[PROFIL,0288]    p_cut_off=2dbar
1700000000:[VALVE ,0234]battery 15073mV,  502152uA, P  +8921mbar
1700000000:[MAIN  ,0007]Pext -45mbar
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. Standalone `P...mbar` hits are
anchored to the whole `message`, so embedded pressure snippets in battery
telemetry do not also hit this family. Pressure offset, profile parameter,
incomplete `Pext`, and `P +12,T -34,S +56` lines do not hit and currently route
to unclassified when no other family matches. Hits previously would have been
ordinary/base operational rows before `log_operational_records` was dissolved.

Known gaps / edge cases: source units are preserved without conversion, so
`pressure_mbar`, `pressure_dbar`, and `internal_pressure_pa` are distinct fields.
Standalone `P...mbar` rows do not assert internal or external pressure. Offset,
configuration/profile parameter, and CTD-style `P,T,S` lines are intentionally
outside this family.

## `log_ctd_records.jsonl`

Purpose / scope: grouped CTD sensor/profiling episodes. The current classifier
recognizes legacy SBE/PROFIL/STAGE LOG tags, but the output product is named
for CTD observations rather than a specific sensor manufacturer. The family
preserves raw source lines and parses literal `P,T,S` CTD sample values when
present.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_ctd.LOG","episode_index":0,"line_start_index":1,"line_end_index":2,"source_line_numbers":[1,2],"start_record_time":"2023-11-14T22:13:20.000000Z","end_record_time":"2023-11-14T22:13:21.000000Z","start_log_epoch_time":"1700000000","end_log_epoch_time":"1700000001","raw_lines":["1700000000:[SBE61 ,0396]P +468,T+150471,S38141","1700000001:[PROFIL,0299]    speed_control=10mbar/s"],"ctd_sample_count":1,"ctd_samples":[{"source_line_number":1,"raw_values":{"P":"+468","T":"+150471","S":"38141"},"pressure_cbar_tenths":468,"temperature_mdegc_tenths":150471,"salinity_psu_thousandths":38141}]}
```

Field table: common grouped-episode fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `ctd_sample_count` | integer | no | Number of parsed CTD sample lines in the grouped episode. | samples | Length of `ctd_samples`. |
| `ctd_samples` | array of objects | no | Parsed CTD sample values from any episode line that matches `P,T,S`. Empty when the episode has no sample line. | n/a | CTD sample regex applied to tagged LOG message text. |
| `ctd_samples[].source_line_number` | integer | no | 1-based source LOG line number for this sample. | lines | Grouped episode source line. |
| `ctd_samples[].raw_values` | object | no | Source-literal `P`, `T`, and `S` strings. | source literal | CTD sample regex capture groups. |
| `ctd_samples[].pressure_cbar_tenths` | integer | no | Parsed `P` value in source precision units. | tenths of cbar | `P` capture converted to integer; no scaling conversion. |
| `ctd_samples[].temperature_mdegc_tenths` | integer | no | Parsed `T` value in source precision units. | tenths of mdegC | `T` capture converted to integer; no scaling conversion. |
| `ctd_samples[].salinity_psu_thousandths` | integer | no | Parsed `S` value in source precision units. | thousandths of PSU | `S` capture converted to integer; no scaling conversion. |

Classifier hit rules:

A parsed tagged LOG line joins a CTD episode when:

```text
subsystem in {"SBE", "SBE41", "SBE61", "PROFIL"}
subsystem == "STAGE" and ("SBE41" in message or "SBE61" in message)
subsystem == "STAGE" and the currently active grouped episode is already CTD
```

Contiguous CTD lines are grouped until a non-CTD tagged line, parameter line,
blank line, rollover banner, or malformed line ends the episode.

Within a CTD episode, sample values are parsed from message text with:

```text
\bP\s*(?P<pressure>[+-]?\d+)\s*,\s*T\s*(?P<temperature>[+-]?\d+)\s*,\s*S\s*(?P<salinity>[+-]?\d+)\b
```

Hits:

```text
1700000000:[SBE61 ,0396]P +468,T+150471,S38141
1700000001:[PROFIL,0299]    speed_control=10mbar/s
1687246390:[STAGE ,0091]Stage [1] surfacing 43200s (<93600s) SBE61 
```

Non-hits:

```text
1700000000:[PRESS ,0038]P+20179mbar,T+32767mdegC
1700000001:[STAGE ,0091]Stage [1] surfacing 43200s      # when no CTD episode is active
1700000002:[MAIN  ,0007]P +12,T -34,S +56
```

Overlap / exclusivity: grouped before ordinary classification and mutually
exclusive by source line. Matching lines do not also appear in unclassified.
These lines previously would have been part of broad operational preservation
before `log_operational_records` was dissolved.

Known gaps / edge cases: CTD samples are parsed only from grouped CTD episode
lines. The normalizer does not scale source-precision values to decimal cbar,
mdegC, or PSU, and does not interpret profiling speed or stage semantics.

## `log_testmode_records.jsonl`

Purpose / scope: grouped test-mode console sessions, including tagged LOG
entries, console text, and blank lines while the session is active.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_testmode.LOG","episode_index":0,"line_start_index":1,"line_end_index":4,"source_line_numbers":[1,2,3,4],"start_record_time":"2023-11-14T22:13:20.000000Z","end_record_time":"2023-11-14T22:13:24.000000Z","start_log_epoch_time":"1700000000","end_log_epoch_time":"1700000004","raw_lines":["1700000000:[TESTMD,0053]Enter in test mode? yes/no","Command list for MOBY 4000m","Set params","1700000004:[TESTMD,0252]0100>"]}
```

Field table: common grouped-episode fields only.

Classifier hit rules:

A parsed tagged LOG line starts a testmode episode when:

```text
subsystem == "TESTMD"
```

While testmode is active, all raw lines are appended to the episode, including
blank lines and untagged console output. The episode ends after a tagged line
whose stripped lowercase message matches:

```text
subsystem == "TESTMD" and message in {'"q"', '"quit"'}
message in {"end of test mode", "reboot mermaid board", "reboot float"}
message.startswith("rebooting with code")
```

Hits:

```text
1683036460:[TESTMD,0053]Enter in test mode? yes/no
Command list for MOBY 4000m
1683036482:[SURF  ,0025]Iridium...
1683036824:[TESTMD,0252]0100>
```

Non-hits:

```text
1700000000:[MAIN  ,0007]Command list
1700000001:Command list
1700000002:[SURF  ,0025]Iridium...
```

Those examples do not hit unless a `TESTMD` line has already started an active
testmode episode.

Overlap / exclusivity: grouped before ordinary classification and mutually
exclusive by source line. Matching lines do not also appear in unclassified.
These lines previously would have been part of broad operational preservation
before `log_operational_records` was dissolved.

Known gaps / edge cases: an unterminated testmode episode is flushed at EOF.
Blank lines inside testmode are emitted in `raw_lines` and have corresponding
entries in `source_line_numbers`; assignment accounting ignores only blank raw
lines when checking exact once-per-source-line family assignment.

## `log_transmission_records.jsonl`

Purpose / scope: upload/transmission workflow lines with conservative parsed
artifact, byte, and session fields.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_upload.LOG","source_container":"log","record_time":"2023-11-14T22:13:21.000000Z","log_epoch_time":"1700000001","subsystem":"UPLOAD","code":"0231","message":"\"0100/AAAA0001.MER\" uploaded at 83bytes/s","source_line_number":2,"referenced_artifact":"0100_AAAA0001.MER","rate_bytes_per_s":83,"byte_count":null,"byte_offset":null,"artifact_size_bytes":null,"uploaded_file_count":null,"disconnect_duration_s":null,"raw_line":"1700000001:[UPLOAD,0231]\"0100/AAAA0001.MER\" uploaded at 83bytes/s","transmission_kind":"upload_artifact"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `referenced_artifact` | string or null | yes | Parsed artifact reference with `/` normalized to `_`. | n/a | Regex group `artifact`, when present. |
| `rate_bytes_per_s` | integer or null | yes | Upload rate. | bytes/s | Upload-artifact regex group `rate`. |
| `byte_count` | integer or null | yes | Uploaded/progress byte count. | bytes | Progress regex group `byte_count`. |
| `byte_offset` | integer or null | yes | Resume byte offset. | bytes | Resume regex group `byte_offset`. |
| `artifact_size_bytes` | integer or null | yes | Resume artifact size when present. | bytes | Optional resume regex group. |
| `uploaded_file_count` | integer or null | yes | Count in session summary. | files | Session-summary regex group. |
| `disconnect_duration_s` | integer or null | yes | Disconnect duration. | seconds | Disconnect regex group. |
| `transmission_kind` | string | no | One of the upload/transmission kind values below. | n/a | First matching transmission predicate. |

Classifier hit rules:

Artifact subpattern:

```text
(?P<artifact>\d{2,4}/[A-Za-z0-9]+\.(?:MER|LOG|BIN))
```

Transmission predicates are checked in this order:

```text
"{artifact}" uploaded at (?P<rate>\d+)bytes/s                         # case-insensitive
peer ask to resume {artifact}(?: \((?P<artifact_size_bytes>\d+)bytes\))? from byte (?P<byte_offset>\d+)  # case-insensitive
(?P<byte_count>\d+) bytes in {artifact}                                # case-insensitive
<ERR>\s*upload\b.*?{artifact}                                          # case-insensitive
transfer interrupted\s*,?\s*retry(?: now)?                             # case-insensitive
(?P<uploaded_file_count>\d+) file(?:\(s\)|s)? uploaded                  # case-insensitive
disconnected after (?P<disconnect_duration_s>\d+)s                     # case-insensitive
^Upload data files\.\.\.$                                              # case-insensitive
```

Kind mapping:

```text
upload_artifact
upload_resume
upload_progress_artifact
upload_error_artifact
upload_retry
upload_session_summary
upload_disconnect
upload_batch
```

Hits:

```text
1700000000:[UPLOAD,0248]Upload data files...
1700000001:[UPLOAD,0231]"0070/60B742A0.MER" uploaded at 137bytes/s
1700000002:[MRMAID,0604]1373 bytes in 0026/5D3CDEA0.MER
1700000003:[ZTX   ,486]peer ask to resume 07/5B6A9B02.LOG from byte 1024
1700000004:<ERR>[ZTX   ,472]peer ask to resume 0048/607503A2.MER (118847bytes) from byte 4294967294
1700000006:[SURF  ,0069]transfer interrupted , retry
1700000008:[SURF  ,0014]disconnected after 288s
```

Non-hits:

```text
1700000009:[SURF  ,0025]Iridium...
1700000010:[SURF  ,0226]Go dive (Minimum surface delay expired and no more file to upload)
1700000011:[SURF  ,0056]<WARN>peer mute
1700000013:[SURF  ,0023]failed to connect #1, code -8, net 1, qual 5, dial 1
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. These lines previously would have
been ordinary/base operational rows before `log_operational_records` was
dissolved.

Known gaps / edge cases: this is upload-focused and corpus-driven. It does not
classify generic modem, Iridium, connection-failure, go-dive, or peer-warning
lines unless they match one of the exact predicates above.

## `log_unclassified_records.jsonl`

Purpose / scope: parsed ordinary LOG lines that do not match any specific
single-line family and are not consumed by grouped families.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_misc.LOG","source_container":"log","record_time":"2023-11-14T22:13:24.000000Z","log_epoch_time":"1700000004","subsystem":"SURF","code":"0071","message":"<WARN>timeout","source_line_number":5,"severity":"warn","unclassified_reason":"no_family_match","raw_line":"1700000004:[SURF  ,0071]<WARN>timeout"}
```

Rollover banner representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_misc.LOG","source_container":"log","record_time":"2023-11-14T22:13:24.000000Z","log_epoch_time":"1700000004","subsystem":"ROLLOVER","code":null,"message":"*** switching to 0100/NEXT.LOG ***","source_line_number":5,"switched_to_log_file":"0100_NEXT.LOG","severity":null,"unclassified_reason":"no_family_match","raw_line":"1700000004:*** switching to 0100/NEXT.LOG ***"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `switched_to_log_file` | string | yes | Canonical rollover target LOG filename. Field is present only for rollover banners. | n/a | Rollover regex group `target`, `/` normalized to `_`, `.LOG` default suffix when absent. |
| `severity` | string or null | yes | `err`, `warn`, or null. This key is emitted on every unclassified record. | n/a | Presence of `<ERR>`, `<WARN>`, or `<WRN>` in `message`. |
| `unclassified_reason` | string | no | Currently always `no_family_match`. | n/a | Constant for parsed non-matching lines. |

Classifier hit rules:

Unclassified is the fallback when:

```text
line parses as an ordinary tagged LOG entry or rollover banner
line is not consumed by parameter, testmode, or CTD grouping
line has zero matches among acquisition, ascent_request, gps, transmission, pressure_temperature, battery
```

Rollover banners parse as ordinary unclassified records when a timestamped
non-tagged line has content matching:

```text
^\*\*\*\s+switching to\s+(?P<target>.+?)\s+\*\*\*$     # case-insensitive
```

Hits:

```text
1565060029:[SURF  ,328]7 cmd(s) received
1700000004:[SURF  ,0071]<WARN>timeout
1700000004:*** switching to 0100/NEXT.LOG ***
```

Non-hits:

```text
1700000002:[PRESS ,0038]P+20179mbar,T+32767mdegC
1700000000:[BUOY  ,0656]P+151590mbar
1535842096:[MRMAID,565]1523dbar, -11degC
1565146653:[MAIN  ,507]Pext -45mbar (rng 30mbar)
1564269461:[MAIN  ,408]internal pressure 78680Pa
1700000003:[MONITR,0461]battery 14685mV,   12688uA
1565146650:[MAIN  ,498]Vbat 14681mV (min 13967mV)
1700000001:    bypass 20000ms 120000ms (10000ms 200000ms stored)
1700000000:<ERR>broken wrapper without subsystem tag
not even timestamped
```

The first three non-hits are consumed by specific/grouped families. The last
two are malformed lines, not unclassified records.

Overlap / exclusivity: unclassified is mutually exclusive with every specific
LOG family. Specific-family lines do not also appear here. This family is the
replacement preservation surface for parsed ordinary lines that formerly would
have appeared in dissolved/base operational records.

Known gaps / edge cases: malformed raw lines are reported through run manifest
diagnostics when enabled, or skipped from JSONL output when diagnostics are not
requested; they are not emitted to `log_unclassified_records`.
Severity is a coarse substring check, not a parsed field from the LOG tag.
