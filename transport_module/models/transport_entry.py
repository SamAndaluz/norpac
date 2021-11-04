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


    
class transport_entry(models.Model):
    _name = "transport.entry"
    _rec_name = 'contact_person' 

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.picking.sequence') or _('New')
        return super(transport_entry, self).create(vals)

    def move_to_start(self): 
        lines = []
        date_list = []
        self.state = 'in-progress'  
        picking_id = self.env['stock.picking'].search([('name', '=', self.picking_id.name)])
        now = self.date
        date_list.append(now)
        i = 0
        for location in self.transport_rote_ids:
            location.state = 'in-progress'
            location.start_time = date_list[i]
            time = location.time
            hours_added = timedelta(hours = time)
            if location.start_time:
                end_time = location.start_time + hours_added
                location.end_time = end_time
                date_list.append(location.end_time)
                vals = {
                        'start_time' : date_list[i],
                        'end_time' : end_time,
                        'state' : self.state,
                        'source_loc':location.source_loc.id, 
                        'dest_loc':location.dest_loc.id, 
                        'distance':location.distance,
                        'time':location.time,
                        'note': location.note,
                    }
                res= self.env['transport.location.details'].create(vals)
                lines.append(res.id)
                i +=1
        picking_id.transport_routes_ids  = [(6,0,lines)]

    def move_to_halt(self):
        lines = [] 
        date_list = []            
        self.state = 'waiting' 
        now = self.date
        date_list.append(now) 
        i = 0
        picking_id = self.env['stock.picking'].search([('name', '=', self.picking_id.name)])
        for location in self.transport_rote_ids:
            location.state = 'waiting'
            time = location.time
            location.start_time = date_list[i]
            hours_added = timedelta(hours = time)
            if location.start_time:
                end_time = location.start_time + hours_added
                location.end_time = end_time
                date_list.append(location.end_time)
                vals = {
                        'start_time' : date_list[i],
                        'end_time' : end_time,
                        'state' : self.state,
                        'source_loc':location.source_loc.id, 
                        'dest_loc':location.dest_loc.id, 
                        'distance':location.distance,
                        'time':location.time,
                        'note': location.note,
                    }
                res= self.env['transport.location.details'].create(vals)
                lines.append(res.id)
                i +=1
        picking_id.transport_routes_ids  = [(6,0,lines)]

    def move_to_done(self): 
        lines = []  
        date_list = [] 
        now = self.date           
        date_list.append(now) 
        i = 0
        picking_id = self.env['stock.picking'].search([('name', '=', self.picking_id.name)])                       
        self.state = 'done'
        for location in self.transport_rote_ids:
            location.state = 'done'
            time = location.time
            hours_added = timedelta(hours = time)
            if location.start_time:
                end_time = location.start_time + hours_added
                date_list.append(location.end_time)
                vals = {
                        'start_time' : date_list[i],
                        'end_time' : end_time,
                        'state' : self.state,
                        'source_loc':location.source_loc.id, 
                        'dest_loc':location.dest_loc.id, 
                        'distance':location.distance,
                        'time':location.time,
                        'note': location.note,
                    }
                res= self.env['transport.location.details'].create(vals)
                lines.append(res.id)
                i +=1
        picking_id.transport_routes_ids  = [(6,0,lines)]
        
    def move_to_cancel(self):
        lines = []             
        self.state = 'cancel' 
        i = 0
        picking_id = self.env['stock.picking'].search([('name', '=', self.picking_id.name)])
        for location in self.transport_rote_ids:
            time = location.time
            location.state = 'cancel'
            vals = {
                    'state' : self.state,
                    'source_loc':location.source_loc.id, 
                    'dest_loc':location.dest_loc.id, 
                    'distance':location.distance,
                    'time':location.time,
                    'note': location.note,
                }
            res= self.env['transport.location.details'].create(vals)
            lines.append(res.id)
            i +=1
        picking_id.transport_routes_ids  = [(6,0,lines)]

    def move_to_progress(self): 
        lines = []             
        self.state = 'in-progress'  
        date_list = []   
        now = self.date         
        date_list.append(now) 
        i = 0
        picking_id = self.env['stock.picking'].search([('name', '=', self.picking_id.name)])
        for location in self.transport_rote_ids:
            time = location.time
            location.state = 'in-progress'
            location.start_time = date_list[i]
            hours_added = timedelta(hours = time)
            if location.start_time:
                end_time = location.start_time + hours_added
                date_list.append(location.end_time)
                location.end_time = end_time
                vals = {
                        'start_time' : date_list[i],
                        'end_time' : end_time,
                        'state' : self.state,
                        'source_loc':location.source_loc.id, 
                        'dest_loc':location.dest_loc.id, 
                        'distance':location.distance,
                        'time':location.time,
                        'note': location.note,
                    }
                res= self.env['transport.location.details'].create(vals)
                lines.append(res.id)
                i +=1
        picking_id.transport_routes_ids  = [(6,0,lines)]

    name =  fields.Char('Name')
    date = fields.Datetime('Transport Date')
    note = fields.Text('Note')
    active = fields.Boolean('Active')
    picking_id = fields.Many2one('stock.picking', string="Delivery Order")
    customer_id = fields.Many2one('res.partner', 'Customer')
    contact_person = fields.Char('Contact Name')
    no_of_parcels = fields.Integer('No Of Parcels')
    lr_number = fields.Char('LR Number')
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle')
    sale_order = fields.Char(string='Sale Order')
    tag_ids = fields.Many2one('fleet.vehicle', copy=False, string='Transport Vehicle')
    driver_id = fields.Many2one('res.partner', 'Vehicle Driver')
    state =  fields.Selection([('draft', 'Start'),('waiting','Waiting'),('in-progress', 'In-Progress'),('done','Done'),('cancel','Cancel'),
                                  ], default =  'draft', copy = False)        
    transport_id = fields.Many2one('transport', 'Transporter Name')
    transport_rote_ids  = fields.One2many('transport.location.details', 'transport_entry_id')
    user_id = fields.Many2one('res.users', string='Responsible User', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.user.company_id)
    note = fields.Text('Note')


            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
