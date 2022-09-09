# -*- coding: utf-8 -*-
import logging
import os
import urllib2
from datetime import date
from datetime import datetime
from datetime import timedelta

import transaction
import zope
from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from gene.common.utils import make_folder
from gene.common.utils import merge_two_dicts
from gene.common.utils import set_headers
from gene.common.utils import stream_data
from gene.tumour import _
from gene.tumour import utils
from gene.tumour.events import StepsChangedEvent
from gene.tumour.interfaces import IAnalysisResults
from gene.tumour.interfaces import IBloodSample
from gene.tumour.interfaces import IComputerDetecting
from gene.tumour.interfaces import ILibraryConstruction
from gene.tumour.interfaces import INAExtraction
from gene.tumour.interfaces import ITumour
from gene.tumour.vocabulary import invert_na_types_dict
from gene.tumour.vocabulary import invert_result_dict
from gene.tumour.vocabulary import invert_situation_dict
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.memoize import view
from plone.namedfile import NamedBlobFile
from plone.namedfile import NamedBlobImage
from plone.uuid.interfaces import IUUIDGenerator
from xlrd import open_workbook
from xlrd import xldate_as_tuple
from zope import schema
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import modified
from Products.CMFPlone.resources import add_bundle_on_request

logger = logging.getLogger(__name__)

invert_situation_local = {}
invert_na_types_local = {}
invert_result_local = {}


class DummyStep(object):
    uuid = u'uuid.uuid4().hex'
    pass


class ImportExcel(BrowserView):

    def __init__(self, context, request):
        super(ImportExcel, self).__init__(context, request)
        self.context = context
        self.request = request
        add_bundle_on_request(self.request, 'gene-tumour-main')
        self.request['disable_border'] = True
        for trans, invert in [(invert_situation_local, invert_situation_dict),
                              (invert_na_types_local, invert_na_types_dict),
                              (invert_result_local, invert_result_dict), ]:
            if not trans:
                for key in invert:
                    trans[translate(_(key), context=request)] = invert[key]

    def __call__(self):
        method = self.request.get('REQUEST_METHOD', 'GET')
        if method != 'POST':
            return self.index()

        valid_steps = (
            u'step1', u'step2', u'step3',
            u'step4', u'step5', u'None')
        auth_permissions = (
            'gene.tumour: Add BloodSample',
            'gene.tumour: Add NAExtraction',
            'gene.tumour: Add LibraryConstruction',
            'gene.tumour: Add ComputerDetecting',
            'gene.tumour: Add AnalysisResults',
            'None')

        button_next = self.request.form.get('form.buttons.next')
        if button_next and button_next in valid_steps:
            self.request.form['form.widgets.step'] = button_next

        import_step = self.request.form.get('form.widgets.step', u'step1')

        try:
            index = valid_steps[:-1].index(import_step)
        except ValueError:
            return self.request.response.redirect(self.context.absolute_url())
        else:
            if api.user.has_permission(auth_permissions[index]):
                if api.user.has_permission(auth_permissions[index + 1]):
                    button_next = valid_steps[index + 1]
                else:
                    button_next = ''
            else:
                raise Unauthorized
            self.request.form['form.buttons.next'] = button_next

        if self.request.form.get('form.buttons.import'):
            return self.import_data(import_step)

        if self.request.form.get('form.buttons.cancel'):
            return self.request.response.redirect(self.context.absolute_url())

        return self.index()

    def import_data(self, import_step=u'step1'):
        simulation_mode = self.request.form.get('form.widgets.simulation')
        self.request.form['form.widgets.simulation'] = simulation_mode
        if simulation_mode:
            msg = _(u'Dry run mode')
            api.portal.show_message(msg, self.request, 'info')

        all_true_mode = self.request.form.get('form.widgets.all_true')
        self.request.form['form.widgets.all_true'] = all_true_mode
        if all_true_mode:
            msg = _(u'Force all success')
            api.portal.show_message(msg, self.request, 'info')

        upload_file = self.request.form.get('form.widgets.excelFile', None)
        if upload_file is None or not upload_file.filename:
            msg = _(u'No files were selected.')
            api.portal.show_message(msg, self.request, 'warn')
            return self.index()
        self.request['form.widgets.filename'] = upload_file.filename

        steps_schema = (IBloodSample,
                        INAExtraction,
                        ILibraryConstruction,
                        IComputerDetecting,
                        IAnalysisResults,)
        valid_steps = (u'step1', u'step2', u'step3',
                       u'step4', u'step5',)
        query_param = ({},
                       {'portal_type': 'Tumour', 'steps': u'step1',
                        'sort_on': 'modified', 'sort_order': 'descending'},
                       {'portal_type': 'Tumour', 'steps': u'step2',
                        'sort_on': 'modified', 'sort_order': 'descending'},
                       {'portal_type': 'Tumour', 'steps': u'step3',
                        'sort_on': 'modified', 'sort_order': 'descending'},
                       {'portal_type': 'Tumour', 'steps': u'step4',
                        'sort_on': 'modified', 'sort_order': 'descending'},
                       {'portal_type': 'Tumour',
                        'sort_on': 'modified', 'sort_order': 'descending'},
                       )
        step_index = valid_steps.index(import_step)
        step_schema = steps_schema[step_index]
        start, end = utils.steps_start_end[step_index]
        query_type = {'portal_type': 'Tumour',
                      'sort_on': 'modified', 'sort_order': 'descending'}
        query_type_steps = query_param[step_index]

        try:
            workbook = open_workbook(file_contents=upload_file.read())
        except Exception:
            msg = _(u'File type not supported.')
            api.portal.show_message(msg, self.request, 'error')
            return self.index()
        sheet = workbook.sheet_by_index(0)

        data_cols = utils.import_len
        if sheet.ncols != data_cols:
            msg = translate(_(u'Excel data format error. '
                              u'Please correct it and retry. '
                              u'Error: expected ${expected} - got ${got}.',
                              mapping={'expected': data_cols,
                                       'got': sheet.ncols}),
                            context=self.request)
            api.portal.show_message(msg, self.request, 'error')
            return self.index()

        fields_name = utils.fields_name()
        fields_title = utils.fields_title()
        step_fields = utils.fields()[start:end]
        step_fields_name = fields_name[start:end]
        feedback_title = [_(u'Success or failure'),
                          _(u'Line number'),
                          _(u'Execution results')
                          ] + fields_title[start:end]

        generator = getUtility(IUUIDGenerator)
        gid = generator()
        feedback_row = []
        success_count = 0

        starttime = datetime.now()
        msg = 'Start importing {0} tumour objects at {1}'.format(
            sheet.nrows - 2, starttime)
        logger.info(msg)

        sample_title = fields_title[0]
        sample_no_unique = []
        for row_index in range(2, sheet.nrows):
            row_value = sheet.row_values(row_index)
            sample_value = row_value[0]
            step_value = row_value[start:end]

            row_buffer = [logging.NOTSET, row_index + 1, '']

            step_obj = DummyStep()
            for index, field in enumerate(step_fields):
                if not step_value[index]:
                    step_value[index] = None
                elif field[1].__class__ is schema.Date:
                    try:
                        date_value = xldate_as_tuple(
                            step_value[index],
                            workbook.datemode)
                        step_value[index] = date(*date_value[:3])
                    except (ValueError, TypeError):
                        row_buffer[0] = logging.ERROR
                elif field[1].__class__ is schema.Datetime:
                    try:
                        date_value = xldate_as_tuple(
                            step_value[index],
                            workbook.datemode)
                        step_value[index] = datetime(*date_value[:6])
                    except (ValueError, TypeError):
                        row_buffer[0] = logging.ERROR
                elif field[1].__class__ is schema.Int:
                    try:
                        step_value[index] = int(step_value[index])
                    except (ValueError, TypeError):
                        row_buffer[0] = logging.ERROR
                elif field[1].__class__ is schema.Float:
                    try:
                        step_value[index] = float(step_value[index])
                    except (ValueError, TypeError):
                        row_buffer[0] = logging.ERROR
                elif field[1].__class__ is schema.URI:
                    try:
                        step_value[index] = str(step_value[index])
                    except (ValueError, TypeError):
                        row_buffer[0] = logging.ERROR
                elif field[1].__class__ is schema.Choice:
                    if field[0] == 'result':
                        title_value_mapping = invert_result_local
                    value = unicode(step_value[index])
                    if value in title_value_mapping:
                        step_value[index] = title_value_mapping[value]
                    else:
                        step_value[index] = value
                elif field[1].__class__ is schema.List:
                    if field[0] == 'treatment_situation':
                        title_value_mapping = invert_situation_local
                    elif field[0] == 'na_extraction_type':
                        title_value_mapping = invert_na_types_local
                    value = unicode(step_value[index]).split(',')
                    step_value[index] = []
                    for item in value:
                        if item in title_value_mapping:
                            step_value[index].append(title_value_mapping[item])
                        else:
                            step_value[index].append(item)
                elif field[1].__class__.__name__ in ('NamedBlobImage',
                                                     'NamedBlobFile'):
                    try:
                        step_value[index] = str(step_value[index]).strip()
                    except (ValueError, TypeError):
                        row_buffer[0] = logging.ERROR
                else:
                    value = step_value[index]
                    if isinstance(value, float) and value - int(value) == 0.0:
                        step_value[index] = int(value)
                    step_value[index] = unicode(step_value[index]).strip()

                setattr(step_obj, field[0], step_value[index])

            value = sample_value
            if isinstance(value, float) and value - int(value) == 0.0:
                sample_value = int(value)
            sample_value = unicode(sample_value).strip()
            setattr(step_obj, 'sample_no', sample_value)

            errors = schema.getValidationErrors(step_schema, step_obj)
            if errors:
                self.extract_error(errors, row_buffer, step_schema)

            if sample_value in sample_no_unique:
                msg = translate(
                    _(u'ValuesError: '
                      u'${sample_title} ${sample_value} are not unique; ',
                      mapping={'sample_title': sample_title,
                               'sample_value': sample_value}),
                    context=self.request)
                row_buffer[0] = logging.ERROR
                row_buffer[2] += msg
            else:
                sample_no_unique.append(sample_value)

            row_buffer += step_value
            if row_buffer[0] == logging.ERROR:
                feedback_row.append(row_buffer)
                continue

            brains_sample = api.content.find(**merge_two_dicts(
                query_type, {'sample_no': sample_value}))

            if import_step == valid_steps[0]:
                if brains_sample:
                    msg = translate(
                        _(u'ValuesError: '
                          u'${sample_title} ${sample_value} already exist; ',
                          mapping={'sample_title': sample_title,
                                   'sample_value': sample_value}),
                        context=self.request)
                    row_buffer[0] = logging.ERROR
                    row_buffer[2] += msg
                    feedback_row.append(row_buffer)
                    continue

                validate_obj = step_obj
                invariant_errors = []
                try:
                    ITumour.validateInvariants(validate_obj,
                                               invariant_errors)
                except zope.interface.exceptions.Invalid:
                    pass
                except AttributeError:
                    pass
                errors = [(None, e) for e in invariant_errors]
                invalid = False
                for error in errors:
                    if error[0] is None:
                        msg = error[1].args[0]
                        msg = translate(_(msg), context=self.request)
                        row_buffer[2] += msg
                        invalid = True
                if invalid:
                    row_buffer[0] = logging.ERROR
                    feedback_row.append(row_buffer)
                    continue

                if simulation_mode:
                    obj = step_obj
                    obj.gid = gid
                else:
                    today = datetime.today()
                    year, month, day = today.year, today.month, today.day
                    container = make_folder(self.aq_parent, (year, month, day))

                    obj = createContentInContainer(
                        container,
                        portal_type='Tumour')
                    map(lambda k, v: setattr(obj, k, v),
                        step_fields_name, step_value)
                    obj.steps = import_step
                    obj.title = unicode(sample_value)
                    obj.gid = gid
                    modified(obj)

                msg = translate(_(
                    u"Import successful: "
                    u"${sample_title} ${sample_value}; ",
                    mapping={'sample_title': sample_title,
                             'sample_value': sample_value}),
                    context=self.request)
                if row_buffer[0] < logging.INFO:
                    row_buffer[0] = logging.INFO
                row_buffer[2] += msg
                feedback_row.append(row_buffer)

            elif import_step in valid_steps:
                if not brains_sample:
                    msg = translate(
                        _(u"ValuesError: "
                          u"${sample_title} ${sample_value} does't exist; ",
                          mapping={'sample_title': sample_title,
                                   'sample_value': sample_value}),
                        context=self.request)
                    row_buffer[0] = logging.ERROR
                    row_buffer[2] += msg
                    feedback_row.append(row_buffer)
                    continue

                brains_steps = api.content.find(**merge_two_dicts(
                    query_type_steps, {'sample_no': sample_value}))
                if not brains_steps:
                    expected_steps = translate(
                        _(query_type_steps['steps']), context=self.request)
                    got_steps = translate(
                        _(brains_sample[0].steps), context=self.request)
                    msg = translate(
                        _(u'StepsError: '
                          u'steps expected ${expected}, got ${got}; ',
                          mapping={'expected': expected_steps,
                                   'got': got_steps}),
                        context=self.request)
                    row_buffer[0] = logging.ERROR
                    row_buffer[2] += msg
                    feedback_row.append(row_buffer)
                    continue

                validate_obj = brains_sample[0].getObject()
                invalid = False
                for the_field, the_value in zip(step_fields, step_value):
                    field_type = the_field[1].__class__.__name__
                    field_name = the_field[0]
                    if field_type in ('NamedBlobImage', 'NamedBlobFile'):
                        if not simulation_mode and the_value != '':
                            success = self.fetch_data(the_field, the_value,
                                                      validate_obj, row_buffer)
                            if not success:
                                invalid = True
                        else:
                            setattr(validate_obj, field_name, None)
                    else:
                        setattr(validate_obj, field_name, the_value)
                if invalid:
                    row_buffer[0] = logging.ERROR
                    feedback_row.append(row_buffer)
                    continue
                invariant_errors = []
                try:
                    ITumour.validateInvariants(validate_obj,
                                               invariant_errors)
                except zope.interface.exceptions.Invalid:
                    pass
                except AttributeError:
                    pass
                errors = [(None, e) for e in invariant_errors]
                invalid = False
                for error in errors:
                    if error[0] is None:
                        msg = error[1].args[0]
                        msg = translate(_(msg), context=self.request)
                        row_buffer[2] += msg
                        invalid = True
                if invalid:
                    row_buffer[0] = logging.ERROR
                    feedback_row.append(row_buffer)
                    continue

                if not simulation_mode:
                    obj = validate_obj
                    old_steps = obj.steps
                    obj.steps = import_step
                    notify(StepsChangedEvent(obj, old_steps, import_step))
                    modified(obj)

                msg = translate(_(
                    u'Import successful: '
                    u'${sample_title} ${sample_value}; ',
                    mapping={'sample_title': sample_title,
                             'sample_value': sample_value}),
                    context=self.request)
                if row_buffer[0] < logging.INFO:
                    row_buffer[0] = logging.INFO
                row_buffer[2] += msg
                feedback_row.append(row_buffer)
            else:
                msg = _(u'Invalid import steps.')
                api.portal.show_message(msg, self.request, type='error')
                logger.error(msg)

            success_count += 1

        duration = str(timedelta(seconds=(datetime.now() - starttime).seconds))
        msg = 'Finished importing {0} tumour objects in {1}'.format(
            sheet.nrows - 2, duration)
        logger.info(msg)

        failed_count = sheet.nrows - 2 - success_count

        if success_count:
            msg = _(u'${count} item(s) import successfully.',
                    mapping={'count': success_count})
            api.portal.show_message(msg, self.request)
            logger.info('{count} item(s) import successfully.'.format(
                count=success_count))
        if failed_count:
            msg = _(u'${count} item(s) import failed.',
                    mapping={'count': failed_count})
            api.portal.show_message(msg, self.request, 'error')
            logger.warn('{count} item(s) import failed.'.format(
                count=failed_count))

        self.request['feedback_title'] = feedback_title
        self.request['feedback_value'] = feedback_row
        self.request['feedback_count'] = success_count + failed_count
        self.request['success_count'] = success_count
        self.request['failed_count'] = failed_count
        self.request['duration'] = duration

        if all_true_mode and failed_count:
            msg = _(u'An error occurred, and the operation aborted.')
            api.portal.show_message(msg, self.request, 'error')
            logger.info(msg)
            transaction.abort()

        return self.index()

    def extract_error(self, errors, row_buffer, step_schema):
        for error in errors:
            if isinstance(error, tuple) and errors[0][1].__class__.__name__ =='Invalid':
                error_doc = error[1].message
                error_doc = translate(_(error_doc),
                                      context=self.request)
                field_title = 'Invalid'
                field_name = 'Invalid'
                
            elif isinstance(error, tuple) and errors[0][1].__class__.__name__ !='Invalid':                
                error_doc = error[1].doc()
                error_doc = translate(_(error_doc),
                                      context=self.request)
                field_title = step_schema[error[0]].title
                field_title = translate(_(field_title),
                                        context=self.request)
                field_name = error[1].args[0]
            else:
                error_doc = error.doc()
                error_doc = translate(_(error_doc),
                                      context=self.request)
                field_title = ''
                field_name = error.args[0]
            error_message = ''
            if not isinstance(field_name, list):
                error_message = translate(_(field_name), context=self.request)
            msg = u'{0}: {1} {2}; '.format(
                error_doc, field_title, error_message)
            row_buffer[0] = logging.ERROR
            row_buffer[2] += msg

            if isinstance(field_name, list):
                self.extract_error(field_name, row_buffer, step_schema)

    def fetch_data(self, field_obj, field_value, _obj, row_buffer):
        field_type = field_obj[1].__class__.__name__
        field_title = field_obj[1].title
        field_name = field_obj[0]
        if field_type in ('NamedBlobImage', 'NamedBlobFile'):
            request = urllib2.Request(url=field_value)
            try:
                response = urllib2.urlopen(request)
                filename = os.path.basename(response.url)
                if field_type == 'NamedBlobFile':
                    blob_file = NamedBlobFile(
                        data=response.read(),
                        filename=safe_unicode(filename))
                elif field_type == 'NamedBlobImage':
                    blob_file = NamedBlobImage(
                        data=response.read(),
                        filename=safe_unicode(filename))
                setattr(_obj, field_name, blob_file)
                return True
            except Exception:
                field_title = translate(_(field_title), context=self.request)
                error_doc = translate(
                    _("""The URL you have provided could not be reached."""),
                    context=self.request)
                msg = u'{0}: {1}; '.format(
                    error_doc, field_title)
                row_buffer[2] += msg
                return False

    @view.memoize_contextless
    def import_excel_template(self):
        curdir = os.path.dirname(__file__)
        sep = os.path.sep

        file_object = open(
            '{0}{1}templates{2}genetumour-import-template.xls'.format(
                curdir, sep, sep), 'rb')
        set_headers(self.request.response, file_object)
        return stream_data(file_object)
