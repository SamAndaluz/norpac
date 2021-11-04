# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import base64
from datetime import datetime,date,timedelta
from odoo.tools import ustr
from io import StringIO
import io
from odoo.exceptions import UserError, Warning
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

try:
    import xlwt
except ImportError:
    xlwt = None


class transport_entry_report_wizard(models.TransientModel):
    _name = "transport.entry.wizard"
    
    start_date = fields.Date('Date')
    trasporter_id  =  fields.Many2one('transport', 'Select Transporter')

    def print_excel_report(self):
        res={}
        object_of_transport_entry = self.env['transport.entry']
        
        date  = str(self.start_date)
        transport_id  = self.trasporter_id.name
        
        company_name = self.env['res.users'].browse(self.env.uid).company_id.name
        
        company_address = self.env['res.users'].browse(self.env.uid).company_id.street or  '' + "," + self.env['res.users'].browse(self.env.uid).company_id.street2 or  ''
        company_city =  self.env['res.users'].browse(self.env.uid).company_id.city
        company_state =  self.env['res.users'].browse(self.env.uid).company_id.state_id.name
        company_country = self.env['res.users'].browse(self.env.uid).company_id.country_id.name

        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        style2 = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') 

        # Create a font to use with the style
        font = xlwt.Font()
        font.name = 'calibri'
        font.bold = True
        font.height = 200
        style.font = font
        index = 1

        #simple font
        font2 = xlwt.Font()
        font2.name = 'Bitstream Charter'
        font2.bold = False
        font2.height = 200
        style2.font = font2
        index = 1

        #company Address
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write(0, 0, company_name , style)
        worksheet.write(2, 0, company_city , style)
        worksheet.write(3, 0, company_state , style)
        worksheet.write(4, 0, company_country , style)

        #transporter and date start deatils
        
        worksheet.write(7, 0, 'Transporter' , style)
        worksheet.write(7, 1,  transport_id, style2)  
        
        worksheet.write(7, 4, 'Date' , style)
        worksheet.write(7, 5, date  , style2) 

        if self.trasporter_id.id and self.start_date:
            records = self.env['transport.entry'].search([('transport_id','=',self.trasporter_id.id),('date','<=',self.start_date),('date','>=',self.start_date)])
            sr_no  = 1
            findal_list_of_data  = []

            worksheet.write(10, 0, 'Order #', style)
            worksheet.write(10, 1, 'Customer', style)
            worksheet.write(10, 2, 'Customer Address', style)
            worksheet.write(10, 3, 'Delivery No.', style)
            worksheet.write(10, 4, 'No. of Parcel', style)
            worksheet.write(10, 5, 'Lr No.', style)
            worksheet.write(10, 6, 'Vehicle', style)
            worksheet.write(10, 7, 'Status', style)
            worksheet.write(10, 8, 'Note', style)
            note_list = []
            count = 0
            for rec in records:
                if self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street != False and  self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street2 != False:
                    partner_address = str(self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street)  + ","+ str(self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street2) or  ''
                elif self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street == False and  self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street2 != False: 
                    partner_address = str(self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street2) or  ''
                elif self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street != False and  self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street2 == False: 
                    partner_address = str(self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street) or  ''
                elif self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street == False and  self.env['stock.picking'].browse(rec['picking_id'].id).partner_id.street2 == False: 
                    partner_address = ''
                if rec['note'] != False:
                    note_list.append(rec['note'])
                else:
                    note_list.append('')
                data_dict  =  {'order_no' : sr_no ,
                           'customer_id': self.env['res.partner'].browse(rec['customer_id'].id).name,
                            'Address':partner_address,
                            'picking_number': self.env['stock.picking'].browse(rec['picking_id'].id).name,
                            'no_of_parcel':self.env['stock.picking'].browse(rec['picking_id'].id).no_of_parcels,
                            'status':rec['state'],
                            'vehicle':rec['tag_ids'].name,
                            'note':note_list[count],
                            'lr_no': self.env['stock.picking'].browse(rec['picking_id'].id).lr_number,
                            }    

                sr_no =  sr_no + 1
                findal_list_of_data.append(data_dict) 
                count = count+1
                
            #heading 
            row  = 11
            for vals in findal_list_of_data:
                worksheet.write(row, 0, ustr(vals['order_no']))
                worksheet.write(row, 1, ustr(vals['customer_id']))
                if vals['Address'] == str(False):
                   vals['Address'] = ''
                worksheet.write(row, 2, ustr(vals['Address']))
                worksheet.write(row, 3, ustr(vals['picking_number']))
                worksheet.write(row, 4, ustr(vals['no_of_parcel']))
                worksheet.write(row, 5,ustr(vals['lr_no']))
                worksheet.write(row, 6,ustr(vals['vehicle']))
                worksheet.write(row, 7,ustr(vals['status']))
                worksheet.write(row, 8,ustr(vals['note'])) 
        
                row = row + 1 

        filename = 'Transport_Daily_Report.xls'        
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['daily.taransport.report.excel'].create( {'excel_file': base64.encodestring(fp.getvalue()),'file_name': filename})
        
        res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'daily.taransport.report.excel',
                'type': 'ir.actions.act_window',
                'target':'new'
        }
        return res


            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
