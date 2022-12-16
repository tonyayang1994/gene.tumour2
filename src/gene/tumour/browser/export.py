# -*- coding: utf-8 -*-

import datetime
import logging
import os
import random
from StringIO import StringIO
from collections import Counter

import xlrd
import xlwt
from Products.Five.browser import BrowserView
from gene.common.utils import set_headers
from gene.common.utils import stream_data
from gene.tumour import utils
from plone import api

logger = logging.getLogger(__name__)


class ExportExcel(BrowserView):

    def __init__(self, context, request):
        super(ExportExcel, self).__init__(context, request)
        self.request['disable_border'] = True

    def export_items(self):

        uuids = self.request.get('uuids', '')
        uuids = uuids and uuids.split(',') or []

        query = dict()
        query['sort_on'] = 'created'
        query['sort_order'] = 'desc'
        query['sort_limit'] = len(uuids)
        query['portal_type'] = 'Tumour'
        query['UID'] = uuids

        items = api.content.find(**query)
        file_obj = self.create_excel(items)
        set_headers(self.request.response,
                    file_obj,
                    'genetumour_sheet_export-{0}.xls'.format(
                        datetime.datetime.now()))
        return stream_data(file_obj)

    def export_dilution(self):

        uuids = self.request.get('uuids', '')
        uuids = uuids and uuids.split(',') or []

        query = dict()
        query['sort_on'] = 'created'
        query['sort_order'] = 'desc'
        query['sort_limit'] = len(uuids)
        query['portal_type'] = 'Tumour'
        query['UID'] = uuids

        items = api.content.find(**query)
        file_object = self.create_dilution(items)
        set_headers(self.request.response,
                    file_object,
                    'genetumour_sheet_dilution-{0}.xls'.format(
                        datetime.datetime.now()))
        return stream_data(file_object)

    def create_excel(self, items=list()):
        can_review = api.user.has_permission(
            'Review portal content', obj=self.context)

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(u'Sheet1')

        for index, value in enumerate(utils.export_fields_title()):
            sheet.write(0, index, value)

        fields_review = []
        for row, obj in enumerate(items):
            real_object = obj.getObject()
            i = 0
            for col, name in enumerate(utils.fields_name()):
                if not can_review and name in fields_review:
                    value = ''
                elif name == "result_file":
                    value = ''
                else:
                    value = getattr(real_object, name, None)
                    if value and isinstance(value, datetime.date):
                        try:
                            value = api.portal.get_localized_time(
                                value, long_format=True)
                        except ValueError:
                            pass
                sheet.write(row + 1, col, value)
                i += 1
            sheet.write(row + 1, i, api.portal.translate(obj.review_state,lang='zh_CN'))
            
        file_obj = StringIO()
        workbook.save(file_obj)
        return file_obj

    def create_dilution(self, items=list()):

        curdir = os.path.dirname(__file__)
        sep = os.path.sep

        filename = '{0}{1}templates{2}genetumour-dilution-template.xls'.format(
            curdir, sep, sep)

        workbook_src = xlrd.open_workbook(
            filename=filename, formatting_info=True)
        sheet_src = workbook_src.sheet_by_index(0)

        workbook_dst = xlwt.Workbook()
        sheet = workbook_dst.add_sheet(u'Sheet1')

        for row_index in range(0, 5):
            row_value = sheet_src.row_values(row_index)
            for col_index, value in enumerate(row_value):
                sheet.write(row_index, col_index, value)

        row_buffer = []
        library_barcode_buffer = []
        for row, obj in enumerate(items):
            line_no = 5 + 1 + row
            real_object = obj.getObject()
            row_value = list()
            row_value.append(row + 1)
            row_value.append(getattr(real_object, 'sample_no', ''))
            row_value.append(getattr(real_object, 'barcode', ''))
            library_barcode = getattr(real_object, 'library_barcode', '')
            row_value.append(library_barcode)
            library_barcode_buffer.append(library_barcode)
            row_value.append(getattr(real_object, 'library_concentration', 0))
            row_value.append(
                xlwt.Formula("(E{0} * 10000000) / (660 * 260)".format(
                    line_no)))
            row_value.append(3)
            row_value.append(
                xlwt.Formula("($F${0} - 1) * $G${1}".format(line_no, line_no)))

            row_buffer.append(row_value)

        counter = Counter(library_barcode_buffer)
        counter = {key: random.choice(xlwt.Style.colour_map.keys())
                   for key in counter if counter[key] > 1}

        for row_index, row_value in enumerate(row_buffer):
            for col, value in enumerate(row_value):
                params = {'r': 5 + row_index, 'c': col, 'label': value}
                if col == 3 and row_value[3] in counter:
                    style = xlwt.easyxf(
                        'pattern: pattern solid, fore_colour {0};'.format(
                            counter[row_value[3]]))
                    params['style'] = style
                sheet.write(**params)

        for row_index, row_src in enumerate(range(22, 26)):
            row_value = sheet_src.row_values(row_src)
            for col_index, value in enumerate(row_value):
                sheet.write(5 + len(items) + row_index, col_index, value)

        # from xlutils.styles import Styles
        # workbook.save('items_sheet_export.xls')
        # styles = Styles(workbook_src)
        # from xlutils.copy import copy
        # wb = copy(workbook_src)
        # sheet = wb.get_sheet(0)
        # wb.save(file_obj)
        file_obj = StringIO()
        workbook_dst.save(file_obj)
        return file_obj
