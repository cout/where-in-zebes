#!/usr/bin/env python3

import sys

sys.path.append('RandomMetroidSolver')

from rando.Items import ItemManager
import json

items = [
  {
    'Category': ItemManager.Items[k]['Category'],
    'Class': ItemManager.Items[k]['Class'],
    'Code': ItemManager.Items[k].get('Code', None),
    'Name': ItemManager.Items[k]['Name'],
    'Type': k,
  } for k in ItemManager.Items
] 

out = open('items.json', 'w')
json.dump(items, out)
