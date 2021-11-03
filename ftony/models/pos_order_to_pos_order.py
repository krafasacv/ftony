
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta,datetime
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)

class PosOrdertoPosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_to_pos_order(self,new_session_id):
        pos_order = {}
        cia = 6
        
#####        
        lineas = self.env['pos.order.line'].search([('order_id', 'in', self.ids)]) \
                    .filtered(lambda r: r.product_id.product_tmpl_id.x_clave_alterna)
        list_lin = []
        order_ids = []
        
        monto_partidas = 0
        b= 0
        clave_alterna =''
        lin_subtotal = 0
        total = 0
        sum_tax = 0
        #for linea in lineas.sorted(key=lambda r: r.tax_ids_after_fiscal_position.ids): Esta seria la linea para ordenar por impuestos
        for linea in lineas.sorted(key=lambda r: r.order_id.id):
            impuestos = []
            
            lin_subtotal += linea.price_subtotal
            total += linea.price_subtotal_incl
            sum_tax =  total - lin_subtotal
            producto = self.env['product.product'].sudo().search([('default_code', '=', linea.product_id.product_tmpl_id.x_clave_alterna)])
            
            for tax in producto.taxes_id:
                impuestos.append(tax.id)
            
            
            list_lin.append((0, 0,
             {
                  'company_id': cia,
                  'name': linea.name,
                  'qty': linea.qty,
                  'price_unit': linea.price_unit,
                  'product_uom_id': linea.product_uom_id.id,
                 'full_product_name': producto.name,
                 'product_id': producto.id,
                 'tax_ids': [(6, 0, impuestos)],
                  'price_subtotal': linea.price_subtotal,
                 'price_subtotal_incl': linea.price_subtotal_incl,
                 #'notice': linea.tax_ids_after_fiscal_position.ids
                 'notice': impuestos
              }))

######        
        pos_order = {
                'amount_tax': sum_tax,#self.amount_tax,
                'amount_total': total,#self.amount_total,
                'amount_paid': total,
                'amount_return': self.amount_return,
                'company_id': cia,
                'pricelist_id': 3,
                'session_id': new_session_id,
                'state': 'paid',#'done',
                'pos_reference': self.pos_reference,
                'lines': list_lin,
                'partner_id': 7444,
            
                #'x_prueba': lineas,
            }

        if total > 0:
            new_pos_order = self.env['pos.order'].sudo().create(pos_order)
            pos_pago = {
                'pos_order_id': new_pos_order.id,
                'amount': total,
                'payment_method_id': 12,
                'session_id': new_session_id 
            }
            self.env['pos.payment'].sudo().create(pos_pago)
        
        
class PosConfigTony(models.Model):
    _inherit = 'pos.config'
    x_company_correspondiente = fields.Many2one('res.company', string='Compñia correspondiente',
        copy=True, storage=True)
    
    def open_session_mnm(self, check_coa=True): #procedimiento para abrir sessión sin interface m aricela n avez m artinez (mnm)
        """ new session button Maricela Navez M

        create one if none exist
        access cash control interface if enabled or start a session
        """
        self.ensure_one()
        if not self.current_session_id:
            self._check_company_journal()
            self._check_company_invoice_journal()
            self._check_company_payment()
            self._check_currencies()
            self._check_profit_loss_cash_journal()
            self._check_payment_method_ids()
            self._check_payment_method_receivable_accounts()
            new = self.env['pos.session'].create({
                'user_id': self.env.uid,
                'config_id': self.id
            })
            
            timezone = self._context.get('tz')
            if not timezone:
                timezone = self.journal_id.tz or self.env.user.partner_id.tz or 'America/Mexico_City'
                
            local = pytz.timezone(timezone)
            fecha = new.start_at.replace(tzinfo=pytz.UTC).astimezone(local) - timedelta(days=1)
            fi = fecha.replace(hour=7,minute=0,second=0)
            ff = (fecha + timedelta(days=2)).replace(hour=7,minute=0,second=0)
            ordenes = self.env['pos.order'].sudo().search(["&","&",('date_order',">",fi),('date_order',"<",ff),('company_id', '=', 1)])
            self.x_prueba = str(fi) + ' ' + str(ff)
            
            for rec in ordenes:
                if rec.partner_id != False:
                    rec.action_pos_order_to_pos_order(new.id)
                

class PosSessionTony(models.Model):
    _inherit = 'pos.session'
    
    def action_pos_session_closing_control_and_invoice(self):
        self.action_pos_session_closing_control()
        self.invoice_session()
    
    def invoice_session(self):
        productos = self.env['product.template'].search([('id', 'in', [39608,39609,39610,39611])])
        nt = 0.00
        lineas = []
        for rec in self.order_ids:                
            for y in productos:
                #self.x_prueba = y.taxes_id.id
                lin = rec.lines.filtered(lambda r: r.tax_ids_after_fiscal_position.id == y.taxes_id.id)
                
                if sum( i.price_subtotal_incl for i in lin) > 0:
                    lineas.append({
                        'product_id': y.id,
                        'quantity': 1,
                        'discount': 0,
                        'price_unit': sum( i.price_subtotal_incl for i in lin),
                        'name': y.display_name + " del pedido " + rec.name,
                        'tax_ids': [(6, 0, [y.taxes_id.id])],
                        'product_uom_id': y.uom_id.id,
                    })
                        
            
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        move_vals = {
        #'payment_reference': self.name,
        'invoice_origin': self.name,
        'journal_id': self.config_id.invoice_journal_id.id,
        'move_type': 'out_invoice',
        'ref': self.name,
        'partner_id': 7444,
        'narration': 'VENTA DEL DÍA', 
        # considering partner's sale pricelist's currency
        'currency_id': self.company_id.currency_id.id,
        'invoice_user_id': self.user_id.id,
        #'invoice_date': self.date_order.astimezone(timezone).date(),
        #'fiscal_position_id': self.fiscal_position_id.id,
        'invoice_line_ids': lineas,#[(0, 0, lineas)],
        'invoice_cash_rounding_id': False
        }
        
        new_move = self.env['account.move'].sudo().create(move_vals)
        message = ("This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (self.id, self.name)
        new_move.message_post(body=message)

        #for rec in self.order_ids:
        #    rec.write({'account_move': new_move.id, 'state': 'invoiced', 'to_invoice': True})
            
        new_move.sudo().with_company(self.company_id)._post()    
        new_move.PostoInvoiceReversal()

        
class PosSessionInvoice(models.Model):
    _inherit = 'account.move'
                                                                        
    def PostoInvoiceReversal(self, default_values_list=None, cancel=True):
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
                'journal_id': 54,
                'ref': 'reverso del asiento ' + move.name,
                'invoice_date': move.invoice_date
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