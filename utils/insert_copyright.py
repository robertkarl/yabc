# Copyright (c) Robert Karl. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
import argparse
import os
import tempfile

copyright = """# Copyright (c) Robert Karl. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    with open(args.file) as input:
        stuff = input.readlines()
        valid = True
        for i in range(len(copyright.strip().split("\n"))):
            if stuff[i].strip("\n") != copyright.strip("\n").split("\n")[i]:
                valid = False
        if not valid:
            result = tempfile.NamedTemporaryFile("w")
            result.file.writelines(copyright)
            result.file.writelines(stuff)
            result.file.flush()

            if args.in_place:
                result.file.close()
                os.rename(result.name, args.file)
            else:
                result.file.close()
                with open(result.name) as f:
                    for line in f.readlines():
                        print(line.strip("\n"))
            result.close()
