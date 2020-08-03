import curses
import sys

class Row(object):
  def __init__(self, item, p, child, highlighted, expanded):
    self.item = item
    self.p = p
    self.child = child
    self.highlighted = highlighted
    self.expanded = expanded

  def attr(self):
    attr = 0
    if self.highlighted:
      attr |= curses.A_REVERSE
    if self.p == 0:
      attr |= curses.A_DIM
    return attr

  def text(self):
    name, path = self.item
    level = len(path)

    if self.child:
      if self.expanded:
        exp = '[-] '
      else:
        exp = '[+] '
    else:
      exp = ''

    return "%s%s%.1f%% %s\n" % ('  '*level, exp, 100*self.p, name)

class TallyRenderer(object):
  def __init__(self, window, engine):
    self.window = window
    self.engine = engine

    self.expanded = { }
    self.selected = None
    self.tally = None
    self.list = [ ]
    self.active = False
    self.did_expand_one_level = False

  def render(self, n=0):
    self.list = [ ]
    if self.tally:
      rows = self._rows(self.tally.probabilities(), ( ))
      for row in rows:
        try:
          self.window.addstr(row.text(), row.attr())
        except curses.error:
          pass
    self.window.refresh()
    self.did_expand_one_level = True

  def _rows(self, tree, path):
    rows = [ ]
    n = len(path)
    for name, (p, child) in tree.items():
      item = ( name, path )
      self.list.append(item)
      if n == 0 and not self.did_expand_one_level:
        self.expanded[item] = True
      if not self.selected:
        self.selected = item
      highlighted = self.selected == item and self.active
      expanded = self.expanded.get(item, False)
      rows.append(Row(item, p, child, highlighted, expanded))
      if child and self.expanded.get(item, None):
        rows.extend(self._rows(child, path + ( name, )))
    return rows

  def handle_input(self, s):
    if s == 'k' or s == curses.KEY_UP:
      self.up()
    elif s == 'j' or s == curses.KEY_DOWN:
      self.down()
    elif s == ' ' or s == "\n" or s == curses.KEY_ENTER:
      self.toggle_expanded()
    elif s == '+':
      self.expand()
    elif s == '-':
      self.collapse()
    elif s == 'x':
      self.toggle_marked()

  def toggle_expanded(self):
    if self.expanded.get(self.selected, None):
      self.collapse()
    else:
      self.expand()

  def expand(self):
    if self.selected:
      self.expanded[self.selected] = True

  def collapse(self):
    if self.selected:
      self.expanded[self.selected] = False

  def up(self):
    idx = self.list.index(self.selected)
    new = self.list[idx-1]
    if new:
      self.selected = new

  def down(self):
    idx = self.list.index(self.selected)
    new = self.list[(idx+1) % len(self.list)]
    if new:
      self.selected = new

  def toggle_marked(self):
    self.engine.toggle_visited(self.selected[0])

class ItemsRenderer(object):
  def __init__(self, window, items, engine):
    self.window = window
    self.items = items
    self.engine = engine

    self.list = [ ]
    self.selected = None
    self.active = False

  def render(self):
    self.list = [ ]
    for item in self.items:
      if item.good:
        self.list.append(item)
        if not self.selected:
          self.selected = item
        if item.found:
          sel = "[%s]" % item.found_in[0]
        else:
          sel = '[ ]'
        attr = 0
        if self.selected == item and self.active:
          attr |= curses.A_REVERSE
        if item.found:
          attr |= curses.A_DIM
        self.window.addstr("%s %s\n" % (sel, item.type), attr)

  def handle_input(self, s):
    if s == 'k' or s == curses.KEY_UP:
      self.up()
    elif s == 'j' or s == curses.KEY_DOWN:
      self.down()
    elif s == ' ' or s == "\n" or s == curses.KEY_ENTER:
      self.cycle_found()
    elif s == 'C' or s == 'c':
      self.toggle_found('Crateria')
    elif s == 'B' or s == 'b':
      self.toggle_found('Brinstar')
    elif s == 'N' or s == 'n':
      self.toggle_found('Norfair')
    elif s == 'M' or s == 'm':
      self.toggle_found('Maridia')
    elif s == 'W' or s == 'w':
      self.toggle_found('WreckedShip')
    elif s == 'x':
      self.set_unfound()

  def toggle_found(self, where):
    if not self.selected:
      return
    if self.selected.found:
      self.set_unfound()
    else:
      self.set_found(where)

  def cycle_found(self):
    if not self.selected:
      return
    if self.selected.found_in == 'Crateria':
      self.selected.found = True
      self.selected.found_in = 'Brinstar'
    elif self.selected.found_in == 'Brinstar':
      self.selected.found = True
      self.selected.found_in = 'Norfair'
    elif self.selected.found_in == 'Norfair':
      self.selected.found = True
      self.selected.found_in = 'Maridia'
    elif self.selected.found_in == 'Maridia':
      self.selected.found = True
      self.selected.found_in = 'WreckedShip'
    elif self.selected.found_in == 'WreckedShip':
      self.selected.found = False
      self.selected.found_in = None
    else:
      self.selected.found = True
      self.selected.found_in = 'Crateria'
    self.engine.mark_dirty()

  def set_found(self, where):
    if not self.selected:
      return
    self.selected.found = True
    self.selected.found_in = where
    self.engine.mark_dirty()

  def set_unfound(self):
    if not self.selected:
      return
    self.selected.found = False
    self.selected.found_in = None
    self.engine.mark_dirty()

  def up(self):
    idx = self.list.index(self.selected)
    new = self.list[idx-1]
    if new:
      self.selected = new

  def down(self):
    idx = self.list.index(self.selected)
    new = self.list[(idx+1) % len(self.list)]
    if new:
      self.selected = new

class UI(object):
  def __init__(self, screen, items, geography, engine, poll):
    self.screen = screen
    self.items = items
    self.geography = geography
    self.engine = engine
    self.poll = poll

    self.window = curses.newwin(0, 0, 0, 2)
    self.window.clear()
    self.window.keypad(True)

    self.iwindow = curses.newwin(0, 0, 0, 42)
    self.iwindow.clear()

    self.tally_renderer = TallyRenderer(self.window, self.engine)
    self.items_renderer = ItemsRenderer(self.iwindow, self.items, self.engine)

    self.active_renderer = None
    self.set_active(self.tally_renderer)

  @staticmethod
  def run(*args, **kwargs):
    screen = curses.initscr()

    try:
      curses.start_color()
      curses.use_default_colors()
      curses.curs_set(0)
      curses.noecho()

      ui = UI(*args, screen=screen, **kwargs)
      ui._run()

    finally:
      curses.endwin()

  def _run(self):
    while True:
      self.poll()
      self.tally()
      self.render()
      self.process_input()

  def tally(self):
    self.tally_renderer.tally = self.engine.tally()

  def render(self):
    self.window.move(0, 0)
    self.window.clear() # TODO: flicker

    self.tally_renderer.render()
    # self.window.addstr("\nTime to tally: %s\n" % self.engine.tally_time)
    self.window.refresh()

    self.iwindow.move(0, 0)
    self.iwindow.clear()
    self.items_renderer.render()
    self.iwindow.refresh()

  def process_input(self):
    self.window.timeout(1000)
    ch = self.window.getch()
    if ch >= 32 and ch < 128:
      s = chr(ch)
    else:
      s = ch
    self.handle_input(s)

  def handle_input(self, s):
    if s == 'q':
      self.quit()
    elif s == 'h' or s == curses.KEY_LEFT:
      self.left()
    elif s == 'l' or s == curses.KEY_RIGHT:
      self.right()
    else:
      self.active_renderer.handle_input(s)

  def set_active(self, renderer):
    if self.active_renderer:
      self.active_renderer.active = False
    self.active_renderer = renderer
    self.active_renderer.active = True

  def left(self):
    self.right()

  def right(self):
    if self.active_renderer is self.tally_renderer:
      self.set_active(self.items_renderer)
    else:
      self.set_active(self.tally_renderer)

  def quit(self):
    sys.exit()
