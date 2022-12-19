import os
import json
import subprocess
import sys
import shutil 


IDF_PATH = os.environ.get('IDF_PATH')
BUILD_PATH = "build/compile_commands.json"


def fix(line):
    return line.replace("-I", "-isystem") if IDF_PATH in line else line


def fix_compile_commands(filename):
    clang_commands_file = os.path.join(os.path.dirname(filename), 'clang-tidy-commands.json')
    shutil.copyfile(filename, clang_commands_file)

    with open(clang_commands_file) as f:
        commands = json.load(f)
    for comm in commands:
        comm["command"] = " ".join([fix(line) for line in comm["command"].split(" ")])
        comm["command"] = comm["command"].replace("-mlongcalls", "")
        comm["command"] = comm["command"].replace("-fno-tree-switch-conversion", "")
        comm["command"] = comm["command"].replace("-fstrict-volatile-bitfields", "")
    with open(clang_commands_file, "w") as f:
        json.dump(commands, f)

    return clang_commands_file    


def run_clang_tidy(commands_file, files):
    return subprocess.run(["clang-tidy", "--config-file", ".clang-tidy", "-p", commands_file, "-fix"] + files).returncode


def run_reconfigure():
    subprocess.run(["idf.py", "reconfigure"])


def main():
    if IDF_PATH is None:
        raise ValueError("IDF_PATH not found. Run '. ./export.sh'")
    
    run_reconfigure()
    commands_file = fix_compile_commands(BUILD_PATH)
    return run_clang_tidy(commands_file, sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())