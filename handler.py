from importlib import import_module
import os

def load():
    commands = []
    category = []
    for root, dirs, files in os.walk("./cmds"):
        for name in dirs:
            if name != "__pycache__":
                module = import_module(f"cmds.{name}")
                init = module.init.load_m()
                temp = []
                for cmd in init:
                    temp.append(cmd)
                commands.append(temp)
                category.append(name)
    return commands, category