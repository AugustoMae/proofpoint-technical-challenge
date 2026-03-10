# Data Quality Report

## Summary

| Metric | Value |
|--------|-------|
| Total input records   | 36 |
| Total output records  | 10 |
| Discarded entries     | 6 |
| Corrected entries     | 8 |
| Duplicates detected   | 20 |

## Data Quality Rates

| Rate | Value |
|------|-------|
| Output rate (clean records / input)     | 27.8% |
| Correction rate (corrected / input)     | 22.2% |
| Discard rate (discarded / input)        | 16.7% |

## Discard Breakdown

| Reason | Count |
|--------|-------|
| Missing series name                          | 2 |
| Episode number, title and air date missing   | 4 |

## Correction Breakdown by Field

| Field | Corrections Applied |
|-------|--------------------|
| Season Number   | 1 |
| Episode Number  | 1 |
| Episode Title   | 1 |
| Air Date        | 5 |

## Deduplication Strategy

Two records belonging to the same normalized series are considered duplicates when **any** of the following criteria is met:

1. Same `SeasonNumber` and same non-zero `EpisodeNumber`.
2. Both `SeasonNumber` values are 0, same `EpisodeNumber`, and same normalized `EpisodeTitle`.
3. Same `SeasonNumber`, both `EpisodeNumber` values are 0, and same normalized `EpisodeTitle`.

**Normalization** means: trim leading/trailing whitespace, collapse internal whitespace to a single space, convert to lowercase.

After initial grouping, a full **transitive merge** pass is applied so that records connected only indirectly (A matches B and B matches C -> one group) are also collapsed correctly.

Within each duplicate group the **best** record is kept using this priority:

1. Valid `AirDate` preferred over `"Unknown"`.
2. Known `EpisodeTitle` preferred over `"Untitled Episode"`.
3. Non-zero `SeasonNumber` **and** `EpisodeNumber` preferred over 0.
4. If still tied -> first record encountered in the input file is kept.
