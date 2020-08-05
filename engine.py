import datetime

class Tally(object):
  def __init__(self, geography):
    self.geography = geography
    self.counts = { }
    self.total = 0

  def count(self, location, item):
    for region in self.geography.regions_by_location[location]:
      self.counts[region] = self.counts.get(region, 0)
      self.counts[region] += 1

    self.total += 1

  def probabilities(self):
    return self._compute_probabilities(self.geography)

  def _compute_probabilities(self, geography):
    probabilities = { }
    for name, value in geography.items():
      if type(value) is dict:
        probabilities[name] = ( self._prob(name), self._compute_probabilities(value) )
      else:
        children = { n : ( self._prob(n), None ) for n in value }
        probabilities[name] = ( self._prob(name), children )
    return probabilities

  def _prob(self, name):
    if self.total == 0:
      return 0
    else:
      return float(self.counts.get(name, 0)) / self.total

class Engine(object):
  def __init__(self, items, locations, geography, rooms, seeds):
    self.items = items
    self.locations = locations
    self.geography = geography
    self.rooms = rooms
    self.seeds = seeds
    self._viable_seeds = None
    self._tally = None
    self._tally_time = None
    self.current_room = None

  def tally(self):
    if self._tally:
      return self._tally

    start_time = datetime.datetime.now()
    tally = Tally(self.geography)
    for seed in self.viable_seeds():
      for location, item in seed.locations:
        self._tally_location(tally, location, item)


    self._tally = tally
    self.tally_time = datetime.datetime.now() - start_time

    return self._tally

  def _tally_location(self, tally, location, item):
    if item.good and not location.visited and not item.found:
      tally.count(location, item)

  def toggle_visited(self, name):
    locs = self.locations.by_name_or_room(name)
    if locs:
      v = not any(loc.visited for loc in locs)
      for loc in locs:
        loc.visited = v

    else:
      locs = self.geography.locations_by_region.get(name, None)

      if locs:
        v = not any(loc.visited for loc in locs)
        for loc in locs:
          loc.visited = v

      else:
        raise RuntimeError("Could not find %s" % name)

    self.mark_dirty()

  def viable_seeds(self):
    if self._viable_seeds:
      return self._viable_seeds

    viable = [ ]

    for seed in self.seeds:
      if self._viable_seed(seed):
        viable.append(seed)

    if len(viable) == 0:
      viable = self.seeds

    self._viable_seeds = viable
    return self._viable_seeds

  def _viable_seed(self, seed):
    for location, item in seed.locations:
      if item.found and item.found_in is not None and item.found_in != location.area:
        return False

    return True

  def mark_dirty(self):
    self._tally = None
    self._viable_seeds = None
