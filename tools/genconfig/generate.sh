#!/bin/sh
cat .config | grep -v "^#" |egrep -xv "[[:space:]]*" > tmpconf
while read -r line; do  echo "#define "$line | sed 's/=y//g' | sed 's/=/ /g';done < tmpconf > config.h
rm -f tmpconf
