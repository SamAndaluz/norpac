# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import base64
from odoo.tools import consteq, plaintext2html
from odoo.addons.website.controllers.main import QueryURL
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import groupby as groupbyelem
from operator import itemgetter

class PortalTransport(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalTransport, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        user = request.env.user
        transport_obj = request.env['transport.entry']
        transport_count = transport_obj.search_count(['|',('user_id','=',user.id),('picking_id.partner_id','=',partner.id)])
        values.update({
            'transport_count': transport_count,
        })
        return values

    def _get_search_transport(self, post):
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        return '%s ,id desc' % post.get('transport_ftr','write_date desc')

    def _get_search_transport_domain(self, search):
        domain = []
        if search:
            for srch in search.split(" "):
                domain = [('name', 'ilike', srch)]
        return domain

    @http.route(['/my/transport_details', '/my/transport_details/page/<int:page>'], type='http', auth="user", website=True)
    def portal_transport_list(self, page=1, date_begin=None, date_end=None, sortby=None, search="", **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        user = request.env.user
        transport_details = request.env['transport.entry']

        domain = self._get_search_transport_domain(search)
        keep = QueryURL('/my/transport_details' , search=search, order=kw.get('order'))
        domain += ['|',('user_id','=',user.id),('picking_id.partner_id','=',partner.id)]
        # count for pager
        repair_count = transport_details.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/transport_details",
            total=repair_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        partner = request.env.user.partner_id
        if kw.get('trans_filter') == "filter all":
            domain += [] 
            
        if kw.get('trans_filter') == "Today":
            current_date = date.today()
            Previous_Date = date.today() + timedelta(days=1)
            domain += [('date','>=',current_date),('date','<',Previous_Date)]

        if kw.get('trans_filter') == "Draft":
            domain += [('state','=','draft')]

        if kw.get('trans_filter') == "Waiting":
            domain += [('state','=','waiting')]

        if kw.get('trans_filter') == "In-Progress":
            domain += [('state','=','in-progress')]

        if kw.get('trans_filter') == "Done":
            domain += [('state','=','done')]

        if kw.get('trans_filter') == "Cancel":
            domain += [('state','=','cancel')] 

        transport = request.env['transport.entry'].sudo().search(domain, order=self._get_search_transport(kw))

        if kw.get('trans_group') == "status":
            grouped_transport = [request.env['transport.entry'].concat(*g) for k, g in groupbyelem(transport, itemgetter('state'))]
        elif kw.get('trans_group') == "responsible":
            grouped_transport = [request.env['transport.entry'].concat(*g) for k, g in groupbyelem(transport, itemgetter('user_id'))]
        elif kw.get('trans_group') == "vehicle":
            grouped_transport = [request.env['transport.entry'].concat(*g) for k, g in groupbyelem(transport, itemgetter('tag_ids'))]        
        else:
            grouped_transport = [transport]
        if transport:
            values.update({
                'transport': transport,
                'page_name': 'transport_details',
                'grouped_transport' : grouped_transport,
                'pager': pager,
                'groupby': kw.get('trans_group'),
                'default_url': '/my/transport_details',
                'keep' : keep,
            })
        else:
            values.update({
                'transport': transport,
                'page_name': 'transport_details',
                'grouped_transport' : grouped_transport,
                'pager': pager,
                'groupby': kw.get('trans_group'),
                'default_url': '/my/transport_details',
                'keep' : keep,
                'khush' : 'khush'
            })
        
        return request.render("bi_web_transport_portal.portal_transport_list", values)

    @http.route(['/transport/view/detail/<model("transport.entry"):transport>'],type='http',auth="public",website=True)
    def transport_view(self, transport,report_type=None, category='', search='',access_token=None, download=False, **kwargs):
        context = dict(request.env.context or {})
        transport_obj = request.env['transport.entry']
        
        context.update(active_id=transport.id)
        transport_list = []
        transport_data = transport_obj.browse(int(transport))
        for items in transport_data:
            transport_list.append(items)

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=transport_data, report_type=report_type, report_ref='transport_module.transport_entry_report', download=download)
            
        return http.request.render('bi_web_transport_portal.transport_portal_template',{
            'transport_list': transport,
            'report_type': 'html',
            'force_refresh': True,
            'redirect_url': transport_data.get_portal_url(),
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
