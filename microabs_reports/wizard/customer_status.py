# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class CustomerStatus(models.TransientModel):
    _name = 'customer.status'
    _description = 'Customer Status'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True)
    partner_id = fields.Many2many('res.partner', string='Customer')
    date_start = fields.Date(string="From Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="To Date", required=True, default=fields.Date.today)

    def generate_report(self):
        '''
        To generate the report
        :return: PDF Report
        '''
        if not self.partner_id:
            raise UserError(_('Please Select the Customer'))
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'partner_id': self.partner_id.ids,
            },
        }
        return self.env.ref('microabs_reports.customer_status_report_id').report_action(self, data=data)

    # Function call to generate report
    def export_all(self):
        return self.env.ref('microabs_reports.customer_status_report_xlsx').report_action(self)
