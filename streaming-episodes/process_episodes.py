import csv
import datetime
import re
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# Text normalization and date validation
# ---------------------------------------------------------------------------

def normalize_text(text):
    """Normalize text for comparisons: trim, lowercase and collapse spaces."""
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def validate_date(d):
    """
    Check if a string is a valid date in YYYY-MM-DD format.

    Some invalid values like '0000-00-00' or '2022-40-99' may pass strptime
    on certain systems, so we also verify the parsed values explicitly.
    """
    if not d:
        return False
    try:
        dt = datetime.datetime.strptime(d.strip(), '%Y-%m-%d')

        # Reject clearly invalid values
        if dt.year == 0 or dt.month < 1 or dt.month > 12 or dt.day < 1 or dt.day > 31:
            return False

        # Let the standard library confirm the date really exists
        datetime.date(dt.year, dt.month, dt.day)
        return True
    except (ValueError, OverflowError):
        return False


# ---------------------------------------------------------------------------
# Record parsing and correction
# ---------------------------------------------------------------------------

def correct_record(row):
    """
    Parse a CSV row and apply the correction rules from the challenge.

    Returns:
        record (dict): cleaned record
        was_corrected (bool): True if any field had to be fixed
        correction_details (dict): which specific fields were corrected
    """
    series   = row[0].strip() if len(row) > 0 else ""
    season_s = row[1].strip() if len(row) > 1 else ""
    ep_num_s = row[2].strip() if len(row) > 2 else ""
    title    = row[3].strip() if len(row) > 3 else ""
    air_date = row[4].strip() if len(row) > 4 else ""

    field_corrected = False
    correction_details = {
        'season':   False,
        'ep_num':   False,
        'title':    False,
        'air_date': False,
    }

    # --- Season Number ---
    try:
        season = int(season_s)
        if season < 0:
            season = 0
            field_corrected = True
            correction_details['season'] = True
    except (ValueError, TypeError):
        season = 0
        if season_s != "":
            field_corrected = True
            correction_details['season'] = True

    # --- Episode Number ---
    try:
        ep_num = int(ep_num_s)
        if ep_num < 0:
            ep_num = 0
            field_corrected = True
            correction_details['ep_num'] = True
    except (ValueError, TypeError):
        ep_num = 0
        if ep_num_s != "":
            field_corrected = True
            correction_details['ep_num'] = True

    # --- Episode Title ---
    if not title:
        title = "Untitled Episode"
        field_corrected = True
        correction_details['title'] = True

    # --- Air Date ---
    if not validate_date(air_date):
        air_date = "Unknown"
        field_corrected = True
        correction_details['air_date'] = True

    record = {
        'series':      series,
        'season':      season,
        'ep_num':      ep_num,
        'title':       title,
        'air_date':    air_date,
        'norm_series': normalize_text(series),
        'norm_title':  normalize_text(title),
    }

    return record, field_corrected, correction_details


def should_discard(record):
    """
    Determine if a record should be discarded and why.

    Returns:
        (bool, str): (should_discard, reason)
    """
    if not record['series']:
        return True, "missing_series"

    ep_missing    = record['ep_num'] == 0
    title_missing = record['title'] == "Untitled Episode"
    date_missing  = record['air_date'] == "Unknown"

    if ep_missing and title_missing and date_missing:
        return True, "all_identifying_fields_missing"

    return False, ""


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def match(r1, r2):
    """Return True if two records refer to the same episode."""
    if r1['norm_series'] != r2['norm_series']:
        return False

    s1, s2 = r1['season'],     r2['season']
    e1, e2 = r1['ep_num'],     r2['ep_num']
    t1, t2 = r1['norm_title'], r2['norm_title']

    # Same series + season + episode number (both non-zero)
    if s1 == s2 and e1 == e2 and e1 != 0:
        return True

    # Missing season but same episode number and title
    if s1 == 0 and s2 == 0 and e1 == e2 and t1 == t2:
        return True

    # Missing episode number but same season and title
    if s1 == s2 and e1 == 0 and e2 == 0 and t1 == t2:
        return True

    return False


def merge_groups(groups):
    """
    Merge groups that are indirectly connected.

    Example: A matches B, B matches C -> all three end up in one group.
    """
    changed = True
    while changed:
        changed = False
        new_groups = []

        for group in groups:
            merged = False

            for existing in new_groups:
                if any(match(r1, r2) for r1 in group for r2 in existing):
                    existing.extend(group)
                    merged = True
                    changed = True
                    break

            if not merged:
                new_groups.append(group)

        groups = new_groups

    return groups


def select_best(group):
    """
    Select the best record from a duplicate group.

    Priority:
        1. Valid air date
        2. Known title
        3. Valid season and episode number
        4. First record encountered
    """
    scored = []

    for idx, r in enumerate(group):
        score = 0

        if r['air_date'] != "Unknown":
            score += 4
        if r['title'] != "Untitled Episode":
            score += 2
        if r['season'] != 0 and r['ep_num'] != 0:
            score += 1

        scored.append((score, idx, r))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][2]


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main(input_file):
    groups          = []
    total_input     = 0
    discarded       = 0
    corrected_count = 0

    # Counters for detailed report
    discard_reasons   = defaultdict(int)
    field_corrections = defaultdict(int)

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header

        for row in reader:
            total_input += 1

            record, was_corrected, correction_details = correct_record(row)

            discard, reason = should_discard(record)
            if discard:
                discarded += 1
                discard_reasons[reason] += 1
                continue                 # do NOT count discarded as corrected

            if was_corrected:
                corrected_count += 1
                for field, was_fixed in correction_details.items():
                    if was_fixed:
                        field_corrections[field] += 1

            # Add record to an existing group or create a new one
            found = False

            for group in groups:
                if any(match(record, g) for g in group):
                    group.append(record)
                    found = True
                    break

            if not found:
                groups.append([record])

    # Fix duplicate groups connected indirectly
    groups = merge_groups(groups)

    clean_records  = [select_best(g) for g in groups]
    num_duplicates = sum(len(g) - 1 for g in groups)
    output_records = len(clean_records)

    # Compute rates
    quality_rate    = (output_records / total_input * 100) if total_input else 0
    correction_rate = (corrected_count / total_input * 100) if total_input else 0
    discard_rate    = (discarded / total_input * 100) if total_input else 0

    # --- Write cleaned catalog ---
    with open('episodes_clean.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['SeriesName', 'SeasonNumber', 'EpisodeNumber',
                         'EpisodeTitle', 'AirDate'])

        for r in clean_records:
            writer.writerow([r['series'], r['season'], r['ep_num'],
                             r['title'], r['air_date']])

    # --- Write quality report ---
    with open('report.md', 'w', encoding='utf-8') as f:

        f.write("# Data Quality Report\n\n")

        # General summary
        f.write("## Summary\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total input records   | {total_input} |\n")
        f.write(f"| Total output records  | {output_records} |\n")
        f.write(f"| Discarded entries     | {discarded} |\n")
        f.write(f"| Corrected entries     | {corrected_count} |\n")
        f.write(f"| Duplicates detected   | {num_duplicates} |\n\n")

        # Quality rates
        f.write("## Data Quality Rates\n\n")
        f.write(f"| Rate | Value |\n")
        f.write(f"|------|-------|\n")
        f.write(f"| Output rate (clean records / input)     | {quality_rate:.1f}% |\n")
        f.write(f"| Correction rate (corrected / input)     | {correction_rate:.1f}% |\n")
        f.write(f"| Discard rate (discarded / input)        | {discard_rate:.1f}% |\n\n")

        # Discard breakdown
        f.write("## Discard Breakdown\n\n")
        f.write(f"| Reason | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Missing series name                          | {discard_reasons.get('missing_series', 0)} |\n")
        f.write(f"| Episode number, title and air date missing   | {discard_reasons.get('all_identifying_fields_missing', 0)} |\n\n")

        # Correction breakdown by field
        f.write("## Correction Breakdown by Field\n\n")
        f.write(f"| Field | Corrections Applied |\n")
        f.write(f"|-------|--------------------|\n")
        f.write(f"| Season Number   | {field_corrections.get('season', 0)} |\n")
        f.write(f"| Episode Number  | {field_corrections.get('ep_num', 0)} |\n")
        f.write(f"| Episode Title   | {field_corrections.get('title', 0)} |\n")
        f.write(f"| Air Date        | {field_corrections.get('air_date', 0)} |\n\n")

        # Deduplication strategy
        f.write("## Deduplication Strategy\n\n")
        f.write(
            "Two records belonging to the same normalized series are considered "
            "duplicates when **any** of the following criteria is met:\n\n"
            "1. Same `SeasonNumber` and same non-zero `EpisodeNumber`.\n"
            "2. Both `SeasonNumber` values are 0, same `EpisodeNumber`, "
            "and same normalized `EpisodeTitle`.\n"
            "3. Same `SeasonNumber`, both `EpisodeNumber` values are 0, "
            "and same normalized `EpisodeTitle`.\n\n"
            "**Normalization** means: trim leading/trailing whitespace, "
            "collapse internal whitespace to a single space, convert to lowercase.\n\n"
            "After initial grouping, a full **transitive merge** pass is applied so "
            "that records connected only indirectly (A matches B and B matches C -> "
            "one group) are also collapsed correctly.\n\n"
            "Within each duplicate group the **best** record is kept using this priority:\n\n"
            "1. Valid `AirDate` preferred over `\"Unknown\"`.\n"
            "2. Known `EpisodeTitle` preferred over `\"Untitled Episode\"`.\n"
            "3. Non-zero `SeasonNumber` **and** `EpisodeNumber` preferred over 0.\n"
            "4. If still tied -> first record encountered in the input file is kept.\n"
        )

    print(f"Done. {output_records} clean records written to episodes_clean.csv")
    print("Report written to report.md")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_episodes.py <input_csv>")
        sys.exit(1)

    main(sys.argv[1])