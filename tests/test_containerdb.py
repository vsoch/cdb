#!/usr/bin/env python
"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os
import pytest

here = os.path.dirname(os.path.abspath(__file__))


def test_generation(tmp_path):
    """test generation with default settings
    """
    from cdb.main import ContainerDatabase

    path = os.path.join(here, "data")

    # Fail if path doesn't exist
    with pytest.raises(FileNotFoundError):
        db = ContainerDatabase(path="_data")

    # Create a Container database
    db = ContainerDatabase(path=path)

    # File generator should be created on demand
    assert len(list(db.files)) == 2
    assert len(list(db.files)) == 2

    # No output means we return a string (default template db.go, func=basic
    script = db.generate()
    output_file = os.path.join(str(tmp_path), "db.go")
    script = db.generate(output=output_file)
    assert os.path.exists(script)

    # Shouldn't overwrite if force is false
    with pytest.raises(SystemExit):
        script = db.generate(output=output_file)

    # Should work given force is True
    script = db.generate(output=output_file, force=True)

    # Should not work if function doesn't exist
    with pytest.raises(RuntimeError):
        script = db.generate(func="doesnotexist")

    # Should work with custom function
    def return_name(filename):
        return filename

    script = db.generate(func=return_name)
