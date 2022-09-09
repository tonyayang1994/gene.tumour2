# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class GeneTumourLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes
        self.loadZCML(package=plone.app.contenttypes)
        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx)
        import gene.tumour
        import Products.DateRecurringIndex
        import Products.CMFPlone
        self.loadZCML(package=Products.CMFPlone)
        self.loadZCML(package=gene.tumour)
        z2.installProduct(app, 'Products.DateRecurringIndex')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.DateRecurringIndex')


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.CMFPlone:plone')
        applyProfile(portal, 'plone.app.contenttypes:default')
        applyProfile(portal, 'gene.tumour:default')

    def tearDownPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:uninstall')

GENE_TUMOUR_FIXTURE = GeneTumourLayer()


GENE_TUMOUR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GENE_TUMOUR_FIXTURE,),
    name='GeneTumourLayer:IntegrationTesting'
)


GENE_TUMOUR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GENE_TUMOUR_FIXTURE,),
    name='GeneTumourLayer:FunctionalTesting'
)


GENE_TUMOUR_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        GENE_TUMOUR_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='GeneTumourLayer:AcceptanceTesting'
)
