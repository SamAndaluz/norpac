# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

class transport_reports_details_1(models.AbstractModel):
    _name='report.transport_module.transport_reports_details_1'

    def _get_detail(self, obj):
        
        transport_obj = self.env['transport']
        partner_obj = self.env['res.partner']
        picking_obj = self.env['stock.picking']
        t_name=[]
        t_add=[]
        c_name=[]
        c_add=[]
        lr=[]
        nop=[]
        d_name=[]
        address=''
        self.env.cr.execute('''select transport_id,lr_number,no_of_parcels,customer_id,picking_id from transport_entry where
                   date <= '%s' and transport_id is not null and active = True
                    ''' % (obj.start_date))
        result = self.env.cr.dictfetchall()
        name = ''
        for i in result:
            if i['lr_number'] == None:
                lr.append(' ')
            else:
                lr.append(i['lr_number'])
            if i['no_of_parcels'] == None:
                nop.append(' ')
            else:
                nop.append(i['no_of_parcels'])
            if i.get('transport_id') != None:
                self.env.cr.execute('''select name,street,street2 from transport where id = %s''' %(i.get('transport_id')))
                tname=self.env.cr.dictfetchall()
            for t in tname:
                t_name.append(t['name'])
                if t['street']==None or t['street2']== None :
                    address=''
                else:
                    address +=t['street']
                    address +=t['street2']
                t_add.append(address)
            self.env.cr.execute('''select name,street,street2,city from res_partner where id = %s''' %(i.get('customer_id')))
            
            cname=self.env.cr.dictfetchall()
            for c in cname:
                c_name.append(c['name'])
                if c['street']==None or c['street2']== None or c['city']==None:
                    address=''
                else:
                    address +=c['street']
                    address +=c['street2']
                c_add.append(address)
            self.env.cr.execute('''select name from stock_picking where id = %s''' %(i.get('picking_id')))
            dname=self.env.cr.dictfetchall()
            for c in dname:
                d_name.append(c['name'])

        final=[{'tname':t_name,'trans_add':t_add,'customer':c_name,'customer_address':c_add,'delivery_no':d_name,'nop':nop,'lr':lr}]
        return final

    @api.model
    def _get_report_values(self, docids, data=None):
        payment = self.env['transport.entry.wizard'].browse(docids)
        return {
            
            'doc_ids': docids,
            'doc_model': 'transport.entry.wizard',
            'docs': payment,
         'get_details':self._get_detail                                                                                                                             ,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
