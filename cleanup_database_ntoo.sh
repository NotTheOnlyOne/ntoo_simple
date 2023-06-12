#!/bin/bash

cp database_ntoo.tsv database_ntoo.tsv.bak

cat database_ntoo.tsv | sed s/‚Äò/\'/g > test_clean_database_ntoo.tsv
cat test_clean_database_ntoo.tsv | sed s/‚Äô/\'/g > test_clean_database_ntoo1.tsv
cat test_clean_database_ntoo1.tsv | sed s/‚Äù/\"/g > test_clean_database_ntoo.tsv
cat test_clean_database_ntoo.tsv | sed s/‚Äú/\"/g > test_clean_database_ntoo1.tsv
cat test_clean_database_ntoo1.tsv | sed s/‚Äî/-/g > test_clean_database_ntoo.tsv


diff database_ntoo.tsv test_clean_database_ntoo.tsv
mv test_clean_database_ntoo.tsv database_ntoo.tsv
rm test_clean_database_ntoo1.tsv
