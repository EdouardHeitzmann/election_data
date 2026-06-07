import argparse
import csv
import re
import shlex
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CandidateFix:
    csv_path: Path
    candidate_number: int
    old_name: str
    new_name: str
    reason: str


@dataclass
class CandidateWarning:
    csv_path: Path
    candidate_number: int | None
    message: str


def fix_scot_elex_candidate_names(
    scot_elex_root="votekit/scot-elex",
    apply=False,
):
    root = Path(scot_elex_root)
    blt_root = root / "blt_files"
    if not blt_root.is_dir():
        raise ValueError(f"Missing BLT directory: {blt_root}")

    fixes = []
    warnings = []

    csv_paths = sorted(
        path
        for path in root.glob("*_cands/*.csv")
        if path.parent.name != "blt_files"
    )
    if not csv_paths:
        raise ValueError(f"No Scottish CSV files found under {root}")

    for csv_path in csv_paths:
        blt_path = blt_root / csv_path.parent.name / f"{csv_path.stem}.blt"
        if not blt_path.exists():
            warnings.append(CandidateWarning(csv_path, None, f"Missing BLT file: {blt_path}"))
            continue

        rows = _read_csv_rows(csv_path)
        csv_candidates = _candidate_rows_from_csv(rows, csv_path)
        try:
            blt_candidates = _candidate_names_from_blt(blt_path)
        except ValueError as exc:
            warnings.append(CandidateWarning(csv_path, None, str(exc)))
            continue

        if len(csv_candidates) != len(blt_candidates):
            warnings.append(
                CandidateWarning(
                    csv_path,
                    None,
                    f"Candidate count mismatch: CSV has {len(csv_candidates)}, BLT has {len(blt_candidates)}",
                )
            )
            continue

        rows_changed = False
        for candidate_number, (row_index, row, blt_name) in enumerate(
            zip((item[0] for item in csv_candidates), (item[1] for item in csv_candidates), blt_candidates),
            start=1,
        ):
            if len(row) < 2:
                warnings.append(CandidateWarning(csv_path, candidate_number, "Malformed CSV candidate row"))
                continue

            old_name = row[1]
            new_name = _csv_style_name(blt_name)
            reason = _safe_fix_reason(old_name, new_name)

            if reason is None:
                if _normalized_name(old_name) != _normalized_name(new_name):
                    warnings.append(
                        CandidateWarning(
                            csv_path,
                            candidate_number,
                            f"Name mismatch not auto-fixed: {old_name!r} vs BLT {new_name!r}",
                        )
                    )
                continue

            if old_name == new_name:
                continue

            fixes.append(CandidateFix(csv_path, candidate_number, old_name, new_name, reason))
            if apply:
                rows[row_index][1] = new_name
                rows_changed = True

        if apply and rows_changed:
            _write_csv_rows(csv_path, rows)

    return fixes, warnings


def _read_csv_rows(csv_path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def _write_csv_rows(csv_path, rows):
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def _candidate_rows_from_csv(rows, csv_path):
    candidates = []
    for row_index, row in enumerate(rows):
        if row and row[0].startswith("Candidate "):
            expected = f"Candidate {len(candidates) + 1}"
            if row[0] != expected:
                raise ValueError(f"{csv_path}: expected {expected}, got {row[0]}")
            candidates.append((row_index, row))
    return candidates


def _candidate_names_from_blt(blt_path):
    lines = blt_path.read_text(encoding="utf-8-sig").splitlines()
    if not lines:
        raise ValueError(f"{blt_path}: empty BLT file")

    try:
        num_candidates = int(lines[0].split()[0])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"{blt_path}: invalid BLT header") from exc

    ballot_end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "0":
            ballot_end_index = i
            break

    if ballot_end_index is None:
        raise ValueError(f"{blt_path}: could not find BLT ballot terminator")

    candidate_lines = lines[ballot_end_index + 1 : ballot_end_index + 1 + num_candidates]
    if len(candidate_lines) != num_candidates:
        raise ValueError(f"{blt_path}: expected {num_candidates} candidate lines")

    names = [_candidate_name_from_blt_line(line) for line in candidate_lines]
    if any(not name for name in names):
        raise ValueError(f"{blt_path}: parsed an empty candidate name")

    return names


def _candidate_name_from_blt_line(line):
    line = line.strip()

    alternative_match = re.match(r"^#\s*ALTERNATIVE NAME\s+\d+:\s*(?P<rest>.*)$", line, re.I)
    if alternative_match:
        line = alternative_match.group("rest").strip()

    if line.startswith('"'):
        csv_parts = next(csv.reader([line]))
        if csv_parts:
            field = csv_parts[0].strip()
            quoted_chunks = re.findall(r'"([^"]+)"', field)
            before_first_quote = field.split('"', 1)[0].strip()

            if quoted_chunks:
                if before_first_quote and not _looks_like_party_label(before_first_quote):
                    return before_first_quote
                return quoted_chunks[0].strip()

            try:
                shell_parts = shlex.split(line)
            except ValueError:
                shell_parts = []
            if len(shell_parts) >= 2:
                return shell_parts[0].strip()
            return field.strip('" ')

    if line.count("(") != line.count(")"):
        return line

    previous = None
    while previous != line:
        previous = line
        line = re.sub(r"\s*\([^()]*\)\s*$", "", line).strip()

    return line


def _safe_fix_reason(old_name, new_name):
    old_norm = _normalized_name(old_name)
    new_norm = _normalized_name(new_name)

    if old_name == new_name:
        return None
    if "\ufffd" in new_name:
        return None
    if _looks_mojibaked(new_name):
        return None
    if new_name.count("(") != new_name.count(")"):
        return None
    if old_norm == new_norm and not _has_non_ascii(old_name) and _has_non_ascii(new_name):
        return "accent-restoration"
    if new_norm.startswith(old_norm) and len(new_norm) > len(old_norm):
        return "truncated-prefix"
    if len(new_norm) > len(old_norm) and _token_prefix_match(old_name, new_name):
        return "truncated-token-prefix"
    return None


def _token_prefix_match(old_name, new_name):
    old_tokens = [_normalized_name(token) for token in old_name.split()]
    new_tokens = [_normalized_name(token) for token in new_name.split()]
    if not old_tokens or len(old_tokens) > len(new_tokens):
        return False
    return all(new_token.startswith(old_token) for old_token, new_token in zip(old_tokens, new_tokens))


def _normalized_name(name):
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_name = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_name.lower())


def _has_non_ascii(value):
    return any(ord(char) > 127 for char in value)


def _looks_mojibaked(value):
    return any(marker in value for marker in ["Ã", "ã", "Â", "â€"])


def _csv_style_name(blt_name):
    return " ".join(blt_name.split()).title()


def _looks_like_party_label(value):
    tokens = value.split()
    known = {
        "con",
        "grn",
        "ind",
        "lab",
        "ld",
        "lib",
        "nf",
        "snp",
        "soc",
        "sol",
        "sscp",
        "ssp",
        "ukip",
    }
    if len(tokens) != 1:
        return False
    token = tokens[0]
    return token.lower().strip(".") in known or token == token.upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="votekit/scot-elex")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fixes, warnings = fix_scot_elex_candidate_names(args.root, apply=args.apply)

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"{mode}: {len(fixes)} fixable candidate names")
    for fix in fixes:
        print(
            f"{fix.csv_path}: Candidate {fix.candidate_number}: "
            f"{fix.old_name!r} -> {fix.new_name!r} ({fix.reason})"
        )

    print(f"Warnings: {len(warnings)}")
    for warning in warnings:
        candidate = "" if warning.candidate_number is None else f" Candidate {warning.candidate_number}:"
        print(f"{warning.csv_path}:{candidate} {warning.message}")


if __name__ == "__main__":
    main()
