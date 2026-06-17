#!/usr/bin/env python3
###############################################################
# Copyright 2026 Lawrence Livermore National Security, LLC
# (c.f. AUTHORS, NOTICE.LLNS, COPYING)
#
# This file is part of the Flux resource manager framework.
# For details, see https://github.com/flux-framework.
#
# SPDX-License-Identifier: LGPL-3.0
###############################################################
#
# flux.schedbench.sweep tests
#
# Unit tests for scheduler recipe processing and TOML parsing

import unittest

from flux.schedbench.sweep import _recipe_from_block


class TestRecipeFromBlock(unittest.TestCase):
    """Test _recipe_from_block() scheduler TOML parsing"""

    def test_amend_r_simple(self):
        """amend_r field maps to fake-resources.amend-r in conf"""
        block = {
            "name": "treepool",
            "amend_r": "flux.resource.TreePool:amend",
        }
        recipe = _recipe_from_block(block)
        self.assertEqual(recipe["name"], "treepool")
        self.assertEqual(
            recipe["conf"]["fake-resources.amend-r"],
            "flux.resource.TreePool:amend",
        )

    def test_amend_r_with_modules(self):
        """amend_r works alongside modules config"""
        block = {
            "name": "treepool",
            "modules": [{"name": "sched-simple", "options": "pool-class=TreePool"}],
            "amend_r": "flux.resource.TreePool:amend",
        }
        recipe = _recipe_from_block(block)
        self.assertEqual(recipe["name"], "treepool")
        self.assertEqual(len(recipe["modules"]), 1)
        self.assertEqual(recipe["modules"][0]["name"], "sched-simple")
        self.assertEqual(
            recipe["conf"]["fake-resources.amend-r"],
            "flux.resource.TreePool:amend",
        )

    def test_amend_r_overrides_conf(self):
        """amend_r takes precedence over conf entry"""
        block = {
            "name": "test",
            "conf": {
                "fake-resources.amend-r": "old-value",
                "other-key": "other-value",
            },
            "amend_r": "new-value",
        }
        recipe = _recipe_from_block(block)
        # amend_r should override the conf entry
        self.assertEqual(recipe["conf"]["fake-resources.amend-r"], "new-value")
        # other conf entries should be preserved
        self.assertEqual(recipe["conf"]["other-key"], "other-value")

    def test_conf_without_amend_r(self):
        """conf still works when amend_r is not present"""
        block = {
            "name": "test",
            "conf": {
                "fake-resources.amend-r": "conf-value",
                "other-key": "other-value",
            },
        }
        recipe = _recipe_from_block(block)
        self.assertEqual(recipe["conf"]["fake-resources.amend-r"], "conf-value")
        self.assertEqual(recipe["conf"]["other-key"], "other-value")

    def test_no_amend_r_or_conf(self):
        """Recipe works without amend_r or conf"""
        block = {"name": "simple"}
        recipe = _recipe_from_block(block)
        self.assertEqual(recipe["name"], "simple")
        self.assertEqual(recipe["conf"], {})

    def test_amend_r_is_known_key(self):
        """amend_r is recognized as a valid scheduler key"""
        # This should not raise ValueError about unknown keys
        block = {
            "name": "test",
            "amend_r": "value",
        }
        try:
            recipe = _recipe_from_block(block)
            self.assertIn("fake-resources.amend-r", recipe["conf"])
        except ValueError as e:
            self.fail(f"amend_r should be a known key, but got: {e}")


if __name__ == "__main__":
    unittest.main()
