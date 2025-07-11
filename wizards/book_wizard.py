from odoo import models, fields, api

class BookWizard(models.TransientModel):
    _name = 'book.wizard'
    _description = 'Batch Feature Books Wizard'

    book_ids = fields.Many2many('book.details', string="Books to Feature")
    is_featured = fields.Boolean(string="Set as Featured", default=True)

    def apply_featured(self):
        for book in self.book_ids:
            book.is_featured = self.is_featured
