#!/usr/bin/env python3

import json
import glob
import re

if __name__ == '__main__':
  seeds = { }
  locations = json.load(open('locations.json'))
  items = json.load(open('items.json'))

  loc_names = { location['Name'] : location for location in locations }
  item_types = { item['Type'] : item for item in items }

  for filename in glob.glob('seeds/*.txt'):
    print(filename)
    locations = { }
    seed = None
    with open(filename) as f:
      for line in f:
        m = re.search(r'SEED: (\d+)', line)
        if m:
          seed = int(m.group(1))

        m = re.search(r'^\s+(.*?):\s+(\w+)\s*$', line)
        if m:
          loc_name = m.group(1)
          item_name = m.group(2)

          loc = loc_names[loc_name]
          item = item_types[item_name]

          if 'Id' in loc:
            # bosses don't have Ids
            locations[loc['Id']] = item['Code'] - 0xee00

    if seed is not None:
      seeds[seed] = locations

  with open('seeds.json', 'w') as o:
    prefix = "{\n"
    for seed, locs in sorted(seeds.items()):
      s = ','.join({ "\"%s\":%s" % (l, i) for l, i in sorted(locs.items()) })
      o.write("%s\"%d\":{%s}" % (prefix, seed, s))
      prefix = ",\n"
    o.write("}\n")
