#!/usr/bin/env python3

import sys

sys.path.append('RandomMetroidSolver')

from graph_locations import locations
from smboolmanager import SMBoolManager
import json
import copy

def convert(loc, sm):
  d = { }
  for key in loc:
    value = loc[key]
    if type(value) is dict:
      value = convert(value, sm)
    elif callable(value):
      value = None # TODO
    d[key] = value
  return d

out = open('locations.json', 'w')
sm = SMBoolManager()
json.dump([ convert(loc, sm) for loc in locations ], out)
