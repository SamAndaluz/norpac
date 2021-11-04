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

class transport(models.Model):

    _name = 'transport'

    name = fields.Char('Name')
    contact_name = fields.Char('Contact Name')
    street = fields.Char('street')
    street2 = fields.Char('street2')
    phone = fields.Char('Phone')
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle',compute="get_vehicles")
    comment = fields.Text('Comment')
    image =  fields.Binary('Transporters Image')
    imgsm = fields.Binary("Image of transport", attachment=True)
    image_medium = fields.Binary("Image", attachment=True)
    calculate_vehicles = fields.Integer(string="Vehicles",compute="vehicles_count",copy=False)
    calculate_invoice = fields.Integer(string="Delivery",compute="invoice_count",copy=False)
    state_id = fields.Many2one('res.country.state',string="State")
    country_id = fields.Many2one('res.country',string="Country")
    transport_charge = fields.Float(string='Transport Charges')

    @api.model
    def create(self, vals):

        return super(transport, self).create(vals)

    def write(self, vals):

        return super(transport, self).write(vals)

    def vehicle_record(self):
        tree_id = self.env.ref('fleet.fleet_vehicle_view_tree').id
        form_id = self.env.ref('fleet.fleet_vehicle_view_form').id
        kanban_id = self.env.ref('fleet.fleet_vehicle_view_kanban').id
        return {'type': 'ir.actions.act_window',
                'name':_('Vehicles'),
                'res_model':'fleet.vehicle',
                'view_mode':'tree,form',
                'views':[(kanban_id,'kanban'),(tree_id,'tree'),(form_id,'form')],
                'context': self.id,
                'domain': [('transporter_id','=',self.id)],
                'context': {
                'create': False,
                'edit' :False,
            },}

    def invoice_record(self):
        tree_id = self.env.ref('stock.vpicktree').id
        form_id = self.env.ref('stock.view_picking_form').id
        return {'type': 'ir.actions.act_window',
                'name':_('Delivery'),
                'res_model':'stock.picking',
                'view_mode':'tree,form',
                'views':[(tree_id,'tree'),(form_id,'form')],
                'context': self.id,
                'domain': [('transport_id','=',self.id)],
                'context': {
                'create': False,
                'edit' :False,
            },}

    def vehicles_count(self):
        for line in self:
            vehicle_id = self.env['fleet.vehicle'].search([('transporter_id','=',self.id)])
            line.calculate_vehicles = len(vehicle_id)

    def invoice_count(self):
        for line in self:
            invoice_id = self.env['stock.picking'].search([('transport_id','=',self.id)])
            line.calculate_invoice = len(invoice_id)

    def get_vehicles(self):
        for line in self:
            vehicle_id = self.env['fleet.vehicle'].search([('transporter_id','=',self.id)])
            if vehicle_id:
                line.vehicle_id = vehicle_id[0].id
            else:
                line.vehicle_id = False

            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
