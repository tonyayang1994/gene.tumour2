# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from gene.tumour.testing import GENE_TUMOUR_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that gene.tumour is properly installed."""

    layer = GENE_TUMOUR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if gene.tumour is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'gene.tumour'))

    def test_browserlayer(self):
        """Test that IGeneTumourLayer is registered."""
        from gene.tumour.interfaces import (
            IGeneTumourLayer)
        from plone.browserlayer import utils
        self.assertIn(IGeneTumourLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = GENE_TUMOUR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['gene.tumour'])

    def test_product_uninstalled(self):
        """Test if gene.tumour is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'gene.tumour'))

    def test_browserlayer_removed(self):
        """Test that IGeneTumourLayer is removed."""
        from gene.tumour.interfaces import IGeneTumourLayer
        from plone.browserlayer import utils
        self.assertNotIn(IGeneTumourLayer, utils.registered_layers())
