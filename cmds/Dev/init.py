import os
from importlib import import_module

def load_m():
    hand = []
    for root, dirs, files in os.walk("./cmds/Dev"):
        for name in files:
            if name != "__init__.py" and (name != "init.py" and name.endswith('.py')):
                try:
                    module = import_module(f"cmds.Dev.{name[:-3]}")
                    for cmd in module.init():
                        hand.append(cmd)
                except:
                    pass
                
    return hand
                
            