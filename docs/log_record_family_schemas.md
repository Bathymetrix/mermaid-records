# LOG Record Family Schemas

This is a developer-facing reference for LOG-derived JSONL families emitted by
`mermaid-records`. Filename examples below use base family filenames such as
`log_gps_records.jsonl`; pipeline outputs normally include the instrument serial
before `.jsonl`, for example `log_gps_records.467.174-T-0100.jsonl`.

The source of truth is `src/mermaid_records/normalize_log.py`.

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

Grouped families (`log_parameter_records.jsonl`, `log_sbe_records.jsonl`, and
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

These fields appear on grouped episode families:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `instrument_id` | string | no | Canonical station/instrument identifier. | n/a | Pipeline context or fallback from LOG path. |
| `instrument_serial` | string | no | Full hardware/dataset serial used in output filenames. | n/a | Pipeline context or fallback from LOG path. |
| `source_file` | string | no | Basename of the source LOG file. | n/a | Source LOG path basename. |
| `episode_index` | integer | no | Zero-based episode number within the source file and family. | n/a | Incremented by grouped parser. |
| `line_start_index` | integer | no | First timestamped line number in the episode. | lines | First grouped line with parsed time. |
| `line_end_index` | integer | no | Last timestamped line number in the episode. | lines | Last grouped line with parsed time. |
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

Purpose / scope: literal battery telemetry lines with voltage and current.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_battery.LOG","source_container":"log","record_time":"2023-11-14T22:13:23.000000Z","log_epoch_time":"1700000003","subsystem":"MONITR","code":"0461","message":"battery 14685mV,   12688uA","source_line_number":4,"voltage_mv":14685,"current_ua":12688,"raw_line":"1700000003:[MONITR,0461]battery 14685mV,   12688uA"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `voltage_mv` | integer | no | Battery voltage. | mV | Regex group `mv`. |
| `current_ua` | integer | no | Battery current. | uA | Regex group `ua`. |

Classifier hit rules:

Regex, case-insensitive, searched anywhere in `message`:

```text
\bbattery\s+(?P<mv>[+-]?\d+)mV,\s+(?P<ua>[+-]?\d+)uA\b
```

Hits:

```text
1700000003:[MONITR,0461]battery 14685mV,   12688uA
1700000003:[MONITR,0461]Battery -1mV, +2uA
```

Non-hits:

```text
1565146650:[MAIN  ,498]Vbat 14681mV (min 13967mV)
1700000003:[MONITR,0461]battery 14685mV
1700000003:[MONITR,0461]bat 14685mV, 12688uA
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. `Vbat ...` lines do not hit this
family and currently route to unclassified if no other family matches. Battery
hits previously would have been ordinary/base operational rows before
`log_operational_records` was dissolved.

Known gaps / edge cases: only the literal word `battery` plus `mV, uA` shape is
recognized; `Vbat`, minimum-voltage summaries, and voltage-only lines are not
classified as battery records.

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
| `raw_values` | object or null | yes | Parsed raw GPS scalar strings, or null for fix attempts. | source literal | Regex capture groups. |

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

Purpose / scope: literal pressure/temperature telemetry observations in mbar
and millidegrees Celsius.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_press.LOG","source_container":"log","record_time":"2023-11-14T22:13:22.000000Z","log_epoch_time":"1700000002","subsystem":"PRESS","code":"0038","message":"P+20179mbar,T+32767mdegC","source_line_number":3,"pressure_mbar":20179,"temperature_mdegc":32767,"raw_line":"1700000002:[PRESS ,0038]P+20179mbar,T+32767mdegC"}
```

Field table: common single-line fields plus:

| Field | Type | Nullable? | Meaning | Units | Source / derivation |
| --- | --- | --- | --- | --- | --- |
| `pressure_mbar` | integer | no | Pressure value. | mbar | Regex group `pressure_mbar`. |
| `temperature_mdegc` | integer | no | Temperature value. | mdegC | Regex group `temperature_mdegc`. |

Classifier hit rules:

Regex, case-sensitive, searched anywhere in `message`:

```text
\bP\s*(?P<pressure_mbar>[+-]?\d+)mbar,\s*T\s*(?P<temperature_mdegc>[+-]?\d+)mdegC\b
```

Hits:

```text
1700000002:[PRESS ,0038]P+20179mbar,T+32767mdegC
1700000000:[PRESS ,0081]P    +0mbar,T-10881mdegC
```

Non-hits:

```text
1565146653:[MAIN  ,507]Pext -45mbar (rng 30mbar)
1700000004:[MAIN  ,0007]New pressure offset: 40mbar
1700000006:[MAIN  ,0007]P +12,T -34,S +56
1700000000:[MAIN  ,408]internal pressure 78680Pa
```

Overlap / exclusivity: mutually exclusive with other LOG families. Matching
lines do not also appear in unclassified. `Pext ...`, `internal pressure ...`,
pressure offset, and `P +12,T -34,S +56` lines do not hit and currently route
to unclassified when no other family matches. Hits previously would have been
ordinary/base operational rows before `log_operational_records` was dissolved.

Known gaps / edge cases: only `P...mbar,T...mdegC` observations are recognized.
Pressure-only, external-pressure, pascal, offset, and SBE-style `P,T,S` lines
are intentionally outside this family.

## `log_sbe_records.jsonl`

Purpose / scope: grouped SBE/PROFIL/STAGE sensor/profiling episodes. The family
preserves raw source lines and does not interpret SBE values.

Representative object:

```json
{"instrument_id":"T0100","instrument_serial":"467.174-T-0100","source_file":"0100_sbe.LOG","episode_index":0,"line_start_index":1,"line_end_index":2,"source_line_numbers":[1,2],"start_record_time":"2023-11-14T22:13:20.000000Z","end_record_time":"2023-11-14T22:13:21.000000Z","start_log_epoch_time":"1700000000","end_log_epoch_time":"1700000001","raw_lines":["1700000000:[SBE61 ,0396]P +20122,T +19514,S +34584","1700000001:[PROFIL,0299]    speed_control=10mbar/s"]}
```

Field table: common grouped-episode fields only.

Classifier hit rules:

A parsed tagged LOG line joins an SBE episode when:

```text
subsystem in {"SBE", "SBE41", "SBE61", "PROFIL"}
subsystem == "STAGE" and ("SBE41" in message or "SBE61" in message)
subsystem == "STAGE" and the currently active grouped episode is already SBE
```

Contiguous SBE lines are grouped until a non-SBE tagged line, parameter line,
blank line, rollover banner, or malformed line ends the episode.

Hits:

```text
1700000000:[SBE61 ,0396]P +20122,T +19514,S +34584
1700000001:[PROFIL,0299]    speed_control=10mbar/s
1687246390:[STAGE ,0091]Stage [1] surfacing 43200s (<93600s) SBE61 
```

Non-hits:

```text
1700000000:[PRESS ,0038]P+20179mbar,T+32767mdegC
1700000001:[STAGE ,0091]Stage [1] surfacing 43200s      # when no SBE episode is active
1700000002:[MAIN  ,0007]P +12,T -34,S +56
```

Overlap / exclusivity: grouped before ordinary classification and mutually
exclusive by source line. Matching lines do not also appear in unclassified.
These lines previously would have been part of broad operational preservation
before `log_operational_records` was dissolved.

Known gaps / edge cases: SBE-style measurements are preserved only as raw
episode lines. The normalizer does not parse `P`, `T`, `S`, salinity,
profiling speed, or stage semantics.

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
Blank lines inside testmode are preserved in `raw_lines` but do not count as
source-line assignments because assignment accounting ignores blank raw lines.

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
| `severity` | string or null | yes | `err`, `warn`, or null. | n/a | Presence of `<ERR>`, `<WARN>`, or `<WRN>` in `message`. |
| `unclassified_reason` | string | no | Currently always `no_family_match`. | n/a | Constant for parsed non-matching lines. |

Classifier hit rules:

Unclassified is the fallback when:

```text
line parses as an ordinary tagged LOG entry or rollover banner
line is not consumed by parameter, testmode, or SBE grouping
line has zero matches among acquisition, ascent_request, gps, transmission, pressure_temperature, battery
```

Rollover banners parse as ordinary unclassified records when a timestamped
non-tagged line has content matching:

```text
^\*\*\*\s+switching to\s+(?P<target>.+?)\s+\*\*\*$     # case-insensitive
```

Hits:

```text
1565146650:[MAIN  ,498]Vbat 14681mV (min 13967mV)
1565146653:[MAIN  ,507]Pext -45mbar (rng 30mbar)
1564269461:[MAIN  ,408]internal pressure 78680Pa
1700000004:[SURF  ,0071]<WARN>timeout
1700000004:*** switching to 0100/NEXT.LOG ***
```

Non-hits:

```text
1700000002:[PRESS ,0038]P+20179mbar,T+32767mdegC
1700000003:[MONITR,0461]battery 14685mV,   12688uA
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
diagnostics when enabled; they are not emitted to `log_unclassified_records`.
Severity is a coarse substring check, not a parsed field from the LOG tag.
