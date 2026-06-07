import csv
from collections import Counter
from pathlib import Path


NO_PARTY = "None"
SKIP_RANK_VALUES = {""}


CONTESTS = [
    {
        "input": "2025-BET-Cast-Vote-Record.csv",
        "output": "board_of_taxation/bot_2025.csv",
        "vacancies": 2,
        "location": "Minneapolis Board of Estimate and Taxation 2025",
    },
    {
        "input": "2025-Park-At-Large-CVR.csv",
        "output": "park_board/pb_2025.csv",
        "vacancies": 3,
        "location": "Minneapolis Park Board At Large 2025",
    },
]


def convert_minneapolis_cvr_to_scottish_csv(input_path, output_path, vacancies, location):
    input_path = Path(input_path)
    output_path = Path(output_path)

    candidates = _candidate_order(input_path)
    candidate_numbers = {candidate: i for i, candidate in enumerate(candidates, start=1)}
    rankings = Counter()
    blank_count = 0
    total_count = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rank_columns = _rank_columns(reader.fieldnames or [])

        for row_number, row in enumerate(reader, start=2):
            count = _positive_int(row["Count"], input_path, row_number)
            total_count += count

            ranking = []
            seen = set()
            for column in rank_columns:
                value = row[column].strip()
                if value.lower() in SKIP_RANK_VALUES:
                    continue
                if value not in candidate_numbers:
                    raise ValueError(f"{input_path}:{row_number}: unknown candidate {value!r}")
                if value in seen:
                    continue
                ranking.append(candidate_numbers[value])
                seen.add(value)

            if ranking:
                rankings[tuple(ranking)] += count
            else:
                blank_count += count

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([len(candidates), vacancies, ""])

        for ranking, count in sorted(rankings.items()):
            writer.writerow([count, *ranking, ""])

        for i, candidate in enumerate(candidates, start=1):
            writer.writerow([f"Candidate {i}", candidate, NO_PARTY, ""])

        writer.writerow([location, ""])

    return {
        "input": str(input_path),
        "output": str(output_path),
        "candidates": len(candidates),
        "vacancies": vacancies,
        "total_count": total_count,
        "nonblank_count": total_count - blank_count,
        "blank_count": blank_count,
        "unique_rankings": len(rankings),
    }


def convert_all_minneapolis_2025(
    input_dir="votekit/minneapolis/raw_data",
    output_dir="votekit/minneapolis",
):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    summaries = []
    for contest in CONTESTS:
        summaries.append(
            convert_minneapolis_cvr_to_scottish_csv(
                input_path=input_dir / contest["input"],
                output_path=output_dir / contest["output"],
                vacancies=contest["vacancies"],
                location=contest["location"],
            )
        )
    return summaries


def _candidate_order(input_path):
    candidates = set()

    with Path(input_path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rank_columns = _rank_columns(reader.fieldnames or [])

        for row in reader:
            for column in rank_columns:
                value = row[column].strip()
                if value.lower() not in SKIP_RANK_VALUES:
                    candidates.add(value)

    return sorted(candidates, key=lambda value: (value == "UWI", value.casefold()))


def _rank_columns(fieldnames):
    rank_columns = [field for field in fieldnames if "Choice" in field]
    if not rank_columns:
        raise ValueError("No rank columns found")
    return rank_columns


def _positive_int(value, input_path, row_number):
    try:
        count = int(value)
    except ValueError as exc:
        raise ValueError(f"{input_path}:{row_number}: Count must be an integer: {value!r}") from exc
    if count <= 0:
        raise ValueError(f"{input_path}:{row_number}: Count must be positive: {value!r}")
    return count


def main():
    for summary in convert_all_minneapolis_2025():
        print(
            f"{summary['output']}: "
            f"{summary['candidates']} candidates, {summary['vacancies']} vacancies, "
            f"{summary['nonblank_count']} nonblank ballots, "
            f"{summary['blank_count']} blank ballots omitted, "
            f"{summary['unique_rankings']} unique rankings"
        )


if __name__ == "__main__":
    main()
