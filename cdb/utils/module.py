"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import importlib
import sys


def import_module(name):
    """Import module will try import of a module based on a name. If import
       fails and there are no ., we expect that it could be a script in the
       present working directory and add .<script>
       Arguments:
        - name (str) : the name of the module to import
    """
    try:
        module = importlib.import_module(name)
    except:
        sys.exit(f"Unrecognizable file, directory, or module name {name}")
    return module
