"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


from cdb.utils.file import recursive_find, write_file
from cdb.utils.module import import_module
from cdb.templates import get_template

from jinja2 import Template

import json
import logging
import os
import sys
import types

bot = logging.getLogger("cdb.main")


class ContainerDatabase:
    """A container database metadata generator will take some input folder
       of files, and recursively run a user-provided or cdb-provided function
       to extract metadata for each one. If no custom function is provided,
       we provide basic metadata about file versions.
    """

    def __init__(self, path, pattern="*"):
        """extract metadata for some recursive set of data objects
        """
        self.get_files(path, pattern)
        self.path = path
        self.pattern = pattern
        self.metadata = {}

    def get_files(self, path, pattern="*"):
        """return files, given update path and pattern
        """
        self.path = path
        self.pattern = pattern
        return self.files

    @property
    def files(self):
        """Given a path, check that it exists, and then create an iterator
           to go over files.
        """
        if self.path in [".", None]:
            self.path = os.getcwd()
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"{self.path} does not exist.")
        return recursive_find(self.path, pattern=self.pattern)

    def generate(self, output=None, template="db.go", force=False, func=None):
        """Given an output file name and a template, iterate
           through files and generate the in-memory database golang file to
           compile into a container.
        """
        bot.debug(f"Loading template {template}")
        template = get_template(template)

        # If the output file exists and force is false, exit early
        if not force and output and os.path.exists(output):
            sys.exit(f"{output} exists, use --force to overwrite.")

        # Retrieve the requested function
        func = self.get_function(func)

        # For each filename, extract metadata and unique keys
        keys = set()
        for filename in self.files:
            result = func(filename)
            if isinstance(result, dict):
                [keys.add(x) for x in result]
                result = json.dumps(result)
            self.metadata[filename] = result

        # Populate the template
        template = Template(template)
        script = template.render(updates=self.metadata, indices=keys)
        print(script)

        if output is not None:
            return write_file(output, script)
        return script

    def export_dockerfile(self, name="Dockerfile"):
        """export a Dockerfile that will perform a multistage build to
        """
        pass

    def get_function(self, funcname=None):
        """Given a function name, return it. Exit on error if not found.
        """
        # Default to cdb.functions.basic
        funcname = funcname or "basic"

        # If it's already a function, return it
        if isinstance(funcname, types.FunctionType):
            return funcname

        # Otherwise, try to import it
        try:
            module = import_module("cdb.functions")
            func = getattr(module, funcname)

        # Fallback to support for custom modules
        except:
            try:
                modulename = funcname.split(".")[0]
                module = import_module(modulename)
                for piece in modulename.split(".")[1:]:
                    module = getattr(module, piece)
                func = module
            except:
                raise RuntimeError(f"{funcname} cannot be imported.")

        return func
