# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta,datetime
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools,
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)

class PosOrdertoPosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_to_pos_order(self):
        pos_order = {}
        cia = 6
        pos_order = {
                'amount_tax': self.amount_tax,
                'amount_total': self.amount_total,
                'amount_paid': self.amount_paid,
                'amount_return': self.amount_return,
                'company_id': cia,
                'pricelist_id': self.pricelist_id.id,
                'session_id': self.session_id.id,
                'state': 'done',
                'pos_reference': self.pos_reference,
                'sale_journal': self.sale_journal,
                'x_prueba': self.lines,
            }

        self.env['pos.order'].sudo().create(pos_order)
