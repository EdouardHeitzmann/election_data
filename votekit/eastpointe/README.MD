## Details/History.

Eastpointe had 2-seat STV for its City Council for 2 elections in 2019 and 2021. This change happened because of a [Consent Decree](https://vhdshf2oms2wcnsvk7sdv3so.blob.core.windows.net/thearp-media/documents/J.M._for_Entry_of_Consent_Judgment_and_Decree_6.5.19_1i12jmD.pdf) pursuant to a VRA case. The decree was only binding for a period of 4 years, and Council Elections reverted to block plurality at large after it lapsed.

## Data Source.

All of the data here comes from the [Harvard Dataverse](https://doi.org/10.7910/DVN/STVUET).

## Cleaning.

I left in ballots with preferences for "writein" in 2019 because removing them would usually change the value of quota (or create empty ballots), which would be more confusing than leaving them in. The 2021 data had write-ins already cleaned out.

The way that Eastpointe dealt with overvotes was by truncating ballots at the position of the overvote. This occasionally results in empty ballots, which I chose to remove from the data, to keep the value of quota consistent with the given one.

Eastpointe rules don't say anything about repeat rankings within the same ballot; I chose to remove these repetitions.

## Oddities.

Neither of my tabulations match up perfectly with the officially posted ones for [2019](https://macombgovdocs.org/clerk/electionresults/2019/November19/6000.html) and [2021](https://macombgovdocs.org/clerk/electionresults/2021/November21/eastpointe.html) -- first-round tallies are consistently one or two ballots off (and the value of quota is also off by one ballot in both years).
