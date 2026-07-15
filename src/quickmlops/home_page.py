from jinja2 import Environment, FileSystemLoader

class HomePage:
    template_dir = Environment(loader=FileSystemLoader("templates"))
    
    def __init__(self):
        pass

