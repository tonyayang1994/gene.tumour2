# -*- coding: utf-8 -*-

import datetime

from collective.z3cform.datagridfield import DictRow
from gene.common.utils import url_exists
from gene.tumour import _
from plone.autoform import directives
from plone.namedfile import field
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import ValidationError


def validate_time(value):
    if value and (value - datetime.datetime.now()).total_seconds() > 0:
        raise ValidationError(
            _(u"This time cannot be greater than current time")
        )
    return True


def validate_sample(value):
    if not check_sample_date(value):
        raise ValidationError(
            _(u"The value is not of the correct format")
        )


def check_sample_date(value):
    pass


def validate_url(value):
    if value != '' and not url_exists(value):
        raise InvalidURL(
            _(u"The URL you have provided could not be reached. "
              u"Please verify the URL is correct "
              u"and that the network location is reachable.")
        )
    return True


class InvalidURL(ValidationError):
    __doc__ = _("""The URL you have provided could not be reached.""")


class IGeneTumourLayer(IDefaultBrowserLayer):
    pass


class IGeneTumourSettings(Interface):
    sms_notify_enabled = schema.Bool(
        title=_(u"SMS notification"),
        description=_(u"If selected, the sent SMS notification to user."),
        default=False
    )

    sms_notify_message = schema.Text(
        title=_(u"SMS text"),
        description=_(u"You need to send the text."),
        default=u'',
        required=False,
    )

    email_notify_enabled = schema.Bool(
        title=_(u"Email notification"),
        description=_(u"If selected, "
                      u"enabled step change Email message notifications."),
        default=False
    )

    record_expire_days = schema.Int(
        title=_(u"Record Expiration days"),
        description=_(u"Please fill out an integer range: 1-365"),
        min=0,
        max=365,
        default=0,
        required=False)

    record_expire_notify = schema.Choice(
        title=_(u"Record expiration notification user group"),
        description=_(u"When the entry has expired, "
                      u"send an email message to inform the user"),
        vocabulary="plone.app.vocabularies.Groups",
        required=False)

    user_search_filter = schema.Dict(
        title=_(u"User search filter"),
        description=_(u"User search filter additional conditions"),
        required=False,
        key_type=schema.Choice(
            title=_(u"User group"),
            vocabulary="plone.app.vocabularies.Groups",
            required=True),
        value_type=schema.TextLine(
            title=_(u"Filter condition"),
            description=_(u"Users search additional filtering criteria. "
                          u"Reference usage: Advanced search instructions"),
            required=True)
    )


class ITumour(Interface):

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=True,
    )

    barcode = schema.TextLine(
        title=_(u"Barcode"),
        required=False,
    )

    name = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )

    sex = schema.TextLine(
        title=_(u"Sex"),
        required=True,
    )

    age = schema.Int(
        title=_(u"Age"),
        min=0,
        max=200,
        required=True,
    )

    inspection_item = schema.TextLine(
        title=_(u"Inspection item"),
        required=True,
    )

    inspection_method = schema.TextLine(
        title=_(u"Inspection method"),
        required=True,
    )

    submission_hospital = schema.TextLine(
        title=_(u"Submission hospital"),
        required=False,
    )

    submission_department = schema.TextLine(
        title=_(u"Submission department"),
        required=False,
    )

    submission_doctor = schema.TextLine(
        title=_(u"Submission doctor"),
        required=False,
    )

    pathological_diagnosis = schema.TextLine(
        title=_(u"Pathological diagnosis"),
        required=False,
    )

    pathological_no = schema.TextLine(
        title=_(u"Pathological number"),
        required=False,
    )

    treatment_situation = schema.List(
        title=_(u"Treatment situation"),
        required=False,
        value_type=schema.Choice(
            title=_(u"Treatment"),
            vocabulary="gene.tumour.vocabulary.treatment_situation",
            required=True),
    )

    received_operator = schema.TextLine(
        title=_(u"Received operator"),
        required=False,
    )

    received_phone = schema.TextLine(
        title=_(u"Received phone"),
        required=False,
    )

    received_address = schema.TextLine(
        title=_(u"Received address"),
        required=False,
    )

    sample_type = schema.TextLine(
        title=_(u"Sample type"),
        required=True,
    )

    sampling_time = schema.Datetime(
        title=_(u"Sampling time"),
        constraint=validate_time,
        required=False,
    )

    received_time = schema.Datetime(
        title=_(u"Received time"),
        constraint=validate_time,
        required=False,
    )

    sample_size = schema.TextLine(
        title=_(u"Sample size "),
        required=False,
    )

    sample_note = schema.TextLine(
        title=_(u"Sample note"),
        required=False,
    )

    sample_source = schema.TextLine(
        title=_(u"Sample source"),
        required=False,
    )

    tcc_tcp = schema.Float(
        title=_(u"TCC/TCP"),
        description=_(u"Glass inspection"
                      u"(Percentage of tumor cells/tumor cells)"),
        required=False,
        min=0.0,
        max=1.00,
    )


    task_no = schema.TextLine(
        title=_(u"Task no"),
        required=False,
    )

    separation_time = schema.Datetime(
        title=_(u"Separation time"),
        constraint=validate_time,
        required=False,
    )

    separation_operator = schema.TextLine(
        title=_(u"Separation operator"),
        required=False,
    )

    plasma_location = schema.TextLine(
        title=_(u"Plasma location"),
        required=False,
    )

    separation_note = schema.TextLine(
        title=_(u"Plasma separation note"),
        required=False,
    )

    extraction_time = schema.Datetime(
        title=_(u"Extraction time"),
        constraint=validate_time,
        required=True,
    )

    na_extraction_type = schema.List(
        title=_(u"NA Extraction Type"),
        required=True,
        value_type=schema.Choice(
            title=_(u"NA type"),
            vocabulary="gene.tumour.vocabulary.na_types",
            required=True),
    )

    na_plasma_volume = schema.Float(
        title=_(u"NA plasma volume(ml)"),
        min=0.0,
        required=False,
    )

    na_concentration = schema.Float(
        title=_(u"NA concentration (NG/UL)"),
        min=0.0,
        required=False,
    )

    absorbance = schema.Float(
        title=_(u"Absorbance 260/280"),
        min=0.0,
        required=False,
    )

    na_kit_no = schema.TextLine(
        title=_(u"NA extraction kit lot number"),
        required=False,
    )

    na_operator = schema.TextLine(
        title=_(u"NA extracting operator"),
        required=False,
    )


    library_time = schema.Datetime(
        title=_(u"Library construction time"),
        constraint=validate_time,
        required=True,
    )

    library_barcode = schema.TextLine(
        title=_(u"Library barcode"),
        required=False,
    )

    library_concentration = schema.Float(
        title=_(u"Library concentration (NG/UL)"),
        min=0.0,
        required=False,
    )

    library_operator = schema.TextLine(
        title=_(u"Library construction operator"),
        required=False,
    )

    library_kit_no = schema.TextLine(
        title=_(u"Library kit lot number"),
        required=False,
    )

    library_location = schema.TextLine(
        title=_(u"Library location"),
        required=False,
    )

    capture_concentration = schema.Float(
        title=_(u"Post capture concentration (NG/UL)"),
        min=0.0,
        required=False,
    )

    template_time = schema.Datetime(
        title=_(u"Template preparation time"),
        constraint=validate_time,
        required=True,
    )

    template_operator = schema.TextLine(
        title=_(u"Template preparation operator"),
        required=False,
    )

    template_kit_no = schema.TextLine(
        title=_(u"Template kit lot number"),
        required=False,
    )

    ot_instrument_no = schema.TextLine(
        title=_(u"OT instrument number"),
        required=False,
    )

    es_instrument_no = schema.TextLine(
        title=_(u"ES instrument number"),
        required=False,
    )

    sequencing_time = schema.Datetime(
        title=_(u"Sequencing time"),
        constraint=validate_time,
        required=True,
    )

    sequencing_operator = schema.TextLine(
        title=_(u"Sequencing operator"),
        required=False,
    )

    sequencing_server = schema.TextLine(
        title=_(u"Sequencer number"),
        required=False,
    )

    sequencing_ip = schema.TextLine(
        title=_(u"Sequencing IP"),
        required=False,
    )

    sequencing_filename = schema.TextLine(
        title=_(u"Sequencing filename"),
        required=False,
    )


    result = schema.Choice(
        title=_(u"Result"),
        required=False,
        vocabulary=u"gene.tumour.vocabulary.analysis_result",
    )

    result_info = schema.TextLine(
        title=_(u"Result information"),
        required=False,
    )

    quality_file = field.NamedBlobFile(
        title=_(u"Quality control document"),
        required=False,
    )

    result_file = field.NamedBlobFile(
        title=_(u"Result detail"),
        required=False,
    )


    steps = schema.Choice(
        title=_(u"Steps"),
        required=True,
        default=u'step1',
        vocabulary=u"gene.tumour.vocabulary.progress_steps",
    )

    @invariant
    def steps_date_valid(obj):
        steps_date = [('sampling_time', 'received_time'),
                      ('separation_time', 'extraction_time'),
                      ('library_time',),
                      ('template_time', 'sequencing_time')]
        steps_date.reverse()
        for index, names in enumerate(steps_date):
            prev_date = []
            [prev_date.extend(item) for item in steps_date[index + 1:]]
            for after in names:
                after_value = getattr(obj, after, None)
                if after_value is not None:
                    for prev in prev_date:
                        prev_value = getattr(obj, prev, None)
                        if (prev_value is not None
                            and isinstance(prev_value, datetime.date)
                            and isinstance(after_value, datetime.date)
                            and prev_value > after_value):
                            raise Invalid(
                                _(u'After steps time must be greater than '
                                  u'or equal to the previous steps time'))


class IBloodSampleAdd(model.Schema):

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=True,
    )

    barcode = schema.TextLine(
        title=_(u"Barcode"),
        required=False,
    )

    name = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )

    sex = schema.TextLine(
        title=_(u"Sex"),
        required=True,
    )

    age = schema.Int(
        title=_(u"Age"),
        min=0,
        max=200,
        required=True,
    )

    inspection_item = schema.TextLine(
        title=_(u"Inspection item"),
        required=True,
    )

    inspection_method = schema.TextLine(
        title=_(u"Inspection method"),
        required=True,
    )

    submission_hospital = schema.TextLine(
        title=_(u"Submission hospital"),
        required=False,
    )

    submission_department = schema.TextLine(
        title=_(u"Submission department"),
        required=False,
    )

    submission_doctor = schema.TextLine(
        title=_(u"Submission doctor"),
        required=False,
    )

    pathological_diagnosis = schema.TextLine(
        title=_(u"Pathological diagnosis"),
        required=False,
    )

    pathological_no = schema.TextLine(
        title=_(u"Pathological number"),
        required=False,
    )

    directives.widget(treatment_situation=CheckBoxFieldWidget)
    treatment_situation = schema.List(
        title=_(u"Treatment situation"),
        required=False,
        value_type=schema.Choice(
            title=_(u"Treatment"),
            vocabulary="gene.tumour.vocabulary.treatment_situation",
            required=True),
    )

    received_operator = schema.TextLine(
        title=_(u"Received operator"),
        required=False,
    )

    received_phone = schema.TextLine(
        title=_(u"Received phone"),
        required=False,
    )

    received_address = schema.TextLine(
        title=_(u"Received address"),
        required=False,
    )

    sample_type = schema.TextLine(
        title=_(u"Sample type"),
        required=True,
    )

    sampling_time = schema.Datetime(
        title=_(u"Sampling time"),
        constraint=validate_time,
        required=False,
    )

    received_time = schema.Datetime(
        title=_(u"Received time"),
        constraint=validate_time,
        required=False,
    )

    sample_size = schema.TextLine(
        title=_(u"Sample size "),
        required=False,
    )

    sample_note = schema.TextLine(
        title=_(u"Sample note"),
        required=False,
    )

    sample_source = schema.TextLine(
        title=_(u"Sample source"),
        required=False,
    )

    tcc_tcp = schema.Float(
        title=_(u"TCC/TCP"),
        description=_(u"Glass inspection"
                      u"(Percentage of tumor cells/tumor cells)"),
        required=False,
        min=0.0,
        max=1.00,
    )


class IBloodSample(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=True,
    )

    barcode = schema.TextLine(
        title=_(u"Barcode"),
        required=False,
    )

    name = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )

    sex = schema.TextLine(
        title=_(u"Sex"),
        required=True,
    )

    age = schema.Int(
        title=_(u"Age"),
        min=0,
        max=200,
        required=True,
    )

    inspection_item = schema.TextLine(
        title=_(u"Inspection item"),
        required=True,
    )

    inspection_method = schema.TextLine(
        title=_(u"Inspection method"),
        required=True,
    )

    submission_hospital = schema.TextLine(
        title=_(u"Submission hospital"),
        required=False,
    )

    submission_department = schema.TextLine(
        title=_(u"Submission department"),
        required=False,
    )

    submission_doctor = schema.TextLine(
        title=_(u"Submission doctor"),
        required=False,
    )

    pathological_diagnosis = schema.TextLine(
        title=_(u"Pathological diagnosis"),
        required=False,
    )

    pathological_no = schema.TextLine(
        title=_(u"Pathological number"),
        required=False,
    )

    treatment_situation = schema.List(
        title=_(u"Treatment situation"),
        required=False,
        value_type=schema.Choice(
            title=_(u"Treatment"),
            vocabulary="gene.tumour.vocabulary.treatment_situation",
            required=True),
    )

    received_operator = schema.TextLine(
        title=_(u"Received operator"),
        required=False,
    )

    received_phone = schema.TextLine(
        title=_(u"Received phone"),
        required=False,
    )

    received_address = schema.TextLine(
        title=_(u"Received address"),
        required=False,
    )

    sample_type = schema.TextLine(
        title=_(u"Sample type"),
        required=True,
    )

    sampling_time = schema.Datetime(
        title=_(u"Sampling time"),
        constraint=validate_time,
        required=False,
    )

    received_time = schema.Datetime(
        title=_(u"Received time"),
        constraint=validate_time,
        required=False,
    )

    sample_size = schema.TextLine(
        title=_(u"Sample size "),
        required=False,
    )

    sample_note = schema.TextLine(
        title=_(u"Sample note"),
        required=False,
    )

    sample_source = schema.TextLine(
        title=_(u"Sample source"),
        required=False,
    )

    tcc_tcp = schema.Float(
        title=_(u"TCC/TCP"),
        description=_(u"Glass inspection"
                      u"(Percentage of tumor cells/tumor cells)"),
        required=False,
        min=0.0,
        max=1.00,
    )

    @invariant
    def pre_older_after(obj):
        prev = 'sampling_time'
        after = 'received_time'
       
        prev_value = getattr(obj, prev, None)
        after_value = getattr(obj, after, None)
        if after_value is not None:
            if (prev_value is not None 
                and isinstance(prev_value, datetime.datetime)
                and isinstance(after_value, datetime.datetime)
                and prev_value > after_value):
                raise Invalid(
                                _(u'After steps time must be greater than '
                                  u'or equal to the previous steps time'))

class INAExtraction(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    task_no = schema.TextLine(
        title=_(u"Task no"),
        required=False,
    )

    separation_time = schema.Datetime(
        title=_(u"Separation time"),
        constraint=validate_time,
        required=False,
    )

    separation_operator = schema.TextLine(
        title=_(u"Separation operator"),
        required=False,
    )

    plasma_location = schema.TextLine(
        title=_(u"Plasma location"),
        required=False,
    )

    separation_note = schema.TextLine(
        title=_(u"Plasma separation note"),
        required=False,
    )

    extraction_time = schema.Datetime(
        title=_(u"Extraction time"),
        constraint=validate_time,
        required=True,
    )

    na_extraction_type = schema.List(
        title=_(u"NA Extraction Type"),
        required=True,
        value_type=schema.Choice(
            title=_(u"NA type"),
            vocabulary="gene.tumour.vocabulary.na_types",
            required=True),
    )

    na_plasma_volume = schema.Float(
        title=_(u"NA plasma volume(ml)"),
        min=0.0,
        required=False,
    )

    na_concentration = schema.Float(
        title=_(u"NA concentration (NG/UL)"),
        min=0.0,
        required=False,
    )

    absorbance = schema.Float(
        title=_(u"Absorbance 260/280"),
        min=0.0,
        required=False,
    )

    na_kit_no = schema.TextLine(
        title=_(u"NA extraction kit lot number"),
        required=False,
    )

    na_operator = schema.TextLine(
        title=_(u"NA extracting operator"),
        required=False,
    )


class ILibraryConstruction(model.Schema):

    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    library_time = schema.Datetime(
        title=_(u"Library construction time"),
        constraint=validate_time,
        required=True,
    )

    library_barcode = schema.TextLine(
        title=_(u"Library barcode"),
        required=False,
    )

    library_concentration = schema.Float(
        title=_(u"Library concentration (NG/UL)"),
        min=0.0,
        required=False,
    )

    library_operator = schema.TextLine(
        title=_(u"Library construction operator"),
        required=False,
    )

    library_kit_no = schema.TextLine(
        title=_(u"Library kit lot number"),
        required=False,
    )

    library_location = schema.TextLine(
        title=_(u"Library location"),
        required=False,
    )

    capture_concentration = schema.Float(
        title=_(u"Post capture concentration (NG/UL)"),
        min=0.0,
        required=False,
    )


class IComputerDetecting(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    template_time = schema.Datetime(
        title=_(u"Template preparation time"),
        constraint=validate_time,
        required=True,
    )

    template_operator = schema.TextLine(
        title=_(u"Template preparation operator"),
        required=False,
    )

    template_kit_no = schema.TextLine(
        title=_(u"Template kit lot number"),
        required=False,
    )

    ot_instrument_no = schema.TextLine(
        title=_(u"OT instrument number"),
        required=False,
    )

    es_instrument_no = schema.TextLine(
        title=_(u"ES instrument number"),
        required=False,
    )

    sequencing_time = schema.Datetime(
        title=_(u"Sequencing time"),
        constraint=validate_time,
        required=True,
    )

    sequencing_operator = schema.TextLine(
        title=_(u"Sequencing operator"),
        required=False,
    )

    sequencing_server = schema.TextLine(
        title=_(u"Sequencer number"),
        required=False,
    )

    sequencing_ip = schema.TextLine(
        title=_(u"Sequencing IP"),
        required=False,
    )

    sequencing_filename = schema.TextLine(
        title=_(u"Sequencing filename"),
        required=False,
    )


class IAnalysisResults(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    result = schema.Choice(
        title=_(u"Result"),
        required=False,
        vocabulary=u"gene.tumour.vocabulary.analysis_result",
    )

    result_info = schema.TextLine(
        title=_(u"Result information"),
        required=False,
    )

    quality_file = schema.URI(
        title=_(u"Quality control document"),
        constraint=validate_url,
        required=False,
    )

    result_file = schema.URI(
        title=_(u"Result detail"),
        constraint=validate_url,
        required=False,
    )


class IAnalysisResultsEdit(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    result = schema.Choice(
        title=_(u"Result"),
        required=False,
        vocabulary=u"gene.tumour.vocabulary.analysis_result",
    )

    result_info = schema.TextLine(
        title=_(u"Result information"),
        required=False,
    )

    quality_file = field.NamedBlobFile(
        title=_(u"Quality control document"),
        required=False,
    )

    result_file = field.NamedBlobFile(
        title=_(u"Result detail"),
        required=False,
    )


class IFailedRedo(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    barcode = schema.TextLine(
        title=_(u"Barcode"),
        required=False,
        readonly=False,
    )

    name = schema.TextLine(
        title=_(u"Name"),
        required=False,
        readonly=False,
    )

    review_state = schema.TextLine(
        title=_(u"Review state"),
        required=False,
        readonly=False,
    )

    steps = schema.Choice(
        title=_(u"Steps"),
        required=True,
        vocabulary=u"gene.tumour.vocabulary.redo_steps"
    )

    changeNote = schema.TextLine(
        title=_(u'label_change_note', default=u'Change Note'),
        description=_(u'help_change_note',
                      default=u'Enter a comment that describes the changes '
                              u'you made.'),
        required=False)


class IChangeSteps(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    barcode = schema.TextLine(
        title=_(u"Barcode"),
        required=False,
        readonly=False,
    )

    name = schema.TextLine(
        title=_(u"Name"),
        required=False,
        readonly=False,
    )

    review_state = schema.TextLine(
        title=_(u"Review state"),
        required=False,
        readonly=False,
    )

    steps = schema.Choice(
        title=_(u"Steps"),
        required=True,
        vocabulary=u"gene.tumour.vocabulary.progress_steps"
    )

    changeNote = schema.TextLine(
        title=_(u'label_change_note', default=u'Change Note'),
        description=_(u'help_change_note',
                      default=u'Enter a comment that describes the changes '
                              u'you made.'),
        required=False)


class IWorkflowStateTransition(model.Schema):
    uuid = schema.TextLine(
        title=_(u"UUID"),
        required=True,
        readonly=False,
    )

    sample_no = schema.TextLine(
        title=_(u"Sample number"),
        required=False,
        readonly=False,
    )

    barcode = schema.TextLine(
        title=_(u"Barcode"),
        required=False,
        readonly=False,
    )

    name = schema.TextLine(
        title=_(u"Name"),
        required=False,
        readonly=False,
    )

    result = schema.Choice(
        title=_(u"Result"),
        required=False,
        readonly=False,
        vocabulary=u"gene.tumour.vocabulary.analysis_result",
    )

    result_info = schema.TextLine(
        title=_(u"Result information"),
        readonly=False,
        required=False,
    )

    steps = schema.Choice(
        title=_(u"Steps"),
        required=False,
        readonly=False,
        vocabulary=u"gene.tumour.vocabulary.progress_steps"
    )

    review_state = schema.TextLine(
        title=_(u"Review state"),
        required=False,
        readonly=False,
    )

    directives.widget('transition_state', RadioFieldWidget)
    transition_state = schema.Choice(
        title=_(u"State transition"),
        required=False,
        vocabulary=u"gene.tumour.vocabulary.review_states"
    )

    changeNote = schema.TextLine(
        title=_(u'label_change_note', default=u'Change Note'),
        description=_(u'help_change_note',
                      default=u'Enter a comment that describes the changes '
                              u'you made.'),
        required=False)


class IBloodSampleAddList(Interface):
    batch_list = schema.List(
        title=_(u'Blood Sample'),
        value_type=DictRow(title=u'Sample', schema=IBloodSampleAdd),
        required=True)


class IBloodSampleList(Interface):
    batch_list = schema.List(
        title=_(u'Blood Sample'),
        value_type=DictRow(title=u'Sample', schema=IBloodSample),
        required=True)


class INAExtractionList(Interface):
    batch_list = schema.List(
        title=_(u'NA Extraction'),
        value_type=DictRow(title=u'NA', schema=INAExtraction),
        required=True)


class ILibraryConstructionList(Interface):
    batch_list = schema.List(
        title=_(u'Library Construction'),
        value_type=DictRow(title=u'Library', schema=ILibraryConstruction),
        required=True)


class IComputerDetectingList(Interface):
    batch_list = schema.List(
        title=_(u'Computer Detecting'),
        value_type=DictRow(title=u'Detecting', schema=IComputerDetecting),
        required=True)


class IAnalysisResultsList(Interface):
    batch_list = schema.List(
        title=_(u'Analysis Results'),
        value_type=DictRow(title=u'Results', schema=IAnalysisResultsEdit),
        required=True)


class IFailedRedoList(Interface):
    batch_list = schema.List(
        title=_(u'Failed Redo'),
        description=_(u"Redo failed item"),
        value_type=DictRow(title=u'Redo', schema=IFailedRedo),
        required=True)


class IChangeStepsList(Interface):
    batch_list = schema.List(
        title=_(u'Change Steps'),
        description=_(u"Please select a new steps."),
        value_type=DictRow(title=u'Redo', schema=IChangeSteps),
        required=True)


class IWorkflowStateTransitionList(model.Schema):
    batch_list = schema.List(
        title=_(u'Workflow state transition'),
        description=_(u"Workflow state transition"),
        value_type=DictRow(title=u'Redo', schema=IWorkflowStateTransition),
        required=True)


class IBackupTumourForm(Interface):
    compression = schema.Bool(
        title=_(u'Data compression'),
        description=_(u'Select this option if you want the data compression '),
        default=False,
    )


class IStepsChangedEvent(IObjectEvent):
    oldSteps = Attribute(u"The old steps value for the object.")
    newSteps = Attribute(u"The new steps value for the object.")
