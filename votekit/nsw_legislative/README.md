## Details/History.

This directory contains statewide New South Wales Legislative Council STV
profiles for 2015, 2019, and 2023.

## Data Source.

The `.stv` source profiles came from Andrew Conway's ConcreteSTV election
database and were derived from NSW Electoral Commission data.

## Cleaning.

ATL votes were expanded to BTL candidate rankings to make the profiles
compatible with VoteKit's Scottish CSV format.

## File Storage.

Files smaller than 50 MB are stored directly as CSV files. Larger files are
stored as individual ZIP archives in `zipped/` to stay below GitHub's file-size
limit. Each archive contains one CSV with the matching base name.

To extract every archived CSV and place it alongside the uncompressed CSVs,
run the following commands from the repository root:

```bash
cd votekit/nsw_legislative
for archive in zipped/*.zip; do
    unzip -jo "$archive" -d .
done
```

The `-j` option discards directory paths stored inside an archive, while `-o`
replaces an existing local copy without prompting.
