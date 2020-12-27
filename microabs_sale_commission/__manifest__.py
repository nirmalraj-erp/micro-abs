{
    'name': 'Micro Abrasive Sales Commission',
    'version': '12.0.1.0.0',
    'summary': 'Micro Abrasive Sales Commission',
    'description': 'Micro Abrasive Sales Commission module with custom changes in Customer master, '
                   'Sale order and Invoice',
    'category': 'Sales Commission',
    'author': 'The Nth Metal',
    'website': '',
    'support': 'nirmalraj.erp@gmail.com',
    'license': 'AGPL-3',
    'depends': ['sale','account'],
    'data': [
        'views/sales_commission.xml',
        'wizard/commission_invoice.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'security/sale_commission_security.xml',
        'reports/sale_commission_report.xml',
        'reports/report_wizard_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
