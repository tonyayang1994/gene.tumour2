# -*- coding: utf-8 -*-
import json
import logging

from gene.common.utils import date_handler
from gene.tumour import utils
from gene.tumour.events import StepsChangedEvent
from gene.tumour.interfaces import IAnalysisResults
from plone import api
from plone.api.exc import InvalidParameterError
from plone.api.exc import MissingParameterError
from zope import schema
from zope.event import notify
from zope.lifecycleevent import modified
from zope.publisher.browser import BrowserView
from zope.schema import getFieldNamesInOrder

logger = logging.getLogger(__name__)


class ReturnData(object):
    pass


class JsonRPC(BrowserView):

    def pull_data(self):
        query = dict()
        query['portal_type'] = 'Tumour'
        query['sort_on'] = 'created'
        query['sort_order'] = 'ascending'
        query['steps'] = 'step4'
        query['review_state'] = 'private'

        raw_result = api.content.find(**query)
        data = []
        for item in raw_result:
            real_obj = item.getObject()
            record = {}
            for name in utils.fields_name():
                record[name] = getattr(real_obj, name, None)
            record['uuid'] = real_obj.UID()
            record['gid'] = real_obj.gid
            record['id'] = real_obj.id
            record['review_state'] = item.review_state
            data.append(record)
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(data, default=date_handler)

    def push_data(self):
        data = self.request.get('json', '[]')
        data_list = json.loads(data)
        names = getFieldNamesInOrder(IAnalysisResults)
        names.remove('uuid')
        names.remove('sample_no')
        success_count = 0

        for entry in data_list:
            return_obj = ReturnData()
            [setattr(return_obj, key, entry[key]) for key in entry]
            errors = schema.getValidationErrors(IAnalysisResults, return_obj)

            if errors:
                msg = []
                for error in errors:
                    error_type = error[1].__class__.__name__
                    field_value = unicode(error[1])
                    err = u'{0}: {1}; '.format(error_type, field_value)
                    msg.append(err)
                msg = ''.join(msg)
                entry.update(dict(_back_success=False, _back_message=msg))
                logger.warn(msg)
                continue
            else:
                uuid = entry['uuid']
                obj = api.content.uuidToObject(uuid)
                if obj:
                    [setattr(obj, k, entry[k]) for k in entry if k in names]
                    old_steps = obj.steps
                    new_steps = u'step5'
                    obj.steps = new_steps
                    notify(StepsChangedEvent(obj, old_steps, new_steps))
                    modified(obj)
                    try:
                        api.content.transition(obj=obj, transition='submit')
                    except (MissingParameterError,
                            InvalidParameterError) as error:
                        msg = 'Warning, {0}'.format(str(error))
                        logger.warn(error)
                    else:
                        msg = 'Success.'
                    success_count += 1
                    entry.update(dict(_back_success=True, _back_message=msg))
                else:
                    msg = u'Warning, ' \
                          u'uuid "{0}" not found, skipping.'.format(uuid)
                    entry.update(dict(_back_success=False, _back_message=msg))
                    logger.warn(msg)

        failed_count = len(data_list) - success_count
        msg = u'Analysis of Results: {0} Item Succeeded, ' \
              u'{1} Item Failed.'.format(success_count, failed_count)
        logger.info(msg)
        return json.dumps(data_list)
