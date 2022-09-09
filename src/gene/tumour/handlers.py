# -*- coding: utf-8 -*-
import logging
from email.mime.text import MIMEText

from DateTime import DateTime
from gene.tumour import _
from plone import api
from plone.stringinterp.interfaces import IStringInterpolator
from zope.component import ComponentLookupError
from zope.component import createObject
from zope.globalrequest import getRequest
from zope.i18n import translate

logger = logging.getLogger(__name__)


def workflow_action(event):
    try:
        sms_notify = api.portal.get_registry_record(
            'gene.tumour.interfaces.IGeneTumourSettings.'
            'sms_notify_enabled')
    except Exception as error:
        sms_notify = False
        logger.warn(error)

    if sms_notify:
        obj = event.object
        if event.action == 'success' and obj.portal_type == 'Tumour':
            phone = getattr(obj, 'patient_phone', None)
            try:
                message = api.portal.get_registry_record(
                    'gene.tumour.interfaces.IGeneTumourSettings.'
                    'sms_notify_message').strip()
                interpolator = IStringInterpolator(obj)
                message = interpolator(message)
            except Exception as error:
                logger.warn(error)
                return

            try:
                websms = createObject(u'gene.sms.websms')
            except ComponentLookupError as error:
                logger.warn(str(error))
            else:
                if phone and message:
                    response = websms.send_msg(to=phone, message=message)
                    logger.debug(response)


def check_record_expiration():
    request = getRequest()
    try:
        notification_enabled = api.portal.get_registry_record(
            'gene.tumour.interfaces.IGeneTumourSettings.'
            'email_notify_enabled')
    except Exception as e:
        notification_enabled = False
        logger.warn(e)
    if not notification_enabled:
        return

    try:
        expiration_usergourp = api.portal.get_registry_record(
            'gene.tumour.interfaces.IGeneTumourSettings.'
            'record_expire_notify')
    except Exception as e:
        expiration_usergourp = {}
        logger.warn(e)
    if not expiration_usergourp:
        return

    try:
        expire_days = api.portal.get_registry_record(
            'gene.tumour.interfaces.IGeneTumourSettings.'
            'record_expire_days')
    except Exception as e:
        expire_days = 0
        logger.warn(e)
    if not isinstance(expire_days, int) or not expire_days:
        return

    query = dict()
    query['portal_type'] = 'Tumour'
    query['review_state'] = {'query': ('private', 'pending'),
                             'operator': 'or'}
    query['sampling_time'] = {'query': [DateTime() - 60,
                                        DateTime() - expire_days],
                              'range': 'min:max'}
    query['sort_on'] = 'sampling_time'
    query['sort_order'] = 'desc'
    query['sort_limit'] = 500
    items = api.content.find(**query)
    if items:
        warn = translate(_(u'Warn'), context=request)
        subject = translate(
            _(u'[${warn}] [Tumour] ${count} items Expiration Notification',
              mapping={'warn': warn, 'count': len(items)}), context=request)

        sample_title = translate(_(u'Sample number'), context=request)
        bar_title = translate(_(u'Barcode'), context=request)
        steps_title = translate(_(u'Steps'), context=request)
        state_title = translate(_(u'State'), context=request)
        sampling_title = translate(_(u"Sampling time"), context=request)
        received_title = translate(_(u"Received time"), context=request)
        modify_time = translate(_(u"Modify time"), context=request)

        title = ('NO.', sample_title, bar_title, steps_title,
                 state_title, sampling_title, received_title, modify_time)

        table = list()
        table.append(
            u'<p style="font-size:14px; font-family:verdana; margin:0 0 10px;'
            u' line-height:22px; text-align:left">{}</p>'.format(subject))
        table.append(u"""<style>
        table {
            border-collapse: collapse;
            border-spacing: 0;
            border-left: 1px solid #C1D9F3;
            border-top: 1px solid #C1D9F3;
            font-size:14px;
        }

        th, td {
            border-right: 1px solid #C1D9F3;
            border-bottom: 1px solid #C1D9F3;
            padding: 5px 10px;
        }

        /*th {
            font-weight: bold;
            background: #ccc;
        }*/

        tr:nth-child(2n+1) {
            background-color: #EFF5FB;
        }

        tr:first-child, tr:last-child {
            background-color: #C1D9F3;
        }
        </style>""")
        table.append(u'<table cellpadding="0" cellspacing="0" border="0"'
                     u'style="border-collapse:collapse; margin:0 0 10px" >')

        td = map(lambda val: u'<th>{0}</th>'.format(val), title)
        head_foot = u'<tr>{0}</tr>'.format(u''.join(td))
        head_foot = head_foot.replace(
            u'<th>',
            u'<th style="font-size:14px;font-weight:bold;padding:5px 10px;'
            u'border:1px solid #C1D9F3; background:#C1D9F3">')
        table.append(head_foot)

        row_template = u'<tr>' \
                       u'<td>{line_number}</td>' \
                       u'<td>{0.sample_no}</td>' \
                       u'<td>{0.barcode}</td>' \
                       u'<td>{steps_value}</td>' \
                       u'<td>{review_state}</td>' \
                       u'<td>{sampling_time}</td>' \
                       u'<td>{received_time}</td>' \
                       u'<td>{modified}</td>' \
                       u'</tr>'

        for index, item in enumerate(items, start=1):
            obj = item.getObject()
            state = api.content.get_state(obj)
            row = row_template.format(
                item,
                line_number=index,
                bar_title=bar_title,
                steps_value=translate(_(item.steps), context=request),
                review_state=translate(_(state.title()), context=request),
                sampling_time=obj.sampling_time,
                received_time=obj.received_time,
                modified=api.portal.get_localized_time(
                    item.modified, long_format=True))
            if index % 2:
                row = row.replace(
                    u'<td>',
                    u'<td style="font-size:14px;text-align:center; '
                    u'padding:5px 15px; border:1px solid #C1D9F3">')
            else:
                row = row.replace(
                    u'<td>',
                    u'<td style="font-size:14px;text-align:center; '
                    u'padding:5px 15px; border:1px solid #C1D9F3;'
                    u'background:#EFF5FB;">')
            table.append(row)

        table.append(head_foot)
        table.append(u'</table>')
        msg_text = u''.join(table)
        msg_text = u'{}<hr/>{}'.format(
            msg_text.replace(u'style=', u'data-style='), msg_text)
        message = MIMEText(msg_text, 'html', 'utf-8')

        users = api.user.get_users(groupname=expiration_usergourp)
        recipient = [user.getProperty('email') for user in users]
        try:
            api.portal.send_email(
                recipient=','.join(recipient),
                subject=subject,
                body=message.as_string(),
            )
        except Exception as e:
            log = logging.getLogger('MailDataManager')
            log.exception(e)
