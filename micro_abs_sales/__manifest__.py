{
    'name': 'Micro Abrasive Sales',
    'version': '12.0.1.0.0',
    'summary': 'Micro Abrasive Sales',
    'description': 'Micro Abrasive Sales module with custom changes in Product master, Sale order and Invoice',
    'category': 'Sales',
    'author': 'Howk-i ERP Zone - Simplified',
    'website': 'http://erp.howk-i.com/',
    'license': 'AGPL-3',
    'depends': ['sale','account'],
    'data': [
        'views/sales_inherit.xml',
        'views/configuration_views.xml',
		'security/ir.model.access.csv',
        'reports/sale_order_report.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
