import os

class Dependencies:
    def __init__(self):
        self.dependencies = [{"nt": "windows-curses", "posix": "curses"}, {"nt": "mp3-tagger", "posix": "mp3-tagger"}]

    def check_dependencies(self):
        """ Check that all required dependencies are installed """
        check = {}
        
        for i in self.dependencies:
            try:
                __import__(i[os.name].replace('-', ''))
                check[i[os.name]] = True
            except ImportError:
                check[i[os.name]] = False
        return check
    
    @staticmethod
    def install(dependency):
        """ Install a dependency using pip """
        if os.name == 'nt':
            os.system(f"py -m pip install {dependency}")
        else:
            os.system(f"pip3 install {dependency}")
    