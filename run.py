import subprocess as s
import shlex as sh


dir = ""  # top pull directory
err = ""  # directory for erroneous images
start = " --start 25"  # option param; add to end of the command string to start at the given location in the image pool

s.call(sh.split("python sort.py --directory " + dir + " --errors " + err + " --keys key_mappings.json"))

# 3 and 4 for navigation dataset
# ` for exiting
