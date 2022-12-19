import os
import json
import subprocess
import sys
import shutil 


IDF_PATH = os.environ.get('IDF_PATH')
BUILD_PATH = "build/"


def fix(line):
    return line.replace("-I", "-isystem") if IDF_PATH in line else line


def fix_compile_commands(filename):
    commands_file = os.path.join(filename, 'compile_commands.json')
    stored_file = os.path.join(filename, 'compile_commands_cached.json')
    shutil.copyfile(commands_file, stored_file)

    with open(commands_file) as f:
        commands = json.load(f)
    for comm in commands:
        comm["command"] = " ".join([fix(line) for line in comm["command"].split(" ")])
        comm["command"] = comm["command"].replace("-mlongcalls", "")
        comm["command"] = comm["command"].replace("-fno-tree-switch-conversion", "")
        comm["command"] = comm["command"].replace("-fstrict-volatile-bitfields", "")
    with open(commands_file, "w") as f:
        json.dump(commands, f)

    return stored_file 


def restore_compile_commands(directory, old_commands_file):
    commands_file = os.path.join(directory, 'compile_commands.json')
    os.remove(commands_file)
    os.rename(old_commands_file, commands_file)


def run_clang_tidy(commands_directory, files):
    return subprocess.run(["clang-tidy", "--config-file", ".clang-tidy", "-p", commands_directory, "-export-fixes", os.path.join(BUILD_PATH, "fixes.yml")] + files).returncode


def run_reconfigure():
    subprocess.run(["idf.py", "reconfigure"])


def main():
    if IDF_PATH is None:
        raise ValueError("IDF_PATH not found. Run '. ./export.sh'")
    
    run_reconfigure()
    old_commands_file = fix_compile_commands(BUILD_PATH)
    result = run_clang_tidy(BUILD_PATH, sys.argv[1:])
    restore_compile_commands(BUILD_PATH, old_commands_file)
    return result


if __name__ == "__main__":
    main()