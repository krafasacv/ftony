# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta,datetime
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
           
#este procedimiento es para agrupar varias notas de venta en una sola factura
    def action_many_nv_one_invoice(self): 
        
        if self.company_id.id in [1,2,3,]:
            diario = 52
            cia = 6
            crm_team_id = 1
            accountid = 269
            
        invoice_vals = {}
        ref = ''
        refa = ''
        m = 0
        list_lin = []
        monto_partidas = 0
        # las facturas deben estar pagadas, de lo contario hay que quitar el filtro
        invoice_vals = {
                'journal_id': diario, 
                'move_type': 'out_invoice',
                'company_id': cia,
                #'partner_id': 11014,
                #'partner_shipping_id': 11014,
                'currency_id': self.company_id.currency_id.id,
                'payment_reference': ref,
                'invoice_payment_term_id': 1,
                'team_id': crm_team_id,
                'invoice_line_ids': list_lin,
                'forma_pago': '01',
                'methodo_pago': 'PUE',
                'uso_cfdi': 'P01',
                'tipo_comprobante': 'I',
                'state': 'draft',
            }
        
        lineas = self.env['account.move.line'].search([('move_id', 'in', self.ids)]) \
                    .filtered(lambda r: r.product_id.product_tmpl_id.x_clave_alterna)
        
        for linea in lineas.sorted(key=lambda r: r.move_id.id):
            impuestos = []
        
            producto = self.env['product.product'].sudo().search([('default_code', '=', linea.product_id.product_tmpl_id.x_clave_alterna)])
            
            for tax in producto.taxes_id:
                impuestos.append(tax.id)
            
            if m != 0:
                monto_partidas += linea.price_subtotal
                
            if monto_partidas > 2000:
                self.env['account.move'].sudo().create(invoice_vals)
                monto_partidas = linea.price_subtotal
                list_lin.clear()
            
            list_lin.append((0, 0,
                             {'ref': linea.move_id.name,
                          'journal_id': diario, 
                          'company_id': cia,
                          'company_currency_id': self.company_id.currency_id.id,
                          'account_id': accountid, 
                          'account_root_id': accountid, 
                          'name': linea.name,
                          'quantity': linea.quantity,
                          'price_unit': linea.price_unit,
                          'product_uom_id': linea.product_uom_id.id,
                          'product_id': producto.id,
                          'tax_ids': [(6, 0, impuestos)]
                              }))
        

        self.x_prueba = invoice_vals
        self.env['account.move'].sudo().create(invoice_vals)
        