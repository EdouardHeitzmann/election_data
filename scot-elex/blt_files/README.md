# How to Read a BLT file
Row 1 -> Number of candidates number of seats

Rows after row 1 
    # Of ballots of the given type
    # The ballot followed by a 0 to end the line

The ballots are separated from the candidates by a line containing only a zero

The candidates are listed in-order at the end of the ballot.

The last line of the file is the name of the ward


## Example BLT file with Comments

Here is an example BLT file

```
3 2
12 1 0
88 1 3 2 0
14 2 3 0
8 3 0
0
Cand A (Party A)
Cand B (Party B)
Cand C (Party C)
Wardy McWard Town
```

How to read it:

```
3 2                 # There are 3 candidates running for 2 seats
12 1 0              # 12 Bullet votes for candidate 1 were cast
88 1 3 2 0          # 88 Ballots preferring 1 to 3 and 3 to 2 were cast
14 2 3 0
8 3 0
0                   # End of the ballots
Cand A (Party A)    # The name of candidate 1 and possibly their party
Cand B (Party B)
Cand C (Party C)
Wardy McWard Town   # The name of the ward
```
