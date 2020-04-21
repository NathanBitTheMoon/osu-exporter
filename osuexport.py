print("Checking that all dependencies are satisfied...")

# Check that all dependencies are installed
import lib.dependencies
l = lib.dependencies.Dependencies()
check_dependencies = l.check_dependencies()

missing = []

for k, v in zip(check_dependencies.keys(), check_dependencies.values()):
    print(f"Dependency {k}:{' not' if not v else ''} installed")
    if not v:
        # Append the missing dependency to the missing list so that it can be installed
        missing.append(k)

if len(missing) != 0:
    print("Installing missing dependencies...")

    for i in missing:
        print(f"Installing {i}...")
        l.install(i)
print("All dependencies satisfied!")

import curses, lib.gui, lib.index, lib.exporter

exporter = lib.exporter.Exporter()

std = curses.initscr()
gui = lib.gui.GUI(std)

dir_gui = lib.gui.InputDir(std)
dir_gui._draw_main()
directory = dir_gui._get_dir()
export_directory = dir_gui._get_export().decode('utf-8')

indexer = lib.index.Indexer(directory.decode('utf-8'))

def export_all(data):
    exporter.export_selections(export_directory, use_gui = True, std = std)

def update_list_for_selections(exp, view):
    for i in range(len(view.items)):
        if exp.is_selected(view.items[i].pass_item):
            view.items[i].items[0] = "*"
        else:
            view.items[i].items[0] = " "
            
def select_all(data):
    paths = [i.pass_item for i in view.items]
    exporter.select_all(paths)
    update_list_for_selections(exporter, view)

def clear_selections(data):
    exporter.clear()
    update_list_for_selections(exporter, view)

def select(data):
    exporter.toggle_selection(data)
    update_list_for_selections(exporter, view)

progress_bar = lib.gui.ProgressBar(std, "Indexing...", 0, len(indexer.subdirs) - 1)
progress_bar.y_offset += 5

view = lib.gui.ItemList(std, [
    lib.gui.ItemList.Column("S", 0.05), 
    lib.gui.ItemList.Column("Title", 0.3), 
    lib.gui.ItemList.Column("Artist", 0.3), 
    lib.gui.ItemList.Column("Creator", 0.15), 
    lib.gui.ItemList.Column("Version", 0.15)], 
    [
        lib.gui.ItemList.KeyAction(115, "Select", "s", select),
        lib.gui.ItemList.KeyAction(83, "Select All", "S", select_all),
        lib.gui.ItemList.KeyAction(67, "Clear Selections", "C", clear_selections),
        lib.gui.ItemList.KeyAction(10, "Export Selections", "ENTER", export_all)
    ])

for i in indexer.subdirs:
    indexer.index_next()
    item = list(indexer.files.values())[indexer.cursor - 1].values
    path = list(indexer.files.values())[indexer.cursor - 1].path
    view.items.append(lib.gui.ItemList.Item([
        "", 
        item["Metadata"]["Title"], 
        item["Metadata"]["Artist"], 
        item["Metadata"]["Creator"], 
        item["Metadata"]["Version"]],
        pass_item = path
        ))
    progress_bar._draw_bar(progress = indexer.cursor, subtitle = f"Indexing {indexer.subdirs[indexer.cursor - 1]}...")
    std.refresh()

try:
    while True:
        view._draw_main()
        std.refresh()

        key_code = std.getch()
        view.process_key(key_code)
except Exception as e:
    print(e.with_traceback())
finally:
    curses.endwin()