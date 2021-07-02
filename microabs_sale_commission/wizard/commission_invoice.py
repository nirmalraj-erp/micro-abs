# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class CommissionInvoice(models.TransientModel):
    _name = "commission.invoice"
    _description = "Commission Invoice"

    @api.multi
    def update_invoice_status(self):
        active = self.env.context.get('active_ids')
        commission_invoice_list = self.env["sale.commission"].search([('id', 'in', active)])
        vals = ({'name': _('New')})
        amount = 0
        commission_report_obj = self.env["sale.commission.report"].create(vals)
        for cm_list in commission_invoice_list:
            print('111111111111111111', cm_list)
            date_invoice = cm_list.invoice_date
            if cm_list.state == 'open':
                amount += cm_list.commission_amount
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
                        'sale_commission_id': cm_list.id,
                    })],
                   })
                commission_report_obj.update({'total_due': amount})
            else:
                raise UserError(_('Invalid Action!! You cannot settle the commission invoice which is already paid'))
            cm_list.update({'state': 'paid'})
            cm_list.update({'com_inv_status': 'done'})
            self.env["sale.commission.report"].search([('id', '=', commission_report_obj.id)]).update(cm_params)
            commission_report_list = self.env["sale.commission.report"].search([('id', '=', commission_report_obj.id)])
            date_list = commission_report_list.commission_line.mapped('invoice_date')
            min_date = min(date_list)
            max_date = max(date_list)
            year, month, date = str(min_date).split('-')
            start_date = month + '/' + year
            year, month, date = str(max_date).split('-')
            end_date = month + '/' + year
            if start_date == end_date:
                commission_report_list.period = end_date
            else:
                commission_report_list.period = start_date + '-' + end_date


class CommissionInvoiceOpen(models.TransientModel):
    _name = "commission.invoice.open"
    _description = "Commission Invoice Open"

    @api.multi
    def update_invoice_status_open(self):
        active = self.env.context.get('active_ids')
        commission_invoice_list = self.env["sale.commission"].search([('id', 'in', active)])
        for cm_list in commission_invoice_list:
            if cm_list.state == 'revert':
                cm_list.update({'state': 'open'})
            else:
                raise UserError(_('Invalid Action!! You cannot open the commission invoice which is already paid'))

