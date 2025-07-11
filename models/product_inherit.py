from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_bookstore_item = fields.Boolean(string="Bookstore Item")
