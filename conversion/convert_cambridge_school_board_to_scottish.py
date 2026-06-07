import csv
import re
from collections import Counter
from pathlib import Path


NO_PARTY = "None"
VACANCIES = 6


def convert_cambridge_school_board_to_scottish(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    candidates = _candidate_order(input_path)
    candidate_numbers = {candidate: i for i, candidate in enumerate(candidates, start=1)}
    rankings = Counter()
    ballot_count = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rank_columns = _rank_columns(reader.fieldnames or [])

        for row_number, row in enumerate(reader, start=2):
            ranking = []
            seen = set()

            for column in rank_columns:
                value = row[column]
                if value == "":
                    continue
                if value not in candidate_numbers:
                    raise ValueError(f"{input_path}:{row_number}: unknown candidate string {value!r}")
                if value in seen:
                    continue
                ranking.append(candidate_numbers[value])
                seen.add(value)

            if not ranking:
                raise ValueError(f"{input_path}:{row_number}: ballot has no non-empty rank values")

            rankings[tuple(ranking)] += 1
            ballot_count += 1

    year = _year_from_path(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([len(candidates), VACANCIES, ""])

        for ranking, count in sorted(rankings.items()):
            writer.writerow([count, *ranking, ""])

        for i, candidate in enumerate(candidates, start=1):
            writer.writerow([f"Candidate {i}", candidate, NO_PARTY, ""])

        writer.writerow([f"Cambridge School Committee {year}", ""])

    return {
        "input": str(input_path),
        "output": str(output_path),
        "year": year,
        "candidates": len(candidates),
        "vacancies": VACANCIES,
        "ballots": ballot_count,
        "unique_rankings": len(rankings),
    }


def convert_all_cambridge_school_board(
    root="votekit/cambridge",
):
    root = Path(root)
    input_paths = sorted(root.glob("raw_data/ca_ma_school_board_*.csv"))
    if not input_paths:
        raise ValueError(f"No Cambridge school-board source files found under {root}")

    summaries = []
    for input_path in input_paths:
        year = _year_from_path(input_path)
        output_path = root / "school_board" / f"ca_school_{year}.csv"
        summaries.append(
            convert_cambridge_school_board_to_scottish(input_path, output_path)
        )
    return summaries


def _candidate_order(input_path):
    candidates = set()

    with Path(input_path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rank_columns = _rank_columns(reader.fieldnames or [])

        for row in reader:
            for column in rank_columns:
                value = row[column]
                if value != "":
                    candidates.add(value)

    if not candidates:
        raise ValueError(f"{input_path}: no candidate strings found")

    return sorted(candidates, key=lambda value: (value.casefold(), value))


def _rank_columns(fieldnames):
    rank_columns = [field for field in fieldnames if field.lower().startswith("rank")]
    if not rank_columns:
        raise ValueError("No rank columns found")
    return sorted(rank_columns, key=_rank_number)


def _rank_number(column):
    match = re.fullmatch(r"rank(\d+)", column, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid rank column: {column!r}")
    return int(match.group(1))


def _year_from_path(input_path):
    match = re.search(r"(?:^|_)((?:19|20)\d{2})(?:_|\.|$)", input_path.name)
    if not match:
        raise ValueError(f"Could not infer election year from {input_path}")
    return match.group(1)


def main():
    for summary in convert_all_cambridge_school_board():
        print(
            f"{summary['output']}: "
            f"{summary['candidates']} candidates, "
            f"{summary['vacancies']} vacancies, "
            f"{summary['ballots']} ballots, "
            f"{summary['unique_rankings']} unique rankings"
        )


if __name__ == "__main__":
    main()
