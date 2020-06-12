"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from cdb.utils.file import read_file
import os

here = os.path.dirname(os.path.abspath(__file__))


def get_template(name, load=True):
    """Given the name of a template (a go file to use to generate the dataset
       metadata) return the template path if it exists. Otherwise, exit on
       error
    """
    # The user can provide a custom template, must have {{ updates }} to include
    if not os.path.exists(name):
        filename = os.path.join(here, name)
    else:
        filename = name

    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} does not exist.")

    # Does the user want to load it?
    if load:
        filename = read_file(filename, readlines=False)
    return filename
