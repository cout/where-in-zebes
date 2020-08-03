#!/usr/bin/env python3

import argparse

from items import Items
from locations import Locations
from geography import Geography
from seeds import Seeds
from engine import Engine
from curses_ui import UI
from clock import Clock
from autotracker import Autotracker

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Zebbo Probability Engine')
  parser.add_argument('--autotrack', dest='autotrack', action='store_true', default=False)
  parser.add_argument('--clock', dest='clock', action='store_true', default=False)

  args = parser.parse_args()

  items = Items.read('items.json')
  locations = Locations.read('locations.json')
  geography = Geography.read(locations, 'geography.json')
  seeds = Seeds.read(items, locations, 'seeds.json')
  engine = Engine(items, locations, geography, seeds)

  if args.clock:
    clock = Clock()
  else:
    clock = None

  if args.autotrack:
    autotracker = Autotracker(engine, clock)
    poll = autotracker.poll
  else:
    poll = lambda: None

  UI.run(items=items, geography=geography, engine=engine, poll=poll, clock=clock)

  # print(engine.tally().probabilities())
