#!/bin/bash

# https://xen.garden/2020/04/29/smrat-data.html

param="./RandomMetroidSolver/standard_presets/SMRAT2020.json"
randoPreset="./RandomMetroidSolver/rando_presets/SMRAT2020.json"

while :
do
  seed=($RANDOM % 1000000)
  filename="seeds/$seed.txt"
  if [ ! -f "${filename}" ]
  then
    ./RandomMetroidSolver/randomizer.py \
        --param "${param}" --randoPreset "${randoPreset}" \
        --seed $seed --output /dev/null --debug --runtime 90 \
        | grep -v "DEBUG\|Apply\|DIAG" > "${filename}"
    if [ ! -s "${filename}" ]
    then
      rm "${filename}"
      break
    fi
    echo "generated $seed"
  fi
done
