from mp3_tagger import MP3File, VERSION_2, VERSION_1
import lib.osureader, lib.gui, lib.index
import shutil, os

class Exporter:
    
    def __init__(self):
        self.selections = []
    
    def is_selected(self, path):
        return path in self.selections
    
    def toggle_selection(self, path):
        if path in self.selections:
            self.selections.remove(path)
        else:
            self.selections.append(path)
    
    def select_all(self, data):
        for i in data:
            if i not in self.selections:
                self.selections.append(i)
    
    def clear(self):
        self.selections = []
    
    @staticmethod
    def export(path, export_path, version = VERSION_2):
        if os.name == "nt":
            reader = lib.osureader.Reader(open(lib.index.Indexer._windows_path(path), encoding="utf-8"))
        else:
            reader = lib.osureader.Reader(open(path, encoding="utf-8"))

        path = path.split('/')
        path = '/'.join(path[::-1][1:][::-1])

        try:
            beatmap_id = str(reader.values["Metadata"]["BeatmapID"])
        except KeyError:
            beatmap_id = ""

        filename = reader.values["Metadata"]["Artist"] + "-" + reader.values["Metadata"]["Title"] + beatmap_id + ".mp3"

        shutil.copy(path + "/" + reader.values["General"]["AudioFilename"], export_path + "/" + filename)
        export_path = export_path + "/" + filename

        working_file = MP3File(export_path)
        
        working_file.artist = reader.values["Metadata"]["Artist"]
        working_file.song = reader.values["Metadata"]["Title"]

        working_file.save()

    def export_selections(self, export_path, use_gui = False, std = None):
        """ Export all of your song selections and tag them """
        if use_gui:
            progress_bar = lib.gui.ProgressBar(std, "Exporting...", 0, len(self.selections))
            progress_bar._draw_bar()

        for export in self.selections:
            Exporter.export(export, export_path)
            if use_gui:
                progress_bar.progress += 1
                progress_bar._draw_bar()
