import importlib
import os

def load(name):
    commands = []
    module = importlib.reload(f"cmds")
    module2 = importlib.import_module(f"cmds.{name}")
    init = module2.init.load_m()
    for cmd in init:
        commands.append(cmd)
    return commands, name