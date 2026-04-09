# Representative LOG Examples

This subset contains 25 representative `LOG` fixtures drawn from:

- `452.020-P-06`
- `467.174-T-0100`

The goal is not exhaustive coverage. This subset is meant for convenient upload,
inspection, and ad hoc comparison across:

- very small files
- very large files
- mid-sized files
- clean files
- files containing `ERR`
- files containing `WARN`
- files containing both `WARN` and `ERR`

Selection approach:

- several of the smallest files from each family
- several of the largest files from each family
- several mid-sized files from each family
- explicit inclusion of clean, `ERR`, `WARN`, and `WARN`+`ERR` examples where available

Notes:

- `452.020-P-06` examples contain many `ERR` cases but no `WARN` cases were found in this family.
- `467.174-T-0100` provides clear `WARN`, `ERR`, and `WARN`+`ERR` examples.

## `452.020-P-06`

| File | Reason |
| --- | --- |
| `06_5B273958.LOG` | Tiny `ERR` example (3 lines) |
| `06_386D4DBA.LOG` | Tiny `ERR` example (3 lines) |
| `06_38871420.LOG` | Small `ERR` example |
| `06_5B0670B9.LOG` | Small clean example |
| `06_3887037A.LOG` | Small clean example |
| `06_65450868.LOG` | Mid-sized `ERR` example |
| `06_5BB630E6.LOG` | Mid-sized `ERR` example |
| `06_64289E82.LOG` | Mid-sized `ERR` example |
| `06_6507C96C.LOG` | Mid-sized clean example |
| `06_64B1871A.LOG` | Mid-sized clean example |
| `06_5BD80EF5.LOG` | Large `ERR` example |
| `06_5DF4BB79.LOG` | Largest clean example |

## `467.174-T-0100`

| File | Reason |
| --- | --- |
| `0100_6478381B.LOG` | Tiny clean example (4 lines) |
| `0100_644BC23A.LOG` | Tiny `WARN`-only example |
| `0100_64784930.LOG` | Tiny `ERR`-only example |
| `0100_64783DBC.LOG` | Tiny `WARN`+`ERR` example |
| `0100_64511916.LOG` | Small clean example |
| `0100_6481688A.LOG` | Small/mid `WARN`-only example |
| `0100_649143FF.LOG` | Mid-sized `WARN`-only example |
| `0100_64895AFD.LOG` | Mid-sized clean example |
| `0100_648169B4.LOG` | Mid-sized `WARN`+`ERR` example |
| `0100_64C773A8.LOG` | Large `WARN`+`ERR` example |
| `0100_65171249.LOG` | Very large `WARN`+`ERR` example |
| `0100_6559EE42.LOG` | Extremely large `WARN`+`ERR` example |
| `0100_68169297.LOG` | Largest `WARN`+`ERR` example |
