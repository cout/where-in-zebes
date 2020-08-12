import json

def good_item(item):
  return item.category == 'Progression' or item.type == 'Charge' or item.type == 'ScrewAttack' or item.type == 'Wave'

class Item(object):
  def __init__(self, d):
    self.category = d['Category']
    self.code = d['Code']
    self.type = d['Type']
    self.item_class = d['Class']
    self.good = good_item(self)
    self.found = None
    self.found_in = None

class Items(object):
  def __init__(self, raw_items):
    self.items = [ Item(d) for d in raw_items ]

    self.by_code = { item.code : item for item in self.items}
    self.by_type = { item.type : item for item in self.items}

  @staticmethod
  def read(filename):
    return Items(json.load(open(filename)))

  def __iter__(self):
    return iter(self.items)
