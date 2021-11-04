# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, Warning
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class stock_picking(models.Model):
    
    _inherit  = 'stock.picking'

    tracking_number  =  fields.Char('Tracking Number', copy=False, readonly=True, index=True)
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle')
    driver_id = fields.Many2one('res.partner', 'Vehicle Driver', related='vehicle_id.driver_id')
    date = fields.Datetime('Transport Date',default = datetime.now())
      
    def write(self, vals):
        if vals.get('no_of_parcels') or vals.get('lr_number'):
           #searching transport entry
           search_transport_entry_ids = self.env['transport.entry'].search([('picking_id','=', self.id)])
           if search_transport_entry_ids:
               transport_entry = search_transport_entry_ids[0]
               if vals.get('no_of_parcels'):
                   transport_entry.no_of_parcels = vals.get('no_of_parcels')
                   if vals.get('lr_number'):
                       transport_entry.lr_number = vals.get('lr_number')
        date_from = datetime.combine(date.today(), datetime.min.time())
        if vals.get('date'):
          date_time = datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S')
          if date_time < datetime.now():
            raise Warning(_("Please select a proper date."))
          if vals.get('vehicle_id'):
            entry = self.env['transport.entry'].search([('transport_id', '=', self.transport_id.id),('tag_ids', '=', vals['vehicle_id']),('state', '=', 'in-progress')])           
            if entry:
              for transport in entry:
                length = len(transport.transport_rote_ids)-1
                if len(transport.transport_rote_ids) == len(transport.transport_rote_ids):
                    if transport.transport_rote_ids[0].start_time <= date_time and transport.transport_rote_ids[length].end_time >= date_time:
                        raise UserError(
                        _(' Fleet is occupied for selected date.'))
                else:
                    if transport.transport_rote_ids[0].start_time <= date_time and transport.transport_rote_ids[0].end_time >= date_time:
                        raise UserError(
                        _(' Fleet is occupied for selected date.'))
          else:
            entry = self.env['transport.entry'].search([('transport_id', '=', self.transport_id.id),('tag_ids', '=', self.vehicle_id.id),('state', '=', 'in-progress')])           
            if entry:
              for transport in entry:
                length = len(transport.transport_rote_ids)-1
                if len(transport.transport_rote_ids) == len(transport.transport_rote_ids):
                    if transport.transport_rote_ids[0].start_time <= date_time and transport.transport_rote_ids[length].end_time >= date_time:
                        raise UserError(
                        _(' Fleet is occupied for selected date.'))
                else:
                    if transport.transport_rote_ids[0].start_time <= date_time and transport.transport_rote_ids[0].end_time >= date_time:
                        raise UserError(
                        _(' Fleet is occupied for selected date.'))
        else:
          date_time = self.date
          if vals.get('vehicle_id'):
            entry = self.env['transport.entry'].search([('transport_id', '=', self.transport_id.id),('tag_ids', '=', vals['vehicle_id']),('state', '=', 'in-progress')])           
            if entry:
              for transport in entry:
                length = len(transport.transport_rote_ids)-1
                if len(transport.transport_rote_ids) == len(transport.transport_rote_ids):
                    if transport.transport_rote_ids[0].start_time <= date_time and transport.transport_rote_ids[length].end_time >= date_time:
                        raise UserError(
                        _(' Fleet is occupied for selected date.'))
                else:
                    if transport.transport_rote_ids[0].start_time <= date_time and transport.transport_rote_ids[0].end_time >= date_time:
                        raise UserError(
                        _(' Fleet is occupied for selected date.'))
        return super(stock_picking, self).write(vals)

    @api.model
    def create(self, val):
        if val.get('tracking_number', 'New') == 'New':
            val['tracking_number'] = self.env['ir.sequence'].next_by_code('stock.picking') or _('New')
        
        if val.get('origin'):
            sale_order_object = self.env['sale.order']
            sale_order_record = sale_order_object.search([('name', '=',val.get('origin') )])
            if sale_order_record:
                sale_order_record = sale_order_record[0]
                if sale_order_record.transport_id:
                    val.update({'transport_id': sale_order_record.transport_id.id })
                    res= super(stock_picking, self).create(val)                                 
                else:
                    res= super(stock_picking, self).create(val) 
            else:
                res= super(stock_picking, self).create(val)

        else :    
            res= super(stock_picking, self).create(val)                                                          
        return res
    
    
    transport_id  =  fields.Many2one('transport')
    no_of_parcels = fields.Integer('No Of Parcels')
    lr_number =  fields.Integer('LR Number')
    parcel_entry_done =  fields.Boolean('Parcel Entry Done', default = False, copy=False)
    transport_ids = fields.One2many('transport.entry', 'picking_id','Transport Entries')
    trans_ids = fields.One2many('transport.entry', 'picking_id')
    route_id  = fields.Many2one('transport.route', 'Route')
    transport_routes_ids = fields.One2many('transport.location.details','picking_id')
    trans_count = fields.Integer(string='Number of Transport Entry',compute='_get_products_count')



    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        for a in self:
            entry = self.env['transport.entry'].search([('picking_id', '=', a.id)])
            if not entry: 
                self.env['transport.entry'].create({
                    'date': date.today(),
                    'active' : True,
                    'picking_id':a.id,
                    'lr_number':a.lr_number,
                    'customer_id':a.partner_id.id,
                    'contact_person':a.transport_id.contact_name,
                    'no_of_parcels':a.no_of_parcels,
                    'transport_id':a.transport_id.id,
                    'tag_ids' : a.vehicle_id.id,
                    'date' : a.date,
                    'driver_id' : a.driver_id.id,
                    'sale_order' : a.origin,
                    'location_dest_id' : a.location_dest_id.id,
                    })

        value = []
        for location in self.transport_routes_ids:
            value.append([0,0,{'source_loc': location.source_loc.id,
                            'dest_loc': location.dest_loc.id,
                            'distance': location.distance,
                            'time': location.time,
                            'note': location.note,
                            'tracking_number':self.tracking_number,
                            }])
        res = self.env['transport.entry'].search([('picking_id','=',self.id)])
        
        if not res.transport_rote_ids: 
            res.write({
                'lr_number' : self.lr_number,
                'transport_rote_ids':value, 
            })
            
        
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        return True




    @api.depends('trans_ids')
    def _get_products_count(self):
        self.trans_count = len(self.trans_ids)

    @api.onchange('route_id')
    def onchange_route_id(self):
        lines = [] 
        origin  = self.origin
        sale_orders = self.env['sale.order'].search([('name', '=', origin)])

        picking = self       
        for location in self.route_id.rote_locations_ids:
            abc = {
                'source_loc':location.source_loc.id, 
                'picking_id': self.id,        
                'dest_loc':location.dest_loc.id, 
                'distance':location.distance,
                'time':location.time 
            }
            if picking:
                res= self.env['transport.location.details'].create({
                    'source_loc':location.source_loc.id, 
                    'picking_id': picking.id,        
                    'dest_loc':location.dest_loc.id, 
                    'distance':location.distance,
                    'time':location.time,
                })
            lines.append(res.id)
        self.transport_routes_ids  = [(6,0,lines)]
        
        