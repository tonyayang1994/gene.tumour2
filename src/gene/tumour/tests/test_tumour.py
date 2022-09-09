# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from gene.tumour.testing import GENE_TUMOUR_INTEGRATION_TESTING  # noqa
from gene.tumour.interfaces import ITumour

import  unittest


class TumourIntegrationTest(unittest.TestCase):

    layer = GENE_TUMOUR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Tumour')
        schema = fti.lookupSchema()
        self.assertEqual(ITumour, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Tumour')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Tumour')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(ITumour.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('Tumour', 'Tumour')
        self.assertTrue(
            ITumour.providedBy(self.portal['Tumour'])
        )
