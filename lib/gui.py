import curses, _curses, textwrap

class GUI:
    def __init__(self, std):
        pass
        self.std = std

        curses.start_color()
        curses.cbreak()
        self.std.keypad(True)

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW) # Lable
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) # Incorrectly typed text
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE) # Cursor text
    
    @staticmethod
    def _pad(text, width, pad_char = ' '):
        while len(text) < width - 1:
            text += pad_char
        text += pad_char
        return text
    
    @staticmethod
    def _trunc(text, width, pad = False, ending = '...'):
        cursor = len(text) - 1
        if cursor > width:
            # Truncate text
            cursor = width - len(ending)
            text = text[:cursor] + ending
            if pad:
                text += " "*(width - cursor + 1)
        else:
            if pad:
                text += " "*((width - cursor) + len(ending))
        return text
    
    @staticmethod
    def _centre(text, width):
        return (width - len(text)) / 2

class ItemList:
    class Column:
        def __init__(self, title, length_percentage):
            self.title = title
            self.length = length_percentage
    
    class Item:
        def __init__(self, items, pass_item):
            self.items = items
            self.pass_item = pass_item
    
    class KeyAction:
        def __init__(self, key_code, name, key_name, function):
            self.key_code = key_code
            self.name = name
            self.function = function
            self.key_name = key_name

    def __init__(self, std, columns, key_actions):
        self.columns = columns
        self.items = []
        self.cursor = 0
        self.scroll = 0
        self.key_actions = key_actions

        self.std = std
        self.y, self.x = self.std.getmaxyx()

        self.scroll_buffer = 3

        self.combo_string = ""
        for i in self.key_actions:
            self.combo_string += f"[{i.key_name}] {i.name} "
        
        self.combo_string = textwrap.wrap(self.combo_string, self.x - 2)
    
    def _draw_main(self):
        self.std.clear()

        # Draw the column header
        column_text = ""
        for i in self.columns:
            length = int((self.x - 2) * i.length) - 1
            text = GUI._trunc(i.title, length, pad = True)
            column_text += text + "|"
        
        self.std.addstr(0, 0, column_text[::-1][2:][::-1], curses.color_pair(1))

        # Draw the items
        draw_area = self.y - 2 - len(self.combo_string)
        item_range = self.items[self.scroll:self.scroll+draw_area]

        for item, row in zip(item_range, range(len(item_range))):
            add_text = ""

            for row_item, column_length in zip(item.items, self.columns):
                length = int((self.x - 2) * column_length.length) - 1
                text = GUI._trunc(row_item, length, pad = True)
                add_text += text + "|"
            
            if self.scroll + row == self.cursor:
                self.std.addstr(1 + row, 0, add_text[::-1][2:][::-1], curses.color_pair(2))
            else:
                self.std.addstr(1 + row, 0, add_text[::-1][2:][::-1])
        
        self.std.addstr(draw_area + 1, 0, '\n'.join(self.combo_string))
        self.std.refresh()
    
    def process_key(self, key_code):
        draw_area = self.y - 2 - len(self.combo_string)
        if key_code == 258:
            # Down
            if self.cursor + 1 < len(self.items):
                self.cursor += 1
        if key_code == 259:
            # Up
            if self.cursor - 1 >= 0:
                self.cursor -= 1
        
        if key_code == 360:
            # End
            self.cursor = len(self.items) - 1
            self.scroll = self.cursor - draw_area + self.scroll_buffer
        
        if key_code == 262:
            # Home
            self.cursor = 0
            self.scroll = 0
        
        if key_code == 339:
            # Page up
            if self.cursor - draw_area >= 0:
                self.cursor -= draw_area
                self.scoll = self.cursor + self.scroll_buffer - draw_area
        
        if key_code == 27:
            # Escape
            raise KeyboardInterrupt()
        
        # Check function keys
        for check_key in self.key_actions:
            if key_code == check_key.key_code:
                check_key.function(self.items[self.cursor].pass_item)

        if self.cursor > (draw_area + self.scroll) - self.scroll_buffer and self.cursor + 1 <= len(self.items) - 1:
            self.scroll += 1
        elif self.cursor < self.scroll + self.scroll_buffer and (self.scroll - 1) >= 0:
            self.scroll -= 1
        

class InputDir:
    def __init__(self, std):
        self.std = std
        self.y, self.x = self.std.getmaxyx()

        curses.start_color()

    def _draw_main(self):
        self.std.clear()

        # Draw header
        self.std.addstr(0, 0, GUI._pad("Enter osu! directory:", self.x), curses.color_pair(1))
        self.std.addstr(2, 0, "Directory:", curses.color_pair(2))
        self.std.addstr(3, 0, "Export path:", curses.color_pair(2))

        self.std.refresh()
    
    def _get_dir(self):
        return self.std.getstr(2, 10)
    
    def _get_export(self):
        return self.std.getstr(3, 12)

class ProgressBar:
    def __init__(self, std, header, min, max):
        self.std = std
        self.std.clear()
        self.y, self.x = self.std.getmaxyx()

        self.header = header

        self.bar_start = int(self.x * 0.05)
        self.bar_end = int(self.x * 0.95)
    
        self.min = min
        self.max = max
        self.progress = 0

        self.y_offset = 0
    
    def _draw_bar(self, progress = None, subtitle = '', use_subtitle = False):
        if progress == None:
            progress = self.progress
        self.std.clear()

        percentage = (progress - self.min) / self.max
        bar_pixels = int((self.bar_end - self.bar_start) * percentage)

        UPPER_LEFT = "╔"
        LOWER_LEFT = "╚"
        UPPER_RIGHT = "╗"
        LOWER_RIGHT = "╝"
        UPPER = "═"
        SIDE = "║"

        self.std.addstr(0 + self.y_offset, 0, UPPER_LEFT + UPPER*(self.x-2) + UPPER_RIGHT)
        self.std.addstr(0 + self.y_offset, 1, GUI._trunc(self.header, int(self.x / 2)))
        self.std.addstr(1 + self.y_offset, 0, f"{SIDE}\n"*4)
        self.std.addstr(1 + self.y_offset, self.x - 1, f"{SIDE}")
        self.std.addstr(2 + self.y_offset, self.x - 1, f"{SIDE}")
        self.std.addstr(3 + self.y_offset, self.x - 1, f"{SIDE}")
        self.std.addstr(4 + self.y_offset, self.x - 1, f"{SIDE}")
        self.std.addstr(5 + self.y_offset, 0, LOWER_LEFT + UPPER*(self.x-2) + LOWER_RIGHT)

        # Draw bar border
        self.std.addstr(1 + self.y_offset, self.bar_start - 2, UPPER_LEFT + UPPER*((self.bar_end - self.bar_start) + 2) + UPPER_RIGHT)
        self.std.addstr(3 + self.y_offset, self.bar_start - 2, LOWER_LEFT + UPPER*((self.bar_end - self.bar_start) + 2) + LOWER_RIGHT)
        self.std.addstr(2 + self.y_offset, self.bar_start - 2, SIDE)
        self.std.addstr(2 + self.y_offset, self.bar_end + 1, SIDE)

        # Draw bar
        self.std.addstr(2 + self.y_offset, self.bar_start, ' '*bar_pixels, curses.color_pair(4))

        # Draw subtitle
        self.std.addstr(4 + self.y_offset, self.bar_start - 2, subtitle)