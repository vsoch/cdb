"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os
from cdb.utils.file import get_file_hash


def basic(filename):
    """Given a filename, return a dictionary with basic metadata about it
    """
    st = os.stat(filename)
    return {"size": st.st_size, "sha256": get_file_hash(filename)}
