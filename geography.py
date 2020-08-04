import json

class Geography(object):
  def __init__(self, locations, raw_geography):
    self.locations = locations
    self.geography = Geography.create_geography(raw_geography)

    self.regions_by_location = { }
    self.regions_by_room_name = { }
    self.locations_by_region = { }
    self.create_lookup(raw_geography)

  @staticmethod
  def read(locations, filename):
    return Geography(locations, json.load(open(filename)))

  def __iter__(self):
    return iter(self.geography)

  def items(self):
    return self.geography.items()

  @staticmethod
  def create_geography(raw_geography):
    geography = { }
    for key, value in raw_geography.items():
      if type(value) is dict:
        geography[key] = Geography.create_geography(value)
      else:
        geography[key] = value
    return geography

  def create_lookup(self, d, regions=[]):
    for key, value in d.items():
      subregions = regions + [key]
      if type(value) is dict:
        self.create_lookup(value, subregions)
      else:
        for name in value:
          locs = self.locations.by_name_or_room(name)
          if locs:
            for loc in locs:
              self.regions_by_location[loc] = subregions + [name]
              self.regions_by_room_name[loc.room] = subregions + [name]
            for sr in subregions:
              self.locations_by_region[sr] = self.locations_by_region.get(sr, [ ])
              self.locations_by_region[sr].extend(locs)
