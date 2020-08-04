import datetime

from retroarch.network_command_socket import NetworkCommandSocket

class MemoryRegion(object):
  def __init__(self, addr, s):
    self.start = addr
    self.s = s

  @staticmethod
  def read_from(sock, addr, size):
    s = sock.read_core_ram(addr, size)
    return MemoryRegion(addr, s)

  def __getitem__(self, addr):
    return self.s[addr - self.start]

  def __len__(self):
    return len(self.s)

  def short(self, addr):
    lo = self[addr] or 0
    hi = self[addr + 1] or 0
    return lo | hi << 8

  def bignum(self, addr, size):
    result = 0
    for i in range(0, size):
      octet = self[addr + i] or 0
      result |= octet << (8 * i)
    return result

RoomAreas = {
  0x00: 'Crateria',
  0x01: 'Brinstar',
  0x02: 'Norfair',
  0x03: 'WreckedShip',
  0x04: 'Maridia',
  0x05: 'Tourian',
  0x06: 'Ceres',
  0x07: 'Debug',
}

class Autotracker(object):
  def __init__(self, engine, clock):
    self.engine = engine
    self.clock = clock

    self.sock = NetworkCommandSocket()
    self.items = 0
    self.beams = 0
    self.locations = 0

  def poll(self):
    region1 = MemoryRegion.read_from(self.sock, 0x0790, 0x1f)
    region2 = MemoryRegion.read_from(self.sock, 0x0990, 0xef)
    region3 = MemoryRegion.read_from(self.sock, 0xD800, 0x8f)
    # region4 = MemoryRegion.read_from(self.sock, 0x0F80, 0x4f)
    region5 = MemoryRegion.read_from(self.sock, 0x05B0, 0x0f)

    room_id = region1.short(0x79B)
    region_id = region1.short(0x79F)

    items = region2.short(0x9A4)
    beams = region2.short(0x9A8)

    igt_frames = region2.short(0x9DA)
    igt_seconds = region2[0x9DC]
    igt_minutes = region2[0x9DE]
    igt_hours = region2[0x9E0]
    fps = 60.0 # TODO

    # Varia randomizer RTA clock
    rta_frames = region5.short(0x5B8)
    rta_rollovers = region5.short(0x5BA)

    area = RoomAreas[region_id]
    locations = region3.bignum(0xD870, 15)

    new_items = items & ~self.items
    new_beams = beams & ~self.beams
    new_locations = locations & ~self.locations

    for item in self.item_names(new_items):      self.set_found(area, item)
    for beam in self.beam_names(new_beams):      self.set_found(area, beam)
    for loc in self.location_ids(new_locations): self.set_visited(loc)

    self.items = items
    self.beams = beams
    self.locations = locations

    self.engine.current_room = self.engine.rooms.by_id.get(room_id, None)

    if self.clock:
      self.clock.igt = datetime.timedelta(seconds=igt_hours * 3600 + igt_minutes
          * 60 + igt_seconds + igt_frames / fps)
      self.clock.rta = datetime.timedelta(seconds=(rta_frames + (rta_rollovers
        << 16)) / 60.0)

  def item_names(self, items):
    if items & 0x0001: yield 'Varia'
    if items & 0x0002: yield 'SpringBall'
    if items & 0x0004: yield 'Morph'
    if items & 0x0008: yield 'ScrewAttack'
    if items & 0x0020: yield 'Gravity'
    if items & 0x0100: yield 'HiJump'
    if items & 0x0200: yield 'SpaceJump'
    if items & 0x1000: yield 'Bomb'
    if items & 0x2000: yield 'SpeedBooster'
    if items & 0x4000: yield 'Grapple'
    if items & 0x8000: yield 'XRayScope'

  def beam_names(self, beams):
    if beams & 0x1000: yield 'Charge'
    if beams & 0x0001: yield 'Wave'
    if beams & 0x0002: yield 'Ice'
    if beams & 0x0004: yield 'Spazer'
    if beams & 0x0008: yield 'Plasma'

  def location_ids(self, locations):
    loc = 0
    while locations != 0:
      if locations & 1:
        yield loc
      locations >>= 1
      loc += 1

  def set_found(self, area, item):
    self.engine.items.by_type[item].found = True
    self.engine.items.by_type[item].found_in = area
    self.engine.mark_dirty()

  def set_visited(self, location_id):
    self.engine.locations.by_id[location_id].visited = True
    self.engine.mark_dirty()
