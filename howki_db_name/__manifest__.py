# -*- coding: utf-8 -*-
{
    'name': "Howki Display DB Name",

    'summary': """
       Display DB name near user.""",

    'description': """
    """,
    'author': 'Howk-i ERP Zone - Simplified',
    'website': 'http://erp.howk-i.com/',
    'license': 'OPL-1',
    'version': '12.0.1.0.0',
    'depends': ['web'],
    # always loaded
    'data': [
        'views/display_db_name.xml',
    ],
    'installable': True,
    'auto_install': False,
 
}