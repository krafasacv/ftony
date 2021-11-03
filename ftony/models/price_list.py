from odoo import models, fields, api

class PriceListMin(models.Model):
    _inherit = 'product.pricelist.item'
              
    @api.onchange('fixed_price')
    def on_change_price(self):
        for record in self:
            if record.min_quantity == 1:
                record.product_tmpl_id['list_price'] = record.fixed_price
                
            