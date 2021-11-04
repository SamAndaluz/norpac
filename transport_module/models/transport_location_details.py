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



class transport_location_details(models.Model):

    _name = 'transport.location.details'

    source_loc = fields.Many2one('route.locations', 'Source Location')
    dest_loc  = fields.Many2one('route.locations','Destination Location')
    distance = fields.Float('Distance (KM)')
    time   = fields.Float('Time in Hours')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    note  = fields.Char('Comment')
    tracking_number  =  fields.Char('Tracking Number')
    picking_id = fields.Many2one('stock.picking')
    transport_entry_id = fields.Many2one('transport.entry')
    route_id = fields.Many2one('transport.route', 'Route Of Transportation')
    state = fields.Selection([('draft', 'Start'), ('waiting','Waiting'),('in-progress', 'In-Progress'), ('done', 'Done'),('cancel','Cancel')] , 'State',default='draft')
    transport_charge = fields.Float(string='Transport Charges', compute='onchange_charges')

    @api.depends('distance')
    def onchange_charges(self):
        for i in self:
            Charges = i.route_id.transporter_id.transport_charge * i.distance
            i.transport_charge = Charges

    @api.model
    def create(self,values):
        res = super(transport_location_details,self).create(values)
        if res.distance == 0.0 or res.time == 0.0:
            raise UserError(_('Distance and Time must be greater than zero.'))
        return res

    def write(self,values):
        res = super(transport_location_details,self).write(values)
        for i in self:
            if i.distance == 0.0 or i.time == 0.0:
                raise UserError(_('Distance and Time must be greater than zero.'))
        return res


            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
