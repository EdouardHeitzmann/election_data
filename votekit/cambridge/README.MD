## Details/History.

Cambridge has had 9-seat STV for City Council and 6-seat STV School committee since 1941; the data for City Council is available since 2001, and the data for School Committee is available since 2003.

Cambridge uses a simultaneous, continuous, and random transfer process. When a winner is seated, a surplus' worth of ballots is drawn randomly for transfer (one at a time) from those ballots within their pile that list a continuing further preference. When multiple winners reach a quota of votes simultaneously, votes can't transfer from one winner to the other. Also, when surplus transfers from one winner give quota to another candidate, surplus votes from the first winner stop transferring to the second.

Cambridge also uses an additional rule where all candidates with strictly less than 50 votes in the first round of the election are eliminated simultaneously (see [Section 9(g) of their ruleset](https://www.cambridgema.gov/-/media/files/electioncommission/massachusettsgenerallawschapter54a.pdf))

## Data Source.

The 2001-2023 data comes from the [Harvard Dataverse](https://doi.org/10.7910/DVN/STVUET).

## Cleaning.

Cambridge allows ballots with overvotes to keep transferring to their next preferences, so I just removed (rather than truncated) the overvotes from ballots. For City Council, the raw data stopped showing overvotes in 2017.

Their writeins are usually arranged as "Write-In 1," "Write-In 2," and so on until "Write-In 9." I kept all of them in as long as they received any mention in the profile, even though they usually get batch-eliminated in the first round of the election. I only broke this rule for the 2023 School Board data, which had horrifically many such Write-In candidates; for that data I removed any candidate that received zero first-place rankings among all ballots.

## Oddities.

Cambridge's random transfer process makes it hard to replicate the [official tabulations](https://www.cambridgema.gov/departments/electioncommission/electionresults) after the first winner is seated, but the first round tallies and threshold consistently match up. The later rounds are also consistently close to the official results.

The 2013 City Council Tabulation first-round tallies are off by a few votes -- maybe because that year had a recount, and the data comes from before the recount?

The 2015 City Council Official Tabulation record was lost as of the time I cleaned this dataset; but the round 1 tallies I have match up with the officially posted ones.

The 2019, 2021, and 2023 data (for both City Council and School Board) doesn't perfectly match the official tabulation -- quota is off by a few votes, and some first-round tallies are off by a few votes.

The 2007 School Board Election was very close! Re-running the random transfers <100 times is sufficient to produce an alternative result.

The 2009 School Board data is missing from the Harvard Dataverse, although that election is on the record.

The 2013 School Board tabulation is missing from the Cambridge City website's records, so I cross-referenced it against a [secondary source](https://cambridgereview.org/election/details-school-committee/school-committee-election-2013/) instead.
