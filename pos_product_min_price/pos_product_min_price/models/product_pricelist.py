from odoo import models, fields

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    product_min_price = fields.Float('Precio minimo')
    