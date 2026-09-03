#!/usr/bin/env python
#
# Copyright © 2026 Appning Lda.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Guards the README's statement of Appning oneTimeProducts support.

This library ships Google's unmodified Android Publisher discovery document and
points the generic REST client at an Appning endpoint. The document therefore
advertises operations that Appning does not implement. README.md states which
ones work.

That statement is written by hand, so it can drift from the document it
describes. These tests remove the drift: the README and the shipped discovery
document must agree, or the suite fails and names the difference.

See PAY-1888.
"""

from __future__ import absolute_import

import json
import os
import re
import unittest

from googleapiclient.discovery_cache import get_static_doc

# Every operation the bundled discovery document exposes under
# monetization.onetimeproducts, as dotted paths relative to that resource.
#
# Generated from the shipped document, not written by hand. To regenerate,
# run sorted(_discovery_operations()) below and paste the result.
EXPECTED_OPERATIONS = frozenset(
    {
        "batchDelete",
        "batchGet",
        "batchUpdate",
        "delete",
        "get",
        "list",
        "patch",
        "purchaseOptions.batchDelete",
        "purchaseOptions.batchUpdateStates",
        "purchaseOptions.offers.activate",
        "purchaseOptions.offers.batchDelete",
        "purchaseOptions.offers.batchGet",
        "purchaseOptions.offers.batchUpdate",
        "purchaseOptions.offers.batchUpdateStates",
        "purchaseOptions.offers.cancel",
        "purchaseOptions.offers.deactivate",
        "purchaseOptions.offers.list",
    }
)

# The only operation Appning implements. Verified against the server routing
# and handlers; see PAY-1888 for the evidence. Appning serves one path,
# "oneTimeProducts:batchUpdate". Only POST does work there: the GET, PUT and
# DELETE handlers are legacy-parity stubs that return 200 and change nothing.
SUPPORTED_OPERATIONS = frozenset({"batchUpdate"})

README_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md"
)

# The README compatibility table lives between these markers so that this test
# can find it without depending on surrounding prose.
TABLE_BEGIN = "<!-- BEGIN onetimeproducts-compat -->"
TABLE_END = "<!-- END onetimeproducts-compat -->"


def _discovery_operations():
    """Return every operation under monetization.onetimeproducts.

    Loads the document through the library's own static-discovery loader rather
    than by opening a path, so that a packaging change which stops shipping the
    document also fails this test.

    Returns:
      set of str, dotted operation paths relative to the onetimeproducts
      resource, e.g. "batchUpdate", "purchaseOptions.offers.list".
    """
    document = json.loads(get_static_doc("androidpublisher", "v3"))
    resource = document["resources"]["monetization"]["resources"]["onetimeproducts"]

    def walk(node, prefix):
        found = set()
        for name in node.get("methods", {}):
            found.add("%s.%s" % (prefix, name) if prefix else name)
        for name, child in node.get("resources", {}).items():
            found |= walk(child, "%s.%s" % (prefix, name) if prefix else name)
        return found

    return walk(resource, "")


def _readme_table_rows():
    """Return the data rows of the README compatibility table.

    Returns:
      list of list of str, one list of cell values per data row.

    Raises:
      AssertionError: if either marker is missing. Failing loudly matters: if a
        future edit strips the markers, this test must not quietly pass on an
        empty table.
    """
    with open(README_PATH, encoding="utf-8") as f:
        readme = f.read()

    assert TABLE_BEGIN in readme, (
        "Marker %s is missing from README.md. The compatibility table can no "
        "longer be located, so it cannot be checked against the discovery "
        "document. Restore the marker." % TABLE_BEGIN
    )
    assert TABLE_END in readme, (
        "Marker %s is missing from README.md. The compatibility table can no "
        "longer be located, so it cannot be checked against the discovery "
        "document. Restore the marker." % TABLE_END
    )

    block = readme.split(TABLE_BEGIN, 1)[1].split(TABLE_END, 1)[0]

    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        # Skip the header row and the |---|---| separator.
        if set("".join(cells)) <= set("-: "):
            continue
        if cells and cells[0].lower() == "operation":
            continue
        rows.append(cells)

    assert rows, (
        "No data rows were found between the compatibility markers in "
        "README.md. The table is empty or its format changed."
    )
    return rows


def _readme_operations():
    """Return the operation named in each README compatibility row."""
    operations = set()
    for cells in _readme_table_rows():
        match = re.search(r"`([A-Za-z0-9_.]+)`", cells[0])
        assert match, (
            "Could not read an operation name from README compatibility row "
            "%r. The first cell must contain the dotted operation name in "
            "backticks, e.g. `purchaseOptions.offers.list`." % (cells,)
        )
        name = match.group(1)
        # Set comparison alone would hide a repeated row, and two rows for one
        # operation can carry two different support claims.
        assert name not in operations, (
            "Operation `%s` appears more than once in the README compatibility "
            "table. Each operation must have exactly one row." % name
        )
        operations.add(name)
    return operations


class TestDiscoveryDocumentSurface(unittest.TestCase):
    """The shipped discovery document must expose the operations we expect."""

    def test_discovery_document_operation_set_is_unchanged(self):
        actual = _discovery_operations()

        added = sorted(actual - EXPECTED_OPERATIONS)
        removed = sorted(EXPECTED_OPERATIONS - actual)

        self.assertEqual(
            actual,
            set(EXPECTED_OPERATIONS),
            "The bundled androidpublisher.v3 discovery document no longer "
            "matches EXPECTED_OPERATIONS.\n"
            "  Added upstream (now exposed, undocumented in README): %s\n"
            "  Removed upstream (documented in README, no longer exposed): %s\n"
            "Update EXPECTED_OPERATIONS and the README compatibility table "
            "together, and confirm the support status of anything new against "
            "the server before calling it supported."
            % (added or "none", removed or "none"),
        )


class TestReadmeCompatibilityTable(unittest.TestCase):
    """README.md must describe exactly the operations the client exposes."""

    def test_readme_documents_every_operation(self):
        documented = _readme_operations()

        missing = sorted(EXPECTED_OPERATIONS - documented)
        extra = sorted(documented - EXPECTED_OPERATIONS)

        self.assertEqual(
            documented,
            set(EXPECTED_OPERATIONS),
            "The README compatibility table disagrees with the bundled "
            "discovery document.\n"
            "  Exposed by the client but absent from the README: %s\n"
            "  Listed in the README but not exposed by the client: %s"
            % (missing or "none", extra or "none"),
        )

    def test_readme_marks_exactly_one_operation_supported(self):
        supported = set()
        for cells in _readme_table_rows():
            status = " ".join(cells[1:]).lower()
            if "not implemented" in status or "404" in status:
                continue
            match = re.search(r"`([A-Za-z0-9_.]+)`", cells[0])
            if match:
                supported.add(match.group(1))

        self.assertEqual(
            supported,
            set(SUPPORTED_OPERATIONS),
            "The README must mark exactly the operations Appning implements as "
            "supported. Expected %s, found %s. Marking an unimplemented "
            "operation as supported is worse than saying nothing: an "
            "integrator will trust it and get a 404."
            % (sorted(SUPPORTED_OPERATIONS), sorted(supported)),
        )


if __name__ == "__main__":
    unittest.main()
