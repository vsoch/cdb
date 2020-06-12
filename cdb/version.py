"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

__version__ = "0.0.0"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsochat@stanford.edu"
NAME = "cdb"
PACKAGE_URL = "https://github.com/singularityhub/cdb"
KEYWORDS = "containers, metadata, database"
DESCRIPTION = "container database (cdb) metadata generation tool."
LICENSE = "LICENSE"

################################################################################
# Global requirements


INSTALL_REQUIRES = (("Jinja2", {"min_version": None}),)
TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)
SCHEMAORG_REQUIRES = (("schemaorg", {"min_version": None}),)

ALL_REQUIRES = INSTALL_REQUIRES + SCHEMAORG_REQUIRES
