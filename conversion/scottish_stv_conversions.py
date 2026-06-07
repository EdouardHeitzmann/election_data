import csv
import json
import re
from collections import Counter
from pathlib import Path


EXPECTED_TOP_LEVEL_KEYS = {
    "metadata",
    "atl",
    "atl_types",
    "btl",
    "btl_types",
    "informal",
}

EXPECTED_METADATA_KEYS = {
    "candidates",
    "enrolment",
    "excluded",
    "name",
    "parties",
    "results",
    "source",
    "tie_resolutions",
    "vacancies",
}

NO_PARTY = "None"


def convert_concrete_json_to_scottish_csv(
    input_path,
    output_path,
    keep_atl=False,
    modern_scottish=False,
):
    if keep_atl:
        raise NotImplementedError("keep_atl=True is not supported yet.")

    if modern_scottish:
        raise NotImplementedError("modern_scottish=True is not supported yet.")

    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", encoding="utf-8") as f:
        election = json.load(f)

    _validate_election(election, input_path)

    metadata = election["metadata"]
    candidates = metadata["candidates"]
    num_cands = len(candidates)
    num_vacancies = metadata["vacancies"]
    ballot_counter = Counter()

    for vote in election["btl"]:
        _validate_vote(vote, "candidates")
        _validate_candidate_indexes(vote["candidates"], num_cands)
        ranking = tuple(candidate_idx + 1 for candidate_idx in vote["candidates"])
        ballot_counter[ranking] += vote["n"]

    for atl_vote in election["atl"]:
        btl_vote = atl_to_btl(election, atl_vote)
        ranking = tuple(candidate_idx + 1 for candidate_idx in btl_vote["candidates"])
        ballot_counter[ranking] += btl_vote["n"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([num_cands, num_vacancies, ""])

        for ranking, count in sorted(ballot_counter.items()):
            writer.writerow([count, *ranking, ""])

        for i, candidate in enumerate(candidates, start=1):
            writer.writerow(
                [
                    f"Candidate {i}",
                    candidate["name"],
                    _candidate_party_name(election, candidate),
                    "",
                ]
            )

        writer.writerow([_election_location(election), ""])


def convert_scottish_csv_to_concrete_json(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    election = scottish_csv_to_concrete_json_dict(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(election, f, ensure_ascii=False, separators=(",", ":"))


def scottish_csv_to_concrete_json_dict(input_path):
    input_path = Path(input_path)

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [_strip_trailing_empty_cells(row) for row in csv.reader(f)]

    rows = [row for row in rows if row]
    if len(rows) < 3:
        raise ValueError(f"{input_path}: expected header, ballots, candidates, and location")

    header = rows[0]
    if len(header) != 2:
        raise ValueError(f"{input_path}: first row must be num_cands,num_vacancies")

    num_cands = _parse_positive_int(header[0], input_path, "num_cands")
    num_vacancies = _parse_positive_int(header[1], input_path, "num_vacancies")

    candidate_start = None
    for i, row in enumerate(rows[1:], start=1):
        if row[0].startswith("Candidate "):
            candidate_start = i
            break

    if candidate_start is None:
        raise ValueError(f"{input_path}: no candidate rows found")

    location_index = candidate_start + num_cands
    if location_index >= len(rows):
        raise ValueError(f"{input_path}: missing final location row")
    if location_index != len(rows) - 1:
        raise ValueError(f"{input_path}: unexpected rows after final location row")

    ballot_rows = rows[1:candidate_start]
    candidate_rows = rows[candidate_start:location_index]
    location_row = rows[location_index]

    if len(location_row) != 1:
        raise ValueError(f"{input_path}: final location row must contain exactly one field")
    location = location_row[0]
    if not location:
        raise ValueError(f"{input_path}: final location row must be non-empty")

    candidates, parties = _parse_scottish_candidate_rows(candidate_rows, num_cands, input_path)
    btl = _parse_scottish_ballot_rows(ballot_rows, num_cands, input_path)

    return {
        "metadata": {
            "name": {
                "year": _infer_year(input_path.name),
                "authority": "",
                "name": location,
                "electorate": location,
            },
            "candidates": candidates,
            "parties": parties,
            "source": [{"url": "", "files": [str(input_path)], "comments": "Converted from Scottish CSV"}],
            "results": [],
            "vacancies": num_vacancies,
        },
        "atl": [],
        "btl": btl,
        "informal": 0,
    }


def atl_to_btl(election: dict, atl_vote: dict) -> dict:
    _validate_vote(atl_vote, "parties")

    candidates = election["metadata"]["candidates"]
    parties = election["metadata"].get("parties")
    if parties is None:
        raise ValueError("Cannot convert ATL vote because election has no party metadata")

    btl_candidates = []
    for party_idx in atl_vote["parties"]:
        if not isinstance(party_idx, int) or party_idx < 0 or party_idx >= len(parties):
            raise ValueError(f"Invalid ATL party index: {party_idx!r}")

        party = parties[party_idx]
        party_candidate_idxs = party["candidates"]
        _validate_candidate_indexes(party_candidate_idxs, len(candidates))
        btl_candidates.extend(
            sorted(
                party_candidate_idxs,
                key=lambda candidate_idx: candidates[candidate_idx]["position"],
            )
        )

    return {"candidates": btl_candidates, "n": atl_vote["n"]}


def _parse_scottish_candidate_rows(candidate_rows, num_cands, input_path):
    candidates = []
    parties = []
    party_lookup = {}

    for i, row in enumerate(candidate_rows, start=1):
        if len(row) != 3:
            raise ValueError(f"{input_path}: candidate row {i} must have 3 fields: {row!r}")
        expected_label = f"Candidate {i}"
        if row[0] != expected_label:
            raise ValueError(f"{input_path}: expected {expected_label!r}, got {row[0]!r}")
        if not row[1]:
            raise ValueError(f"{input_path}: candidate {i} has empty name")
        if not row[2]:
            raise ValueError(f"{input_path}: candidate {i} has empty party affiliation")

        party_name = row[2]
        if party_name not in party_lookup:
            party_lookup[party_name] = len(parties)
            parties.append(
                {
                    "column_id": _party_column_id(len(parties), party_name),
                    "name": party_name,
                    "atl_allowed": False,
                    "candidates": [],
                }
            )

        party_idx = party_lookup[party_name]
        candidate_idx = i - 1
        parties[party_idx]["candidates"].append(candidate_idx)
        candidates.append({"name": row[1], "party": party_idx, "position": len(parties[party_idx]["candidates"])})

    if len(candidates) != num_cands:
        raise ValueError(f"{input_path}: expected {num_cands} candidates, found {len(candidates)}")

    return candidates, parties


def _parse_scottish_ballot_rows(ballot_rows, num_cands, input_path):
    btl = []
    for row_number, row in enumerate(ballot_rows, start=2):
        if len(row) < 2:
            raise ValueError(f"{input_path}: ballot row {row_number} has no ranking")

        count = _parse_positive_int(row[0], input_path, f"ballot row {row_number} count")
        ranking = [
            _parse_positive_int(value, input_path, f"ballot row {row_number} ranking")
            for value in row[1:]
        ]
        if any(candidate_num > num_cands for candidate_num in ranking):
            raise ValueError(f"{input_path}: ballot row {row_number} has candidate above {num_cands}")
        if len(ranking) != len(set(ranking)):
            raise ValueError(f"{input_path}: ballot row {row_number} has duplicate candidates")

        btl.append({"candidates": [candidate_num - 1 for candidate_num in ranking], "n": count})

    return btl


def _validate_election(election: dict, source: Path) -> None:
    if not isinstance(election, dict):
        raise ValueError(f"{source}: expected top-level JSON object")

    keys = set(election)
    required = {"metadata", "atl", "btl", "informal"}
    missing = required - keys
    unexpected = keys - EXPECTED_TOP_LEVEL_KEYS

    if missing:
        raise ValueError(f"{source}: missing top-level keys: {sorted(missing)}")
    if unexpected:
        raise ValueError(f"{source}: unexpected top-level keys: {sorted(unexpected)}")
    if not isinstance(election["atl"], list):
        raise ValueError(f"{source}: atl must be a list")
    if not isinstance(election["btl"], list):
        raise ValueError(f"{source}: btl must be a list")
    if not isinstance(election["informal"], int) or election["informal"] < 0:
        raise ValueError(f"{source}: informal must be a non-negative integer")

    metadata = election["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError(f"{source}: metadata must be an object")

    metadata_required = {"name", "candidates", "vacancies"}
    metadata_missing = metadata_required - set(metadata)
    metadata_unexpected = set(metadata) - EXPECTED_METADATA_KEYS
    if metadata_missing:
        raise ValueError(f"{source}: missing metadata keys: {sorted(metadata_missing)}")
    if metadata_unexpected:
        raise ValueError(f"{source}: unexpected metadata keys: {sorted(metadata_unexpected)}")

    if not isinstance(metadata["vacancies"], int) or metadata["vacancies"] <= 0:
        raise ValueError(f"{source}: vacancies must be a positive integer")

    name = metadata["name"]
    if not isinstance(name, dict):
        raise ValueError(f"{source}: metadata.name must be an object")
    for key in ["year", "electorate"]:
        if not isinstance(name.get(key), str) or not name[key].strip():
            raise ValueError(f"{source}: metadata.name.{key} must be a non-empty string")

    candidates = metadata["candidates"]
    parties = metadata.get("parties")
    if not candidates:
        raise ValueError(f"{source}: candidates must be non-empty")
    if not isinstance(candidates, list) or not all(isinstance(c, dict) for c in candidates):
        raise ValueError(f"{source}: candidates must be a list of objects")
    if parties is not None and (
        not isinstance(parties, list) or not all(isinstance(p, dict) for p in parties)
    ):
        raise ValueError(f"{source}: parties must be a list of objects")
    if election["atl"] and parties is None:
        raise ValueError(f"{source}: ATL votes are present but metadata.parties is missing")

    for i, candidate in enumerate(candidates):
        if not isinstance(candidate.get("name"), str) or not candidate["name"].strip():
            raise ValueError(f"{source}: candidate {i} has no name")
        if not isinstance(candidate.get("position"), int) or candidate["position"] <= 0:
            raise ValueError(f"{source}: candidate {i} has invalid position")
        party_idx = candidate.get("party")
        if parties is None:
            if party_idx is not None:
                raise ValueError(f"{source}: candidate {i} has party index but parties are missing")
        elif not isinstance(party_idx, int) or party_idx < 0 or party_idx >= len(parties):
            raise ValueError(f"{source}: candidate {i} has invalid party index")

    if parties is not None:
        for party_idx, party in enumerate(parties):
            if "candidates" not in party:
                raise ValueError(f"{source}: party {party_idx} has no candidates field")
            _validate_candidate_indexes(party["candidates"], len(candidates))
            positions = [candidates[candidate_idx]["position"] for candidate_idx in party["candidates"]]
            if len(positions) != len(set(positions)):
                raise ValueError(f"{source}: party {party_idx} has duplicate candidate positions")

    sources = metadata.get("source", [])
    if not isinstance(sources, list):
        raise ValueError(f"{source}: metadata.source must be a list")
    for source_idx, source_record in enumerate(sources):
        if not isinstance(source_record, dict):
            raise ValueError(f"{source}: metadata.source[{source_idx}] must be an object")
        if set(source_record) != {"url", "files", "comments"}:
            raise ValueError(
                f"{source}: metadata.source[{source_idx}] must contain url, files, and comments"
            )
        if not isinstance(source_record["url"], str):
            raise ValueError(f"{source}: metadata.source[{source_idx}].url must be a string")
        if not isinstance(source_record["files"], list) or not all(
            isinstance(filename, str) for filename in source_record["files"]
        ):
            raise ValueError(
                f"{source}: metadata.source[{source_idx}].files must be a list of strings"
            )
        if source_record["comments"] is not None and not isinstance(
            source_record["comments"], str
        ):
            raise ValueError(
                f"{source}: metadata.source[{source_idx}].comments must be a string or null"
            )


def _validate_vote(vote: dict, ranking_key: str) -> None:
    if not isinstance(vote, dict):
        raise ValueError(f"Vote must be an object: {vote!r}")
    if set(vote) != {ranking_key, "n"}:
        raise ValueError(f"Vote must only contain {ranking_key!r} and 'n': {vote!r}")
    if not isinstance(vote["n"], int) or vote["n"] <= 0:
        raise ValueError(f"Vote count must be a positive integer: {vote!r}")
    if not isinstance(vote[ranking_key], list) or not vote[ranking_key]:
        raise ValueError(f"Vote ranking must be a non-empty list: {vote!r}")
    if len(vote[ranking_key]) != len(set(vote[ranking_key])):
        raise ValueError(f"Vote ranking contains duplicate entries: {vote!r}")


def _validate_candidate_indexes(candidate_idxs: list[int], num_cands: int) -> None:
    if not isinstance(candidate_idxs, list):
        raise ValueError(f"Candidate indexes must be a list: {candidate_idxs!r}")
    for candidate_idx in candidate_idxs:
        if not isinstance(candidate_idx, int) or candidate_idx < 0 or candidate_idx >= num_cands:
            raise ValueError(f"Invalid candidate index: {candidate_idx!r}")


def _candidate_party_name(election: dict, candidate: dict) -> str:
    parties = election["metadata"].get("parties")
    if parties is None or "party" not in candidate:
        return NO_PARTY

    party = parties[candidate["party"]]
    return party.get("name") or party.get("column_id") or NO_PARTY


def _election_location(election: dict) -> str:
    name = election["metadata"]["name"]
    return " ".join(
        str(part)
        for part in [name.get("name"), name.get("year"), name.get("electorate")]
        if part
    )


def _strip_trailing_empty_cells(row):
    row = [cell.strip() for cell in row]
    while row and row[-1] == "":
        row.pop()
    return row


def _parse_positive_int(value, input_path, field_name):
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{input_path}: {field_name} must be an integer: {value!r}") from exc
    if parsed <= 0:
        raise ValueError(f"{input_path}: {field_name} must be positive: {value!r}")
    return parsed


def _party_column_id(party_idx, party_name):
    if party_name == NO_PARTY:
        return "UG"
    return _spreadsheet_column_name(party_idx)


def _spreadsheet_column_name(index):
    index += 1
    chars = []
    while index:
        index, remainder = divmod(index - 1, 26)
        chars.append(chr(ord("A") + remainder))
    return "".join(reversed(chars))


def _infer_year(filename):
    match = re.search(r"(?:^|_)((?:19|20)\d{2})(?:_|\.|$)", filename)
    return match.group(1) if match else ""
