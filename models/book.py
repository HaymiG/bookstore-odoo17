from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class BookDetails(models.Model):
    _name = 'book.details'
    _description = 'Book Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='title'

    title = fields.Char(required=True, tracking=True)
    is_featured = fields.Boolean(string="Featured", default=False)

    product_id = fields.Many2one(
        'product.product',
        string='Related Product',
        domain=[('detailed_type', '=', 'product')],
        required=True
    )

    author_id = fields.Many2one(
        'res.partner',
        string='Author',
        domain="[('author', '=', True)]",
        tracking=True
    )

    publisher = fields.Char(required=True)
    published_date = fields.Date(required=True, tracking=True)
    book_age = fields.Integer(compute='_compute_book_age', store=True)
    isbn = fields.Char(string="ISBN", unique=True)
    is_archived = fields.Boolean(default=False)
    stock_qty = fields.Float(default=0.0, string="Stock Quantity")
    price = fields.Monetary()

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    genre_ids = fields.Many2many('genre.details', string='Genres', tracking=True)
    cover_image = fields.Binary("Cover Image")

    can_archive = fields.Boolean(compute='_compute_archive_buttons')
    can_unarchive = fields.Boolean(compute='_compute_archive_buttons')

    @api.depends('published_date')
    def _compute_book_age(self):
        for record in self:
            if record.published_date:
                record.book_age = date.today().year - record.published_date.year
            else:
                record.book_age = 0

    @api.depends('is_archived')
    def _compute_archive_buttons(self):
        for record in self:
            record.can_archive = not record.is_archived
            record.can_unarchive = record.is_archived

    @api.constrains('stock_qty', 'price', 'published_date')
    def _check_validations(self):
        for record in self:
            if record.stock_qty < 0:
                raise ValidationError(_('Stock quantity cannot be negative.'))
            if record.price < 0:
                raise ValidationError(_('Price cannot be negative.'))
            if record.published_date and record.published_date > date.today():
                raise ValidationError(_('Published date cannot be in the future.'))

    def action_archive(self):
        for record in self:
            record.is_archived = True

    def action_unarchive(self):
        for record in self:
            record.is_archived = False

    def decrease_stock(self, qty=1):
        for record in self:
            if record.stock_qty < qty:
                raise UserError(_('Not enough stock to rent this book.'))
            record.stock_qty -= qty

    def increase_stock(self, qty=1):
        for record in self:
            record.stock_qty += qty

    @api.model
    def create(self, vals):
        # Create a related product with Can be Purchased enabled
        product_template = self.env['product.template'].create({
            'name': vals.get('title'),
            'list_price': vals.get('price', 0.0),
            'detailed_type': 'stockable',
            'purchase_ok': True,
        })
        vals['product_id'] = product_template.id
        return super(BookDetails, self).create(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        return {
            'domain': {
                'product_id': [('purchase_ok', '=', True)]
            }
        }


class BookRental(models.Model):
    _name = 'book.rental'
    _description = 'Book Rental'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    book_id = fields.Many2one('book.details', string='Book', required=True, domain="[('is_archived', '=', False)]")
    rent_date = fields.Date(string='Rent Date', required=True, default=fields.Date.context_today)
    return_date = fields.Date(string='Return Date')
    price = fields.Float(string="Rental Price", required=True)
    state = fields.Selection([
        ('rented', 'Rented'),
        ('returned', 'Returned')
    ], default='rented', string='State', readonly=True)

    def action_mark_as_returned(self):
        for rental in self:
            if rental.state == 'returned':
                raise UserError("This book is already returned.")
            rental.state = 'returned'
            rental.return_date = fields.Date.today()
            # Increase stock back on return
            rental.book_id.increase_stock()

    @api.model
    def create(self, vals):
        # When renting, decrease the stock of the book
        book = self.env['book.details'].browse(vals.get('book_id'))
        if book:
            book.decrease_stock()
        return super(BookRental, self).create(vals)
