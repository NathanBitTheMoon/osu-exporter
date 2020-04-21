import os, lib.osureader, glob

class Indexer:
    def __init__(self, path):
        self.files = {}
        self.mp3s = []
        self.path = path
        self.cursor = 0
        self.subdirs = os.listdir(path + "/Songs/".replace("/", "\\" if os.name == "nt" else "/"))

    def index_next(self):
        i = self.path + "/Songs/" + self.subdirs[self.cursor] + "/"
        files = [e for e in os.listdir(i) if e.endswith('.osu')]

        for f in files:
            path = "/" + i + "/" + f
            if os.name == "nt":
                path = path.replace('/', "\\")
            try:
                item = lib.osureader.Reader(open(Indexer._windows_path(path), 'r', encoding="utf-8"))
            except:
                continue
            item.path = path
            if i + item.values["General"]["AudioFilename"] not in self.mp3s:
                self.files[path] = item
                self.mp3s.append(i + item.values["General"]["AudioFilename"])
    
        self.cursor += 1
    
    @staticmethod
    def _windows_path(path):
        path = path.split('\\')
        # Remove all empty items from the list
        output_list = []
        for i in path:
            if i.strip() != "":
                output_list.append(i)
        
        return '\\'.join(output_list)