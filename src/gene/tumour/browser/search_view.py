# -*- coding: utf-8 -*-
import json
import logging
import urllib

from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from gene.common.utils import date_handler
from gene.tumour import _
from gene.common.utils import DateTime2localTime
from gene.tumour import utils
from gene.tumour.vocabulary import situation_dict, result_dict
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.batching import Batch
from plone.memoize import view
from zope.i18n import translate
from zope.publisher.browser import BrowserView
from Products.CMFPlone.resources import add_bundle_on_request

logger = logging.getLogger(__name__)


class SearchView(BrowserView):

    def __init__(self, context, request):

        self.context = context
        self.request = request
        add_bundle_on_request(self.request, 'gene-tumour-main')

    def __call__(self, *args, **kw):
        self.request['disable_border'] = True

        bulkaction = self.request.get('bulk_action', '')
        if bulkaction == 'delete':
            self.delete()

        return self.index()

    def delete(self):
        can_review = api.user.has_permission(
            'Review portal content', obj=self.context)
        if not can_review:
            raise Unauthorized

        uuids = self.request.get('uuids', '')
        uuids = uuids and uuids.split(',') or []

        for uuid in uuids:
            item = api.content.uuidToObject(uuid)
            if item:
                api.content.delete(item)
                logger.info('Delete tumour {0}'.format(item))

    @view.memoize
    def fields_name_title(self):

        split_point = 3
        step5_start, step5_end = utils.steps_start_end[4]

        fields_name = utils.fields_name()[-1:]
        fields_name += ['review_state']
        fields_name += utils.fields_name()[:split_point]
        fields_name += utils.fields_name()[step5_start:step5_end]
        fields_name += utils.fields_name()[split_point:step5_start]

        fields_title = utils.fields_title()[-1:]
        fields_title += [translate(_('Review state'), context=self.request)]
        fields_title += utils.fields_title()[:split_point]
        fields_title += utils.fields_title()[step5_start:step5_end]
        fields_title += utils.fields_title()[split_point:step5_start]

        return zip(fields_name, fields_title)

    def table_data(self):
        indexes = api.portal.get_tool('portal_catalog').indexes()

        b_size = int(self.request.form.get('length', 10))
        b_start = int(self.request.form.get('start', 0))
        sort_on = self.request.get('order[0][column]', 0)
        sort_on = self.request.get('columns[{0}][data]'.format(sort_on),
                                   'created')
        sort_on = sort_on in indexes and sort_on or 'created'
        sort_order = self.request.get('order[0][dir]', 'desc')
        sort_order = sort_order == 'asc' and 'ascending' or 'descending'
        sort_limit = self.request.get('sort_limit', 300)

        searchable_text = self.request.form.get('search[value]', '')
        searchable_text = safe_unicode(searchable_text)
        search_field = self.request.get('search_field', '')
        search_date = self.request.get('search_date', '')
        date_from = self.request.get('date_from', '')
        date_to = self.request.get('date_to', '')

        query = dict()
        query['b_size'] = b_size
        query['b_start'] = b_start
        query['sort_on'] = sort_on
        query['sort_order'] = sort_order
        query['sort_limit'] = sort_limit
        query['portal_type'] = 'Tumour'

        query['path'] = {
            'query': '/'.join(self.context.getPhysicalPath()),
            'depth': -1}

        if search_field in ('task_no', 'sequencing_filename'):
            query[search_field] = searchable_text
        else:
            query['SearchableText'] = searchable_text
            if search_field in utils.progress_steps:
                query['steps'] = search_field
            elif search_field in utils.review_states:
                query['review_state'] = search_field
            else:
                search_words = searchable_text.lower().split()
                if search_words > 1:
                    operators = ('and', 'or', 'not', '(', ')')
                    if not any(map(lambda val: val in search_words, operators)):
                        searchable_text = u' OR '.join(search_words)
                        query['SearchableText'] = searchable_text

        if search_date in ('sampling_time', 'received_time',
                           'separation_time', 'extraction_time',
                           'library_time', 'template_time',
                           'sequencing_time',
                           'created', 'modified'):
            try:
                start_date = DateTime(date_from)
            except:
                start_date = DateTime('1970-01-01')
            try:
                end_date = DateTime(date_to)
            except:
                end_date = DateTime()
            query[search_date] = {
                'query': sorted([start_date, end_date]),
                'range': 'min:max'}

        try:
            user_search_filter = api.portal.get_registry_record(
                'gene.tumour.interfaces.IGeneTumourSettings.'
                'user_search_filter')
        except Exception as e:
            user_search_filter = []
            logger.warn(e)
        if not isinstance(user_search_filter, (list, tuple)):
            user_search_filter = []
        current_user = api.user.get_current()
        for group in user_search_filter:
            users = api.user.get_users(groupname=group)
            if current_user in users:
                searchable_text += ' '
                searchable_text += safe_unicode(user_search_filter[group])

        results = api.content.find(**query)
        results = IContentListing(results)
        results = Batch(results, size=b_size, start=b_start)

        can_review = api.user.has_permission(
            'Review portal content', user=current_user, obj=self.context)
        can_changenote = api.user.has_permission(
            'gene.tumour: Change Note', user=current_user, obj=self.context)
        rows = []

        for item in results:
            obj = item.getObject()
            record = {}
            for name, value in utils.fields():
                if value.__class__.__name__ in ('NamedBlobImage',
                                                'NamedBlobFile'):
                    record[name] = [self.display_url(obj, name),
                                    self.download_url(obj, name)]
                else:
                    record[name] = getattr(obj, name, None)
            record['created'] = DateTime2localTime(obj.created())
            record['modified'] = DateTime2localTime(obj.modified())
            record['report'] = getattr(obj.aq_explicit, 'report', None)
            record['url'] = obj.absolute_url_path()
            state = api.content.get_state(obj)
            record['review_state'] = translate(
                _(state.title()),
                context=api.portal.getRequest())
            if record['result'] in result_dict:
                record['result'] = translate(
                    _(result_dict[record['result']]),
                    context=api.portal.getRequest())

            if record['treatment_situation']:
                record['treatment_situation'] = u','.join(
                    [translate(_(situation_dict[item]),
                               context=api.portal.getRequest())
                     for item in record['treatment_situation']
                     if item in situation_dict])
            record['can_versions'] = can_review
            record['can_changenote'] = can_changenote
            record['DT_RowId'] = obj.UID()
            record['DT_RowClass'] = '{0} {1}'.format(obj.steps, state)
            record['DT_RowData'] = dict()
            record['DT_RowData']['id'] = obj.id
            record['DT_RowData']['uuid'] = obj.UID()
            record['DT_RowData']['gid'] = obj.gid
            record['DT_RowData']['steps'] = obj.steps
            record['DT_RowData']['url'] = obj.absolute_url()
            record['DT_RowData']['result'] = getattr(obj, 'result', None)
            record['DT_RowData']['library_barcode'] = getattr(
                obj, 'library_barcode', None)
            record['steps'] = translate(
                _(obj.steps), context=self.request)
            if not can_review:
                pass
            rows.append(record)

        table_data = dict()
        table_data['draw'] = int(self.request.form.get('draw', 1))
        table_data['recordsTotal'] = len(results)
        table_data['recordsFiltered'] = len(results)
        table_data['data'] = rows

        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename={0}'.format('filename.json'))
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(table_data, default=date_handler)

    def filename_encoded(self, field_obj):
        filename = getattr(field_obj, 'filename')
        if filename is None:
            return None
        else:
            if isinstance(filename, unicode):
                filename = filename.encode('utf-8')
            return urllib.quote_plus(filename)

    def download_url(self, obj, field_name):
        field_obj = getattr(obj, field_name)
        if field_obj is None:
            return None
        filename = self.filename_encoded(field_obj)
        if self.filename_encoded(field_obj):
            return "%s/@@download/%s/%s" % (
                obj.absolute_url(), field_name, filename)
        else:
            return "%s/@@download/%s" % (
                obj.absolute_url(), field_name)

    def display_url(self, obj, field_name):
        field_obj = getattr(obj, field_name)
        if field_obj is None:
            return None
        filename = self.filename_encoded(field_obj)
        if self.filename_encoded(field_obj):
            return "%s/@@display-file/%s/%s" % (
                obj.absolute_url(), field_name, filename)
        else:
            return "%s/@@display-file/%s" % (
                obj.absolute_url(), field_name)
