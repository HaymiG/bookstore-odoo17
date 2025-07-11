from odoo import models, fields, api
from odoo.exceptions import UserError

class BookRental(models.Model):
    _name = 'book.rental'
    _description = 'Book Rental'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)

    book_id = fields.Many2one(
        'book.details',
        string='Book',
        required=True,
        domain=[('is_archived', '=', False)]
    )

    rent_date = fields.Date(string='Rent Date', required=True)
    return_date = fields.Date(string='Return Date')

    price = fields.Float(string="Rental Price", required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('rented', 'Rented'),
        ('returned', 'Returned'),
    ], string='State', tracking=True) 

    @api.model
    def create(self, vals):
        book = self.env['book.details'].browse(vals.get('book_id'))
        if book:
            if book.stock_qty < 1:
                raise UserError("Not enough stock to rent this book.")
            book.stock_qty -= 1
        return super(BookRental, self).create(vals)

    def mark_as_returned(self):
        for rental in self:
            if rental.state == 'returned':
                raise UserError("This book is already returned.")
            rental.state = 'returned'
            rental.return_date = fields.Date.today()
            rental.book_id.stock_qty += 1

    @api.onchange('book_id')
    def _onchange_book_id(self):
        if self.book_id:
            self.price = self.book_id.price
