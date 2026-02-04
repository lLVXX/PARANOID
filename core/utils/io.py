#core/utils/io.py

def clear():
    import os
    os.system("clear" if os.name == "posix" else "cls")
