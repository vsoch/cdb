#!/usr/bin/env python

"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from cdb.logger import CDB_LOG_LEVEL, CDB_LOG_LEVELS
import cdb
import argparse
import sys
import logging


def get_parser():
    parser = argparse.ArgumentParser(
        description="Container database metadata generator."
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--log_level",
        dest="log_level",
        choices=CDB_LOG_LEVELS,
        default=CDB_LOG_LEVEL,
        help="Customize logging level for containerdb.",
    )

    description = "actions for cdb"
    subparsers = parser.add_subparsers(
        help="cdb actions", title="actions", description=description, dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", help="show software version")

    # Generate a key for the interface
    generate = subparsers.add_parser(
        "generate", help="generate a template go script for container entrypoint.",
    )

    generate.add_argument(
        "path", help="Path to dataset files.", nargs="?", default=".",
    )

    # Specify output file, defaults to db.go
    generate.add_argument(
        "-o",
        "--out",
        dest="output",
        default="db.go",
        help="Output file path (must end in .go, defaults to db.go)",
    )

    generate.add_argument(
        "-t",
        "--template",
        dest="template",
        default="db.go",
        help="Template file to use in templates folder, or custom template.",
    )

    generate.add_argument(
        "--func",
        dest="function",
        default="basic",
        help="Function to extract metadata per file import path, or name in cdb.functions.",
    )

    generate.add_argument(
        "--force",
        dest="force",
        help="force generation if output file already exists.",
        default=False,
        action="store_true",
    )

    return parser


def main():
    """main entrypoint for cdb
    """

    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client 
           and exit with return code.
        """
        version = cdb.__version__

        print("\nContainer database metadata generator v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Set the logging level
    logging.basicConfig(level=getattr(logging, args.log_level))
    bot = logging.getLogger("cdb.client")
    bot.setLevel(getattr(logging, args.log_level))

    # Show the version and exit
    if args.command == "version" or args.version:
        print(cdb.__version__)
        sys.exit(0)

    # Does the user want a shell?
    if args.command == "generate":
        from .generate import main

    # Pass on to the correct parser
    return_code = 0
    # try:
    main(args=args, extra=extra)
    sys.exit(return_code)
    # except UnboundLocalError:
    #    return_code = 1

    help(return_code)


if __name__ == "__main__":
    main()
