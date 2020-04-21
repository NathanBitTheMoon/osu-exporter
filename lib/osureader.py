class Reader:
    def __init__(self, fp):
        self.lines = fp.readlines()
        self.cursor = 0
        self.path = ""

        required_headers = ["General", "Metadata"]
        self.values = {}

        # Read all the data in the file
        while True:
            # Check if all the header information is satisfied
            satisfied = True
            for i in required_headers:
                if i not in self.values.keys():
                    satisfied = False
            
            if satisfied:
                # Exit the loop because we have all the values we need
                break

            self._read_header()
            header = self.lines[self.cursor].strip()
            header = header[1:len(header) - 1]

            if header == "General" or header == "Metadata":
                self.cursor += 1

                sub_lines = self.lines[self.cursor:self._seek_section_end()] # Get the lines contained within the section
                for line in sub_lines:
                    # Set the values for each line
                    try:
                        key_value = line.split(':')
                        key = key_value[0].strip()
                        value = ':'.join(key_value[1:]).strip()

                        if header not in self.values.keys():
                            self.values[header] = {}

                        self.values[header][key] = value
                    except ValueError as e:
                        raise ValueError(e)
            else:
                self.cursor += 1
    
    def _read_header(self):
        """ Sets the cursor to the start of the section """
        while not self.lines[self.cursor][0] == '[':
            self.cursor += 1
        
    def _seek_section_end(self):
        """ Return the line number of the end of the current section """
        sub_cursor = self.cursor + 1

        while not self.lines[sub_cursor].startswith('['):
            sub_cursor += 1
        
        return sub_cursor