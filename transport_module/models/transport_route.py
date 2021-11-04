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



class transport_route(models.Model):
    _name  = 'transport.route'

    name = fields.Char('Name')
    transporter_id  = fields.Many2one('transport','Transporter')
    rote_locations_ids  =  fields.One2many('transport.location.details', 'route_id', 'Route Lines')
    

            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
