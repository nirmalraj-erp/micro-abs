{
    'name': 'Micro Abrasive Invoice Template',
    'version': '12.0.1.0.0',
    'summary': 'Micro Abrasive Invoice Template',
    'description': 'Micro Abrasive Invoice Template',
    'category': 'Invoicing',
    'author': 'Howk-i ERP Zone - Simplified',
    'website': 'http://erp.howk-i.com/',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mail_compose_message_view.xml',
        # 'data/mail_template_data.xml',
        'views/account_inherit_template.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
