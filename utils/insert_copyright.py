# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
import tempfile
import os

copyright = """# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
"""
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    with open(args.file) as input:
        stuff = input.readlines()
        if stuff[0] != copyright.strip().split('\n')[0] or stuff[1] != copyright.strip().split('\n')[1]:
            result = tempfile.NamedTemporaryFile('w')
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
                        print(line.strip('\n'))
            result.close()

