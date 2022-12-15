import os
import json
import subprocess
import sys


IDF_PATH = os.environ.get('IDF_PATH')
BUILD_PATH = "build/compile_commands.json"


def fix(line):
    return line.replace("-I", "-isystem") if IDF_PATH in line else line


def fix_compile_commands(filename):
    with open(filename) as f:
        commands = json.load(f)
    for comm in commands:
        comm["command"] = " ".join([fix(line) for line in comm["command"].split(" ")])
        comm["command"] = comm["command"].replace("-mlongcalls", "")
        comm["command"] = comm["command"].replace("-fno-tree-switch-conversion", "")
        comm["command"] = comm["command"].replace("-fstrict-volatile-bitfields", "")
    with open(filename, "w") as f:
        json.dump(commands, f)


def run_clang_tidy(file):
    subprocess.run(["clang-tidy", "--config-file", ".clang-tidy", "-p", "build/compile_commands.json", "-fix"] + file)


def run_reconfigure():
    subprocess.run(["idf.py", "reconfigure"])


def main():
    if IDF_PATH is None:
        raise ValueError("IDF_PATH not found. Run '. ./export.sh'")
    
    run_reconfigure()
    fix_compile_commands(BUILD_PATH)
    run_clang_tidy(sys.argv[1:])


if __name__ == "__main__":
    main()