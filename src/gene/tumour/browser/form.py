# -*- coding: utf-8 -*-
import datetime
import logging

from AccessControl import Unauthorized
from collective.z3cform.datagridfield import DataGridFieldFactory
from gene.common.utils import make_folder
from gene.tumour import _
from gene.tumour import utils
from gene.tumour.events import StepsChangedEvent
from gene.tumour.interfaces import IAnalysisResultsEdit
from gene.tumour.interfaces import IAnalysisResultsList
from gene.tumour.interfaces import IBloodSample
from gene.tumour.interfaces import IBloodSampleAdd
from gene.tumour.interfaces import IBloodSampleAddList
from gene.tumour.interfaces import IBloodSampleList
from gene.tumour.interfaces import IChangeSteps
from gene.tumour.interfaces import IChangeStepsList
from gene.tumour.interfaces import IComputerDetecting
from gene.tumour.interfaces import IComputerDetectingList
from gene.tumour.interfaces import IFailedRedo
from gene.tumour.interfaces import IFailedRedoList
from gene.tumour.interfaces import ILibraryConstruction
from gene.tumour.interfaces import ILibraryConstructionList
from gene.tumour.interfaces import INAExtraction
from gene.tumour.interfaces import INAExtractionList
from gene.tumour.interfaces import IWorkflowStateTransition
from gene.tumour.interfaces import IWorkflowStateTransitionList
from plone import api
from plone.dexterity.utils import createContentInContainer  # ,iterSchemata
from plone.uuid.interfaces import IUUIDGenerator
from z3c.form import form, field, button
# from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import modified
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder

logger = logging.getLogger(__name__)


class BloodSampleAddForm(form.AddForm):
    def __init__(self, context, request):
        super(BloodSampleAddForm, self).__init__(context, request)
        self.request['disable_border'] = True
        self.items = []

    _add_permission = 'gene.tumour: Add BloodSample'
    _finishedAdd = False
    _list_schema = IBloodSampleAdd

    label = _(u'Blood Sample')
    prefix = 'form.tumour.sample.add'

    fields = field.Fields(IBloodSampleAddList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        data = {'batch_list': []}
        return data

    def dumpOutput(self, data):
        batch_list = data.get('batch_list', [])
        add_count = 0

        generator = getUtility(IUUIDGenerator)
        gid = generator()

        today = datetime.datetime.today()
        year, month, day = today.year, today.month, today.day
        container = make_folder(self.aq_parent, (year, month, day))

        for entry in batch_list:
            obj = createContentInContainer(
                container,
                portal_type='Tumour',
                gid=gid)
            if obj:
                add_count += 1
                fields = dict((field[0], field[1])
                              for field in getFieldsInOrder(self._list_schema))
                for name, value in entry.items():
                    if name in fields and fields[name].readonly is False:
                        setattr(obj, name, value)
                obj.steps = 'step1'
                if 'sample_no' in entry:
                    obj.title = entry['sample_no']
                modified(obj)

        api.portal.show_message(
            _(u'${count} Item created', mapping={'count': add_count}),
            self.request,
            'info')
        logger.info(
            '{count} item(s) added successfully.'.format(count=add_count))

        return add_count

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.steps = self.formErrorsMessage
            return

        count = self.dumpOutput(data)

        context = self.getContent()
        for k, v in data.items():
            context[k] = v

        if count is not None:
            self._finishedAdd = True
            # api.portal.show_message(
            # _(u'Item created'), self.request, 'info')

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        api.portal.show_message(
            _(u'operation cancelled'), self.request,
            'info')
        self.request.response.redirect(self.nextURL())

    def update(self):
        if not api.user.has_permission(self._add_permission, obj=self.context):
            raise Unauthorized

        super(BloodSampleAddForm, self).update()

    def updateActions(self):
        super(form.AddForm, self).updateActions()

    def updateWidgets(self, prefix=None):
        super(BloodSampleAddForm, self).updateWidgets()
        self.widgets['batch_list'].auto_append = False
        self.widgets['batch_list'].allow_reorder = True
        self.widgets['batch_list'].allow_insert = True
        self.widgets['batch_list'].allow_delete = True

    @property
    def action(self):
        parent_url = self.context.absolute_url()
        view_name = self.__name__
        return parent_url + '/' + view_name

    def nextURL(self):
        url = self.context.absolute_url()
        return url

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ''
        return super(BloodSampleAddForm, self).render()


class BloodSampleEditForm(form.EditForm):
    def __init__(self, context, request):
        super(BloodSampleEditForm, self).__init__(context, request)
        self.request['disable_border'] = True
        self.items = []
        self.new_steps = ''
        self.view_edit_mode = None

    _add_permission = 'gene.tumour: Add BloodSample'
    _edit_permission = 'Review portal content'
    _finishedAdd = False
    _list_schema = IBloodSample

    label = _(u'Blood Sample')
    prefix = 'form.tumour.sample'

    fields = field.Fields(IBloodSampleList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory
    fields_readonly = []

    def getContent(self):
        data = {'batch_list': []}
        names = getFieldNamesInOrder(self._list_schema)

        for obj in self.items:
            record = {}
            for name in names:
                record[name] = getattr(obj, name, None)
            record['uuid'] = obj.UID()
            data['batch_list'].append(record)

        return data

    def dumpOutput(self, data):
        batch_list = data.get('batch_list', [])
        add_count = 0
        edit_count = 0

        for entry in batch_list:
            uuid = entry['uuid']
            obj = api.content.uuidToObject(uuid)
            if obj:
                edit_count += 1
                fields = dict((field[0], field[1])
                              for field in getFieldsInOrder(self._list_schema))
                for name, value in entry.items():
                    if name in fields and fields[name].readonly is False:
                        setattr(obj, name, value)

                if 'sample_no' in entry:
                    obj.title = entry['sample_no']
                if self.new_steps and self.new_steps != u'step*':
                    old_steps = obj.steps
                    obj.steps = self.new_steps
                    notify(StepsChangedEvent(obj, old_steps, self.new_steps))
                modified(obj)

        if add_count:
            api.portal.show_message(
                _(u'${count} Item created', mapping={'count': add_count}),
                self.request,
                'info')
            logger.info(
                '{count} item(s) added successfully.'.format(count=add_count))
        if edit_count:
            api.portal.show_message(
                _(u'${count} Item edited', mapping={'count': edit_count}),
                self.request,
                'info')
            logger.info(
                '{count} items edited successfully.'.format(count=edit_count))

        return add_count or edit_count

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.steps = self.formErrorsMessage
            return

        count = self.dumpOutput(data)

        if count is not None:
            self._finishedAdd = True
            # api.portal.show_message(
            # _(u'Item created'), self.request, 'info')

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        api.portal.show_message(
            _(u'operation cancelled'),
            self.request,
            'info')
        self.request.response.redirect(self.nextURL())

    def update(self):
        self.view_edit_mode = self.request.form.get('form.widgets.edit')
        if self.view_edit_mode:
            if not api.user.has_permission(self._edit_permission,
                                           obj=self.context):
                raise Unauthorized
        else:
            if not api.user.has_permission(self._add_permission,
                                           obj=self.context):
                raise Unauthorized

        form_view = (
            'genetumour-blood-sample-form',
            'genetumour-na-extraction-form',
            'genetumour-library-construction-form',
            'genetumour-computer-detecting-form',
            'genetumour-analysis-results-form',
            'genetumour-failed-redo-form',
            'genetumour-change-steps-form',
            'genetumour-workflow-state-transition-form',)

        old_steps = (
            u'step#', u'step1', u'step2',
            u'step3', u'step4', u'step*',
            u'step*', u'step*', u'step*',)
        new_steps = (
            u'step1', u'step2', u'step3',
            u'step4', u'step5', u'step*',
            u'step*', u'step*', u'step*',)

        try:
            index = form_view.index(self.__name__)
        except ValueError:
            filter_steps = ''
        else:
            if self.view_edit_mode:
                filter_steps = new_steps[index]
            else:
                filter_steps = old_steps[index]
                self.new_steps = new_steps[index]

        uuids = self.request.get('uuids', '')
        uuids = uuids and uuids.split(',') or []
        for uuid in uuids:
            item = api.content.uuidToObject(uuid)
            if item and (item.steps == filter_steps or
                         u'step*' == filter_steps):
                self.items.append(item)
        super(BloodSampleEditForm, self).update()

    def updateActions(self):
        super(form.EditForm, self).updateActions()

    def updateWidgets(self, prefix=None):
        super(BloodSampleEditForm, self).updateWidgets()
        self.widgets['batch_list'].auto_append = False
        self.widgets['batch_list'].allow_reorder = True
        self.widgets['batch_list'].columns[0]['mode'] = HIDDEN_MODE
        if self.view_edit_mode:
            self.widgets['batch_list'].allow_reorder = False
            self.widgets['batch_list'].allow_insert = False
            self.widgets['batch_list'].allow_delete = False
            self.widgets['batch_list'].auto_append = False

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets['uuid'].mode = HIDDEN_MODE
        for name in self.fields_readonly:
            if name in widgets:
                widgets[name].mode = DISPLAY_MODE

    @property
    def action(self):
        self._parent_action = super(BloodSampleEditForm, self).action
        parent_url = self.context.absolute_url()
        view_name = self.__name__
        return parent_url + '/' + view_name

    def nextURL(self):
        url = self.context.absolute_url()
        return url

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ''
        return super(BloodSampleEditForm, self).render()


class NAExtractionEditForm(BloodSampleEditForm):
    """"""
    _add_permission = 'gene.tumour: Add NAExtraction'
    _list_schema = INAExtraction

    label = _(u'NA Extraction')
    prefix = 'form.tumour.na'

    fields = field.Fields(INAExtractionList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory
    fields_readonly = ['sample_no', ]

    def updateWidgets(self, prefix=None):
        super(NAExtractionEditForm, self).updateWidgets()
        self.widgets['batch_list'].allow_insert = False
        self.widgets['batch_list'].allow_delete = False
        self.widgets['batch_list'].auto_append = False


class LibraryConstructionEditForm(NAExtractionEditForm):
    """"""
    _add_permission = 'gene.tumour: Add LibraryConstruction'
    _list_schema = ILibraryConstruction

    label = _(u'Library Construction')
    prefix = 'form.tumour.library'

    fields = field.Fields(ILibraryConstructionList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory


class ComputerDetectingEditForm(NAExtractionEditForm):
    """"""
    _add_permission = 'gene.tumour: Add ComputerDetecting'
    _list_schema = IComputerDetecting

    label = _(u'Computer Detecting')
    prefix = 'form.tumour.detecting'

    fields = field.Fields(IComputerDetectingList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory


class AnalysisResultsEditForm(NAExtractionEditForm):
    """"""
    _add_permission = 'gene.tumour: Add AnalysisResults'
    _list_schema = IAnalysisResultsEdit

    label = _(u'Analysis Results')
    prefix = 'form.tumour.results'

    fields = field.Fields(IAnalysisResultsList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory


class FailedRedoEditForm(BloodSampleEditForm):
    """"""
    _add_permission = 'Review portal content'
    _edit_permission = 'Review portal content'
    _finishedAdd = False
    _list_schema = IFailedRedo

    label = _(u'Failed Redo')
    prefix = 'form.tumour.redo'

    fields = field.Fields(IFailedRedoList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory
    fields_readonly = ['sample_no', 'barcode', 'name', 'review_state']

    def getContent(self):
        data = {'batch_list': []}
        names = getFieldNamesInOrder(self._list_schema)

        for obj in self.items:
            if api.content.get_state(obj=obj) == 'failed':
                record = {}
                for name in names:
                    record[name] = getattr(obj, name, None)
                record['uuid'] = obj.UID()
                record['review_state'] = translate(
                    _(api.content.get_state(obj).title()),
                    context=api.portal.getRequest())
                data['batch_list'].append(record)
        return data

    def dumpOutput(self, data):
        """
        """
        batch_list = data.get('batch_list', [])
        add_count = 0

        for entry in batch_list:
            uuid = entry['uuid']
            obj = api.content.uuidToObject(uuid)
            change_note = entry['changeNote']
            valid_steps = (u'step2', u'step3', u'step4')
            steps = entry['steps']
            try:
                index = valid_steps.index(steps)
            except ValueError:
                index = 0
            start, end = 0, utils.steps_start_end[index][1]
            step_field = utils.fields_name()[start:end]
            step_field.extend(['gid', 'creation_date', 'title'])

            if obj:
                container = obj.aq_parent
                new_obj = createContentInContainer(
                    container,
                    portal_type='Tumour')
                [setattr(new_obj, name, getattr(obj, name, ''))
                 for name in step_field]
                [setattr(new_obj, k, v) for k, v in entry.items()]
                new_obj.steps = utils.progress_steps[index]
                add_count += 1
                change_note = u"{0} - {1}: {2}.".format(
                    translate(self.label, context=api.portal.getRequest()),
                    translate(_(steps), context=api.portal.getRequest()),
                    change_note if change_note else '')
                annotation = IAnnotations(self.context.REQUEST)
                annotation['plone.app.versioningbehavior' +
                           '-changeNote'] = change_note
                modified(new_obj)

        if add_count:
            api.portal.show_message(
                _(u'${count} Item created', mapping={'count': add_count}),
                self.request,
                'info')
            logger.info(
                '{count} item(s) added successfully.'.format(count=add_count))

        return add_count

    def updateWidgets(self, prefix=None):
        super(FailedRedoEditForm, self).updateWidgets()
        self.widgets['batch_list'].allow_reorder = False
        self.widgets['batch_list'].allow_insert = False
        self.widgets['batch_list'].allow_delete = False
        self.widgets['batch_list'].auto_append = False
        self.widgets['batch_list'].columns[0]['mode'] = HIDDEN_MODE


class ChangeStepsEditForm(FailedRedoEditForm):
    """"""
    _add_permission = 'Review portal content'
    _edit_permission = 'Review portal content'
    _finishedAdd = False
    _list_schema = IChangeSteps

    label = _(u'Change Steps')
    prefix = 'form.tumour.steps'

    fields = field.Fields(IChangeStepsList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory
    fields_readonly = ['sample_no', 'barcode', 'name', 'review_state']

    def getContent(self):
        data = {'batch_list': []}
        names = getFieldNamesInOrder(self._list_schema)

        for obj in self.items:
            record = {}
            for name in names:
                record[name] = getattr(obj, name, None)
            record['uuid'] = obj.UID()
            record['review_state'] = translate(
                _(api.content.get_state(obj).title()),
                context=api.portal.getRequest())
            data['batch_list'].append(record)

        return data

    def dumpOutput(self, data):
        """
        """
        batch_list = data.get('batch_list', [])
        edit_count = 0

        for entry in batch_list:
            uuid = entry['uuid']
            obj = api.content.uuidToObject(uuid)
            change_note = entry['changeNote']
            if obj:
                old_steps = obj.steps
                if old_steps != entry['steps']:
                    obj.steps = entry['steps']
                    edit_count += 1
                    notify(StepsChangedEvent(obj, old_steps, entry['steps']))
                    change_note = u"{0} - {1}->{2}: {3}.".format(
                        translate(self.label,
                                  context=api.portal.getRequest()),
                        translate(_(old_steps),
                                  context=api.portal.getRequest()),
                        translate(_(obj.steps),
                                  context=api.portal.getRequest()),
                        change_note if change_note else '')
                    annotation = IAnnotations(self.context.REQUEST)
                    annotation['plone.app.versioningbehavior' +
                               '-changeNote'] = change_note
                    modified(obj)

        if edit_count:
            api.portal.show_message(
                _(u'${count} Item edited', mapping={'count': edit_count}),
                self.request,
                'info')
            logger.info(
                '{count} item(s) edited successfully.'.format(
                    count=edit_count))

        return edit_count


class WorkflowStateTransitionForm(ChangeStepsEditForm):
    """"""
    _add_permission = 'Review portal content'
    _edit_permission = 'Review portal content'
    _finishedAdd = False
    _list_schema = IWorkflowStateTransition

    label = _(u'Workflow state transition')
    prefix = 'form.tumour.state'

    fields = field.Fields(IWorkflowStateTransitionList)
    fields['batch_list'].widgetFactory = DataGridFieldFactory
    fields_readonly = ['sample_no', 'barcode', 'name',
                       'steps', 'review_state',
                       'result', 'result_info']

    def datagridInitialise(self, subform, widget):
        pass

    def dumpOutput(self, data):
        """
        """
        batch_list = data.get('batch_list', [])
        edit_count = 0

        for entry in batch_list:
            uuid = entry['uuid']
            obj = api.content.uuidToObject(uuid)
            if obj:
                transition = entry['transition_state']
                change_note = entry['changeNote']
                if transition:
                    api.content.transition(
                        obj=obj, transition=transition, comment=change_note)
                    edit_count += 1
                    obj.reindexObject(idxs=['review_state'])
        if edit_count:
            api.portal.show_message(
                _(u'${count} Item state changed',
                  mapping={'count': edit_count}),
                self.request,
                'info')
            logger.info(
                '{count} item(s) state changed.'.format(
                    count=edit_count))

        return edit_count
