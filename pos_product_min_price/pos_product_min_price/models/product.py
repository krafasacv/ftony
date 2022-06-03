from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    product_min_price = fields.Float('Precio minimo')
    