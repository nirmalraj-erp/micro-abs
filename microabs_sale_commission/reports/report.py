from odoo import api, fields, models, _
from datetime import datetime
from dateutil import relativedelta
from num2words import num2words
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError


class SaleCommissionReportWizard(models.Model):
    _name = "sale.commission.report"
    _description = "Sale Commission Report Wizard"

    name = fields.Char(string='Name', index=True, default=lambda self: _('New'))
    period = fields.Char(string='Period')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    commission_line = fields.One2many('commission.line', 'line_id', string="Commission Line")
    currency_id = fields.Many2one('res.currency', 'Currency')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('revert', 'Reverted')], readonly=True,
                             default='draft', copy=False, string="Status")
    bank_name_id = fields.Many2one('bank.name', 'Bank Name')
    bank_address = fields.Char('Bank Address', store=True, compute='_get_bank_details')
    swift_code = fields.Char('Swift Code', store=True, compute='_get_bank_details')
    bank_acc_no = fields.Char('Acc No', store=True, compute='_get_bank_details')
    bb_contact = fields.Char('Name', store=True, compute='_get_bank_details')
    int_bank_address = fields.Char('Bank Address',store=True, compute='_get_bank_details')
    int_swift_code = fields.Char('Swift Code', store=True, compute='_get_bank_details')
    int_bank_acc_no = fields.Char('Acc No', store=True, compute='_get_bank_details')
    int_iban_no = fields.Char('IBAN NO./ Routing No.', store=True, compute='_get_bank_details')
    int_contact = fields.Char('Name', store=True, compute='_get_bank_details')
    # check = fields.Boolean('chechk', default=True)

    @api.onchange('bank_name_id')
    def _get_bank_details(self):
        if self.bank_name_id:
            self.bank_address = self.bank_name_id.bank_address
            self.swift_code = self.bank_name_id.swift_code
            self.bank_acc_no = self.bank_name_id.bank_acc_no
            self.bb_contact = self.bank_name_id.contact
            self.int_bank_address = self.bank_name_id.int_bank_address
            self.int_swift_code = self.bank_name_id.int_swift_code
            self.int_bank_acc_no = self.bank_name_id.int_bank_acc_no
            self.int_iban_no = self.bank_name_id.int_iban_no
            self.int_contact = self.bank_name_id.int_contact

    def action_revert(self):
        for line in self.commission_line:
            sale_cm_id = line.sale_commission_id
            sale_cm_id.write({'com_inv_status': 'revert'})
            sale_cm_id.write({'state': 'open'})
        self.name = 'Reverted'
        self.write({'state': 'revert'})
        return True

    def action_done(self):
        self.name = self.env['ir.sequence'].next_by_code('sale.commission.report') or _('New')
        self.write({'state': 'done'})
        return True

    # @api.model
    # def create(self, vals):
    #     if self.state == 'done':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('sale.commission.report') or _('New')
    #     result = super(SaleCommissionReportWizard, self).create(vals)
    #     return result

    @api.multi
    def amount_to_text(self, amount):
        amount_to_word = self.company_id.currency_id.amount_to_text(amount).title()
        return amount_to_word

    @api.multi
    def unlink(self):
        for invoice in self:
            if invoice.state not in 'draft':
                raise UserError(_('You cannot delete an invoice which is not in draft State.'))
        return super(SaleCommissionReportWizard, self).unlink()


class BankName(models.Model):
    _name = "bank.name"
    _description = "Bank Name"

    name = fields.Char('Bank Name')
    bank_acc_no = fields.Char('Acc No')
    bank_address = fields.Char('Bank Address')
    swift_code = fields.Char('Swift Code')
    iban_no = fields.Char('IBAN NO./ Routing No.')
    contact = fields.Char('Name')
    int_bank_address = fields.Char('Bank Address', store=True)
    int_swift_code = fields.Char('Swift Code', store=True)
    int_bank_acc_no = fields.Char('Acc No', store=True)
    int_iban_no = fields.Char('IBAN NO./ Routing No.', store=True)
    int_contact = fields.Char('Name', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))


class CommissionLine(models.Model):
    _name = "commission.line"
    _description = "Commission Line"
    _order = 'invoice_date'

    line_id = fields.Many2one('sale.commission.report', string='Commission ID')
    sale_commission_id = fields.Many2one('sale.commission', 'Sale Commission ID')
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
        if report_obj.state == 'revert':
            raise ValidationError(_(
                'Invalid Action!! You cannot print the report in Reverted state'))
        else:
            return {
                'doc_ids': ids,
                'doc_model': 'sale.order',
                'docs': report_obj,
                'data': data,
            }
