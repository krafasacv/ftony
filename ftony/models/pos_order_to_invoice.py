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
    x_monto_f = fields.Float('Monto de la factura', default='0', store =True)
    x_order_ids = fields.One2many('pos.order', 'account_move', string='Ids de Ordenes Afectadas',
        copy=False, readonly=True)
    x_prueba = fields.Char('para pruebas')

    def PostoInvoice(self):
        fi = datetime.combine(self.invoice_date, datetime.min.time()) + timedelta(hours=5)
        ff = fi + timedelta(hours=23)
        x = ''
        ordenes = self.env['pos.order'].search(['&',('date_order','>',fi),('date_order','<',ff)]).filtered(lambda r: r.state == 'done')

        if ordenes:
            x = ordenes.action_many_pos_order_invoice(self.x_monto_f)
            self.update(x)
            self.x_monto_f = self.amount_total
        #self.x_prueba = ordenes

        for order_id in self.x_order_ids:
            order_id.state = 'invoiced'


    def EntryReversal(self, default_values_list=None, cancel=True):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'move_type': 'entry',
                'reversed_entry_id': move.id,
                'journal_id': 3,
                'ref': 'reverso del asiento ' + move.name
            })
            move_vals_list.append(move.with_context(move_reverse_cancel=cancel)._reverse_move_vals(default_values, cancel=cancel))

        reverse_moves = self.env['account.move'].create(move_vals_list)

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel)._post(soft=False)
            for move, reverse_move in zip(self, reverse_moves):
                accounts = move.mapped('line_ids.account_id') \
                    .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
                for account in accounts:
                    (move.line_ids + reverse_move.line_ids)\
                        .filtered(lambda line: line.account_id == account and not line.reconciled)\
                        .with_context(move_reverse_cancel=cancel)\
                        .reconcile()

class PosOrdertoInvoice(models.Model):
    _inherit = 'pos.order'
    x_prueba = fields.Char('para pruebas')

    def prueba(self):
        for x in self:
            x.x_prueba =  self

    def action_many_pos_order_invoice(self,m): # se agrega el argumento m que es el monto a facturar
        invoice_vals = {}
        ref = ''
        refa = ''
        crm_team_id = self.crm_team_id.id
        cia = self.company_id.id
        lineas = self.env['pos.order.line'].search([('order_id', 'in', self.ids)])
        list_lin = []
        order_ids = []
        monto_partidas = 0
        b= 0
        for linea in lineas.sorted(key=lambda r: r.order_id.id):
            if refa != linea.order_id.name:
                if b != 0:
                    break
                ref += linea.order_id.name + ' '
                refa = linea.order_id.name
                order_ids.append(linea.order_id.id)

            list_lin.append((0, 0,
             {'ref': linea.order_id.name,
                  'journal_id': 10, #el Id es 10 para que se generen el el POS de lo contrario hay que poner el 1
                  'company_id': cia,
                  'company_currency_id': 33,
                  'account_id': linea.product_id.product_tmpl_id.categ_id.property_account_income_categ_id.id,
                  'account_root_id': linea.product_id.product_tmpl_id.categ_id.property_account_income_categ_id.root_id.id,
                  'name': linea.name,
                  'quantity': linea.qty,
                  'price_unit': linea.price_unit,
                  'product_uom_id': linea.product_uom_id.id,
                  'product_id': linea.product_id.id,
                  'tax_ids': [(6, 0, linea.tax_ids_after_fiscal_position.ids)]
              }))

            monto_partidas += linea.price_subtotal
            if monto_partidas > m:
                b=1

        invoice_vals = {
                'journal_id': 10, #el Id es 10 para que se generen el el POS de lo contrario hay que poner el 1
                'move_type': 'out_invoice',
                'invoice_origin': self.ids,
                'company_id': cia,
                'partner_id': 11014,
                'partner_shipping_id': 11014,
                'currency_id': self.pricelist_id.currency_id.id,
                'payment_reference': ref,
                'invoice_payment_term_id': 1,
                'team_id': crm_team_id,
                'invoice_line_ids': list_lin,
                'forma_pago': '01',
                'methodo_pago': 'PUE',
                'uso_cfdi': 'P01',
                'tipo_comprobante': 'I',
                'state': 'posted',
                'x_order_ids': order_ids,
            }
        return(invoice_vals)
    
    
#### Este procedimiento es para cuando se hace el cierre de caja el sistema genere los borradores de los tickets que se quedaron pendientes de #### timbrar

class NvPosInvoice(models.Model):
    _inherit = 'pos.session'
    x_prueba = fields.Char('para pruebas')

    def action_pos_order_corte_to_invoice(self):
        ordenes = self.order_ids.filtered(lambda r: r.state == 'invoiced' or r.state == 'paid' and r.partner_id.vat)
        self.x_prueba = ''
        for rec in ordenes:
            formadepago = ''
            y = rec.action_pos_order_invoice()
            paymentmethodid = sorted(rec.payment_ids, key=lambda pagos: pagos.amount, reverse=True)[0].payment_method_id.id
            if paymentmethodid == 1:
                formadepago = '01'
            elif paymentmethodid == 2:
                formadepago = '03'
            elif paymentmethodid == 3:
                formadepago = '04'
            elif paymentmethodid == 4:
                formadepago = '28'
            elif paymentmethodid == 5:
                formadepago = '03'
            else:
                formadepago = '99'
            
            recupdate = self.env['account.move'].search([('id','=',y['res_id'])])
            recupdate.forma_pago = formadepago
            recupdate.methodo_pago = 'PUE'
            recupdate.uso_cfdi = rec.partner_id.uso_cfdi
            recupdate.tipo_comprobante = 'I'
            self.x_prueba += str(y['res_id'])
        #return(invoice_vals)