# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.tools import groupby, float_is_zero


class sale_order(models.Model):
	
	_inherit  = 'sale.order'

	transport_id = fields.Many2one('transport','Transport Via')



	def _prepare_invoice(self):
        
		self.ensure_one()
		journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
		if not journal:
		    raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
		
		invoice_vals = {
		    'ref': self.client_order_ref or '',
		    'move_type': 'out_invoice',
		    'narration': self.note,
		    'currency_id': self.pricelist_id.currency_id.id,
		    'campaign_id': self.campaign_id.id,
		    'medium_id': self.medium_id.id,
		    'source_id': self.source_id.id,
		    'invoice_user_id': self.user_id and self.user_id.id,
		    'team_id': self.team_id.id,
		    'partner_id': self.partner_invoice_id.id,
		    'partner_shipping_id': self.partner_shipping_id.id,
		    'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
		    'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
		    'journal_id': journal.id,  # company comes from the journal
		    'invoice_origin': self.name,
		    'invoice_payment_term_id': self.payment_term_id.id,
		    'payment_reference': self.reference,
		    'transaction_ids': [(6, 0, self.transaction_ids.ids)],
		    'invoice_line_ids': [],
		    'company_id': self.company_id.id,
		}
		return invoice_vals


