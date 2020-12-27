from odoo import api, fields, models, _
from datetime import datetime
from dateutil import relativedelta
from num2words import num2words
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class SaleCommissionReportWizard(models.Model):
    _name = "sale.commission.report"
    _description = "Sale Commission Report Wizard"

    name = fields.Char(string='Name', default=lambda self: _('New'))
    period = fields.Char(string='Period')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    commission_line = fields.One2many('commission.line', 'line_id', string="Commission Line")
    currency_id = fields.Many2one('res.currency', 'Currency')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.order') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.commission.report') or _('New')
        result = super(SaleCommissionReportWizard, self).create(vals)
        return result

    @api.multi
    def amount_to_text(self, amount):
        amount_to_word = self.company_id.currency_id.amount_to_text(amount).title()
        return amount_to_word

    @api.multi
    def get_number_month(self, date):
        date = datetime.strptime(str(self.date_start), DEFAULT_SERVER_DATE_FORMAT)
        months = date.month
        year = date.year
        return num2words(months).title()


class CommissionLine(models.Model):
    _name = "commission.line"
    _description = "Commission Line"

    line_id = fields.Many2one('sale.commission.report', string='Commission ID')
    invoice_no = fields.Char(string='Invoice No.')
    invoice_date = fields.Date(string='Inv. Date')
    customer_code = fields.Char(string='Cust. Code')
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    invoice_amount = fields.Float(string='Inv. Amount')
    actual_received = fields.Float(string='Actually Received')
    commission_amount = fields.Float(string='Commission Amount')
    commission_percentage = fields.Integer(string='% Age')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)


class SaleCommissionReportInherit(models.AbstractModel):
    _name = 'report.microabs_sale_commission.sale_commission_report'
    _description = 'Sale Commission Report'

    @api.multi
    def _get_report_values(self, ids, data=None):
        report_obj = self.env['sale.commission.report'].browse(ids)
        return {
            'doc_ids': ids,
            'doc_model': 'sale.order',
            'docs': report_obj,
            'data': data,
        }
