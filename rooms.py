import json

class Room(object):
  def __init__(self, room_id, name):
    self.room_id = room_id
    self.name = name

class Rooms(object):
  def __init__(self, raw_rooms):
    self.by_id = {
        int(room_id, 16) : Room(room_id=int(room_id, 16), name=room_name)
        for room_id, room_name in raw_rooms.items()
        }

  @staticmethod
  def read(filename):
    return Rooms(json.load(open(filename)))
