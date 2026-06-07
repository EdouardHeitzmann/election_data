# STV Election Data

This repository collects cast vote records for Single Transferable Vote
elections around the world. The goal is to make this data accessible and easy
to load for research.

It also contains a few Instant Runoff Voting elections that were incidentally stored in larger STV datasets, although it is not currently my aim to accumulate IRV data here.

The data is formatted in two ways:

1. VoteKit Scottish `.csv` format, as used by the
   [scot-elex](https://github.com/mggg/scot-elex) repository. This format stores
   the number of seats, candidate names, party affiliations, and ward name.
2. ConcreteSTV JSON `.stv` format, used by Andrew Conway's Rust-based
   [ConcreteSTV](https://github.com/AndrewConway/ConcreteSTV) project.

The `votekit/` and `concrete/` directories contain the public datasets.
`conversion/` contains utilities used to convert and repair them. Source and
license information appears in each collection's README and `LICENSE.md`, and
in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Data Conversion Notes

When no partisan affiliation was available, candidates were assigned the
literal affiliation `None`. This is required because the current VoteKit
Scottish CSV loader rejects empty candidate-party fields. `None` means that no
affiliation is recorded in this dataset; it is not always an accurate description, since in some cases these candidates did receive partisan endorsements.

Australian elections include Above the Line (ATL) votes that rank parties
instead of individual candidates. For the VoteKit CSV copies, ATL votes were
expanded into their deterministic Below the Line (BTL) candidate order. This
preserves the interpreted candidate ranking used in tabulation, but loses the
distinction between ballots originally cast ATL and BTL.

## Using VoteKit

```python
from votekit.cvr_loaders import load_scottish
from votekit.elections import FastSTV

profile, seats, candidates, candidate_parties, ward = load_scottish(
    "path_to_data.csv"
)

election = FastSTV(profile, n_seats=seats)

print(election.election_states[0].scores)
print(election.get_status_df())
```

There are plans to eventually add more detailed tabulation display methods to Votekit, but for now the best way to access the round-by-round tallies is by accessing the `election.election_states`.

## Using ConcreteSTV

In a directory where you're happy cloning the repo:

```bash
git clone https://github.com/AndrewConway/ConcreteSTV.git
cd ConcreteSTV
cargo build --release
```

Choose an `.stv` file, an appropriate ruleset, and an output transcript path:

```bash
./target/release/concrete_stv AEC2019 /path/to/data.stv \
    -t /path/to/output.transcript
```

Open `docs/Viewer.html` in a browser and select the transcript using "Browse."

You can switch out the "AEC2019" ruleset with one of the many other 