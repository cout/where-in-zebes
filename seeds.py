import json

class Seed(object):
  def __init__(self, items, item_locations, seed, raw_locations):
    self.seed = seed

    self.locations = [ ]
    for loc_id, item_id in raw_locations.items():
      loc_id = int(loc_id)
      item_code = item_id + 0xee00
      location = item_locations.by_id[loc_id]
      item = items.by_code[item_code]
      self.locations.append([location, item])

class Seeds(object):
  def __init__(self, items, locations, raw_seeds):
    self.items = items
    self.locations = locations
    self.seeds = [ Seed(items, locations, seed, raw_seeds[seed]) for seed in raw_seeds ]

  @staticmethod
  def read(items, locations, filename):
    return Seeds(items, locations, json.load(open(filename)))

  def __iter__(self):
    return iter(self.seeds)
