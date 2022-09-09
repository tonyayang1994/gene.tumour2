# -*- coding: utf-8 -*-
from gene.tumour.interfaces import IStepsChangedEvent
from zope.interface import implementer


@implementer(IStepsChangedEvent)
class StepsChangedEvent(object):
    def __init__(self, object, oldSteps, newSteps):
        self.object = object
        self.oldSteps = oldSteps
        self.newSteps = newSteps
