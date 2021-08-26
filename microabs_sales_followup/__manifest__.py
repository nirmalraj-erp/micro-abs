{
    'name': 'Micro Abrasive Sales Email Template',
    'version': '12.0.1.0.0',
    'summary': 'Micro Abrasive Sales Email Template',
    'description': 'Micro Abrasive Sales Email Template',
    'category': 'Invoicing',
    'author': 'Howk-i ERP Zone - Simplified',
    'website': 'http://erp.howk-i.com/',
    'license': 'AGPL-3',
    'depends': ['sale', 'micro_abs_sales'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'wizard/mail_compose_message_view.xml',
        'views/sale_order_email.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
