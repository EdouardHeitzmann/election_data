"""Convert a .blt file into the scot-elex style CSV format."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple


def parse_blt(path: Path) -> Tuple[int, int, List[List[str]], List[str], str]:
    """Return (candidate_count, seat_count, ballots, candidate_names, election_name)."""
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    if not lines:
        raise ValueError(f"{path} is empty")

    try:
        candidate_count, seat_count = (int(x) for x in lines[0].split()[:2])
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unable to read header from {path}") from exc

    ballots: List[List[str]] = []
    idx = 1
    while idx < len(lines):
        line = lines[idx]
        idx += 1
        if line == "0":
            break
        parts = line.split()
        # First value is the ballot count, remaining values are preferences ending with 0.
        count, *prefs = parts
        prefs = [p for p in prefs if p != "0"]
        ballots.append([count, *prefs])

    candidate_names = [lines[idx + i].strip('"') for i in range(candidate_count)]
    election_name = lines[idx + candidate_count].strip('"')
    return candidate_count, seat_count, ballots, candidate_names, election_name


def to_csv_lines(
    candidate_count: int,
    seat_count: int,
    ballots: List[List[str]],
    candidate_names: List[str],
    election_name: str,
) -> List[str]:
    """Build CSV lines matching the scot-elex layout."""
    lines: List[str] = [f"{candidate_count},{seat_count},\n"]

    for ballot in ballots:
        lines.append(",".join(ballot) + ",\n")

    for idx, name in enumerate(candidate_names, start=1):
        lines.append(f'"Candidate {idx}","{name}","blank",\n')

    lines.append(f'"{election_name}",\n')
    return lines


def convert_blt_to_csv(input_path: Path, output_path: Path) -> None:
    """Read a BLT file and write the CSV counterpart."""
    (
        candidate_count,
        seat_count,
        ballots,
        candidate_names,
        election_name,
    ) = parse_blt(input_path)

    output_lines = to_csv_lines(
        candidate_count, seat_count, ballots, candidate_names, election_name
    )
    output_path.write_text("".join(output_lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a .blt file into the scot-elex CSV format."
    )
    parser.add_argument("input", type=Path, help="Path to the source .blt file.")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Where to write the CSV (default: alongside the input).",
    )
    args = parser.parse_args()

    output_path = args.output
    if output_path is None:
        output_path = args.input.with_suffix(".csv")

    convert_blt_to_csv(args.input, output_path)


if __name__ == "__main__":
    main()
