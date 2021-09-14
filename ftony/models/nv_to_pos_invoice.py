# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)

class NvPosInvoice(models.Model):
    _inherit = 'account.move'
    x_prueba = fields.Char('para pruebas')
    x_ff = fields.Char('ff', default='/')

    def action_nv_to_pos_invoice(self):
        invoice_vals = {}
        ref = ''
        #crm_team_id = self.crm_team_id.id
        cia = self.company_id.id
        list_lin = []#

        for linea in self.invoice_line_ids:
            list_lin.append((0, 0,
                             {'ref': linea.name,
                              'journal_id': 10,
                              # el Id es 10 para que se generen el el POS de lo contrario hay que poner el 1
                              'company_id': cia,
                              'company_currency_id': 33,
                              'account_id': linea.account_id.id,
                              'account_root_id': linea.account_root_id.id,
                              'name': linea.name,
                              'quantity': linea.quantity,
                              'price_unit': linea.price_unit,
                              'product_uom_id': linea.product_uom_id.id,
                              'product_id': linea.product_id.id,
                              'tax_ids': [(6, 0, linea.tax_ids.ids)]
                              }))
            ref += linea.name

        invoice_vals = {
            'journal_id': 10,  # el Id es 10 para que se generen el el POS de lo contrario hay que poner el 1
            'move_type': 'out_invoice',
            'invoice_origin': self.ids,
            'company_id': cia,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'currency_id': self.currency_id.id,
            #'payment_reference': ref,
            'invoice_payment_term_id': 1,
            #'team_id': crm_team_id,
            'invoice_line_ids': list_lin,
            'forma_pago': '01',
            'methodo_pago': 'PUE',
            'uso_cfdi': 'P01',
           'tipo_comprobante': 'I',
        }

        idnew = self.env['account.move'].sudo().create(invoice_vals)
        self.env.cr.commit()

    def folio_factura_fiscal(self):
        if self.x_ff == '/':
            sequence_id = self.env['ir.sequence'].search([('code', '=', 'account.sequence.ff')])
            sequence_pool = self.env['ir.sequence']
            application_no = sequence_pool.sudo().get_id(sequence_id.id)
            self.write({'x_ff': application_no})
            self.write({'x_prueba': application_no})


        #for rec in self:
        #    rec.state = 'invoiced'
        #    rec.account_move = idnew
