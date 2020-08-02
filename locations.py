import json

class Location(object):
  def __init__(self, d):
    self.id = d.get('Id', None) # bosses do not have Ids
    self.room = d['Room']
    self.name = d['Name']
    self.area = d['Area']
    self.visited = False

class Locations(object):
  def __init__(self, raw_locations):
    self.locations = [ Location(loc) for loc in raw_locations ]

    self.by_id = { loc.id : loc for loc in self.locations }
    self.by_name = { loc.name : loc for loc in self.locations }

    self.by_room = { }
    for loc in self.locations:
      self.by_room[loc.room] = self.by_room.get(loc.room, [ ])
      self.by_room[loc.room].append(loc)

  @staticmethod
  def read(filename):
    return Locations(json.load(open(filename)))

  def by_name_or_room(self, name_or_room):
    loc = self.by_name.get(name_or_room, None)
    if loc:
      return [ loc ]

    locs = self.by_room.get(name_or_room, None)
    if locs:
      return locs

    return None
