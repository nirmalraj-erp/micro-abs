{
    'name': 'Micro Abrasive Payment Follow-ups',
    'version': '12.0.1.0.0',
    'summary': 'Automatic Payment Follow-ups',
    'description': 'Automatic Payment Follow-ups',
    'category': 'Invoicing',
    'author': 'Howk-i ERP Zone - Simplified',
    'website': 'http://erp.howk-i.com/',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/payment_followup_security.xml',
        'views/res_partner.xml',
        'views/payment_followup.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
