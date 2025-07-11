{
    'name': 'My Bookstore',
    'version': '17.0.1.0.0',
    'depends': ['base', 'product', 'mail'],  
    'summary': 'Manage bookstore inventory and sales',
    'sequence': 10,
    'description': """A simple module to manage bookstore""",
    'category': 'Productivity',
    'author': 'Haymanot',
    'website': '',
    'data': [
        
        'security/ir.model.access.csv',
         'security/security.xml',
      
        'views/book_wizard_view.xml',
        'data/genre_model.xml',
        'views/book_views.xml',
        'views/genre_views.xml',
        'views/book_kanban_view.xml',
         'views/product_inherit_view.xml',
        'views/book_rental_view.xml',
        'views/menu.xml',
    
],
    
    'demo': [
    'data/demo_data.xml',
],
    'installable': True,
    'application': True,
    'auto_install': False,
}
