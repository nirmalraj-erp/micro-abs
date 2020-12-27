# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'),
              ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'),('12', 'Dec')]


class CommissionInvoice(models.TransientModel):
    _name = "commission.invoice"
    _description = "Commission Invoice"

    @api.multi
    def update_invoice_status(self):
        numdays = 100
        active = self.env.context.get('active_ids')
        commission_invoice_list = self.env["sale.commission"].search([('id', 'in', active)])
        vals = ({'name': self.env['ir.sequence'].next_by_code('sale.commission.report')})
        commission_report_obj = self.env["sale.commission.report"].create(vals)
        for cm_list in commission_invoice_list:
            date_invoice = cm_list.invoice_date
            if cm_list.state == 'open':
                cm_params = ({
                    'commission_line': [(0, 0, {
                        'invoice_no': cm_list.invoice_no,
                        'invoice_date': cm_list.invoice_date,
                        'customer_id': cm_list.customer_id.id,
                        'invoice_amount': cm_list.invoice_amount,
                        'actual_received': cm_list.actual_received,
                        'commission_amount': cm_list.commission_amount,
                        'commission_percentage': cm_list.commission_percentage,
                        'currency_id': cm_list.currency_id.id,
                        'company_id': cm_list.company_id.id,
                    })],
                   })
            else:
                raise UserError(_('Invalid Action!! You have selected Paid Commission Invoice'))
            cm_list.update({'state': 'paid'})
            self.env["sale.commission.report"].search([('id', '=', commission_report_obj.id)]).update(cm_params)

