# -*- coding: utf-8 -*-
from gene.tumour.interfaces import IBloodSampleAdd
from gene.tumour.interfaces import IBloodSampleAddList
from gene.tumour.interfaces import IBloodSampleList
from gene.tumour.interfaces import IFailedRedoList
from gene.tumour.interfaces import IGeneTumourLayer
from gene.tumour.interfaces import IWorkflowStateTransitionList
from gene.tumour.utils import normal_review_states
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.app.uuid.utils import uuidToCatalogBrain
from z3c.form import validator
from zope.schema.interfaces import NotUnique
from zope.schema.interfaces import RequiredMissing


class BloodSampleAddValidator(validator.SimpleFieldValidator):

    def validate(self, value, force=False):
        super(BloodSampleAddValidator, self).validate(value)
        field = self.field.getName()
        query = dict()
        query['portal_type'] = 'Tumour'
        query[field] = value
        results = api.content.find(**query)
        if results:
            raise NotUnique


validator.WidgetValidatorDiscriminators(
    validator=BloodSampleAddValidator,
    request=IGeneTumourLayer,
    field=IBloodSampleAdd['sample_no'])


class BloodSampleAddListValidator(validator.SimpleFieldValidator):

    def validate(self, value, force=False):
        super(BloodSampleAddListValidator, self).validate(value)
        sample_no_list = [item['sample_no'] for item in value]
        sample_no_set = set(sample_no_list)
        if len(sample_no_list) != len(sample_no_set):
            raise NotUnique


validator.WidgetValidatorDiscriminators(
    validator=BloodSampleAddListValidator,
    request=IGeneTumourLayer,
    field=IBloodSampleAddList['batch_list'])


class BloodSampleEditListValidator(validator.SimpleFieldValidator):

    def validate(self, value, force=False):
        super(BloodSampleEditListValidator, self).validate(value)
        sample_no_list = [item['sample_no'] for item in value]
        sample_no_set = set(sample_no_list)
        if len(sample_no_list) != len(sample_no_set):
            raise NotUnique
        for item in value:
            query = dict()
            query['portal_type'] = 'Tumour'
            query['sample_no'] = item['sample_no']
            query['review_state'] = {'query': normal_review_states,
                                     'operator': 'or'}
            results = api.content.find(**query)
            if results and results[0].UID != item['uuid']:
                obj = uuidToCatalogBrain(item['uuid'])
                if obj and obj.review_state in normal_review_states:
                    raise NotUnique


validator.WidgetValidatorDiscriminators(
    validator=BloodSampleEditListValidator,
    request=IGeneTumourLayer,
    field=IBloodSampleList['batch_list'])


class FailedRedoEditListValidator(validator.SimpleFieldValidator):

    def validate(self, value, force=False):
        for item in value:
            real_obj = uuidToObject(item['uuid'])
            if real_obj:
                query = dict()
                query['portal_type'] = 'Tumour'
                query['sample_no'] = real_obj.sample_no
                query['review_state'] = {'query': normal_review_states,
                                         'operator': 'or'}
                results = api.content.find(**query)
                if results:
                    raise NotUnique
            else:
                raise RequiredMissing


validator.WidgetValidatorDiscriminators(
    validator=FailedRedoEditListValidator,
    request=IGeneTumourLayer,
    field=IFailedRedoList['batch_list'])


class WorkflowStateTransitionListValidator(validator.SimpleFieldValidator):

    def validate(self, value, force=False):
        for item in value:
            if item['transition_state'] in (u'fallback', u'success'):
                real_obj = uuidToObject(item['uuid'])
                if real_obj:
                    query = dict()
                    query['portal_type'] = 'Tumour'
                    query['sample_no'] = real_obj.sample_no
                    query['review_state'] = {'query': normal_review_states,
                                             'operator': 'or'}
                    results = api.content.find(**query)
                    if results and results[0].UID != item['uuid']:
                        raise NotUnique
                else:
                    raise RequiredMissing


validator.WidgetValidatorDiscriminators(
    validator=WorkflowStateTransitionListValidator,
    request=IGeneTumourLayer,
    field=IWorkflowStateTransitionList['batch_list'])
