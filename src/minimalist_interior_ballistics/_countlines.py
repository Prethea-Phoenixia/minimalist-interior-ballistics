import os
import sys


def countlines(start, lines=0, header=True, begin_start=None) -> int:
    if header:
        print("{:>10} |{:>10} | {:<20}".format("ADDED", "TOTAL", "FILE"))
        print("{:->11}|{:->11}|{:->20}".format("", "", ""))

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            if thing.endswith(".py"):
                with open(thing, "r", encoding="utf-8") as f:
                    newlines = len(f.readlines())
                    lines += newlines

                    if begin_start is not None:
                        reldir_of_thing = "." + thing.replace(begin_start, "")
                    else:
                        reldir_of_thing = "." + thing.replace(start, "")

                    print("{:>10} |{:>10} | {:<20}".format(newlines, lines, reldir_of_thing))

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isdir(thing):
            lines = countlines(thing, lines, header=False, begin_start=start)

    return lines


if __name__ == "__main__":
    with open("linecounts.txt", "w+") as sys.stdout:
        countlines(r"./")
