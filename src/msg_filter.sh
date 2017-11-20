#!/bin/bash
# Delete nonprint characters
# Delete 0-9a-zA-z and some useless characters
# Turn sequence of empty char to single one
# Delete empty lines
sed 's/[^[:print:]]//g' $1 \
| sed 's/[0-9a-zA-Z+=\./:\"<>|_&#\s\*\-]//g' \
| sed 's/[中国移动|中国联通|中国电信]//g' > $2
# sed '/^ *$/d' > $2
