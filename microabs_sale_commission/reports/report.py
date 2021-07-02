from odoo import api, fields, models, _
from datetime import datetime
from dateutil import relativedelta
from num2words import num2words
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError


class SaleCommissionReportWizard(models.Model):
    _name = "sale.commission.report"
    _description = "Sale Commission Report Wizard"

    # def get_currency(self):
    #     return self.env.ref('base.main_company').currency_id

    name = fields.Char(string='Name', index=True, default=lambda self: _('New'))
    period = fields.Char(string='Period')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    commission_line = fields.One2many('commission.line', 'line_id', string="Commission Line")
    currency_id = fields.Many2one('res.currency', 'Currency')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('revert', 'Reverted'), ('paid', 'Paid')], readonly=True,
                             default='draft', copy=False, string="Status")
    bank_name_id = fields.Many2one('bank.name', 'Bank')
    bank_address = fields.Char('Bank Address')
    swift_code = fields.Char('Swift Code')
    bank_acc_no = fields.Char('Acc No')
    bb_contact = fields.Char('Bank Name')
    company_name = fields.Char('Name')
    company_address = fields.Char('Address')
    int_bank_address = fields.Char('Bank Address')
    int_swift_code = fields.Char('Swift Code')
    int_bank_acc_no = fields.Char('Acc No')
    int_iban_no = fields.Char('IBAN NO./ Routing No.')
    int_contact = fields.Char('Name', store=True)
    # check = fields.Boolean('chechk', default=True)
    total_commission = fields.Float(
        string="Total Commission",
        compute="_compute_commission_total",
        store=True,
    )
    total_invoice = fields.Float(
        string="Total Invoice",
        compute="_compute_commission_total",
        store=True,
    )
    total_due = fields.Float(string="Total Due")
    commission_count = fields.Integer(compute='compute_commission_count', string="Payments")

    @api.depends('state')
    def compute_commission_count(self):
        for record in self:
            payment = self.env["commission.payment.history"].sudo().search_count([('commission_id', '=', record.id)])
            record.commission_count = payment

    @api.multi
    def action_account_payment(self):
        payment_id = self.env["commission.payment.history"].sudo().search([('commission_id', '=', self.id)])
        action = self.env.ref('microabs_sale_commission.action_commission_payment_history').read()[0]
        action['domain'] = [('id', 'in', payment_id.ids)]
        return action
    
    @api.depends('commission_line.commission_amount', 'commission_line.invoice_amount')
    def _compute_commission_total(self):
        for record in self:
            record.invoice_amount = 0.0
            record.commission_amount = 0.0
            for line in record.commission_line:
                record.total_commission += sum(x.commission_amount for x in line)
                record.total_invoice += sum(x.invoice_amount for x in line)
                record.total_due = record.total_commission

    @api.onchange('bank_name_id')
    def _get_bank_details(self):
        for rec in self:
            if rec.bank_name_id:
                rec.bank_address = rec.bank_name_id.bank_address
                rec.swift_code = rec.bank_name_id.swift_code
                rec.bank_acc_no = rec.bank_name_id.bank_acc_no
                rec.bb_contact = rec.bank_name_id.contact
                rec.company_name = rec.bank_name_id.company_name
                rec.company_address = rec.bank_name_id.company_address
                rec.int_bank_address = rec.bank_name_id.int_bank_address
                rec.int_swift_code = rec.bank_name_id.int_swift_code
                rec.int_bank_acc_no = rec.bank_name_id.int_bank_acc_no
                rec.int_iban_no = rec.bank_name_id.int_iban_no
                rec.int_contact = rec.bank_name_id.int_contact

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
    contact = fields.Char('Bank Name')
    company_name = fields.Char('Name')
    company_address = fields.Char('Address')
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
    commission_percentage = fields.Float(string='% Age')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    sequence = fields.Integer(string='Sequence', default=10)


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


class SaleCommissionPayment(models.Model):
    _name = "sale.commission.payment"
    _description = "Sale Commission Payment"

    name = fields.Text(string="Name")
    amount = fields.Float(string="Payment Amount")
    journal_id = fields.Many2one("account.journal", string="Payment Journal")
    payment_date = fields.Date(string="Payment Date")
    currency_id = fields.Many2one('res.currency', 'Currency')
    company_id = fields.Many2one("res.company")
    commission_id = fields.Many2one("sale.commission.report")

    @api.model
    def default_get(self, fields):
        res = super(SaleCommissionPayment, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        commission_id = self.env["sale.commission.report"].sudo().browse(res_ids)
        res.update({'amount': commission_id.total_due,
                    'payment_date': datetime.now().date(),
                    'name': commission_id.name,
                    'currency_id': commission_id.currency_id.id,
                    'company_id': commission_id.company_id.id,
                    'commission_id': commission_id.id
                    })
        return res

    def validate_payment(self):
        if self.amount <= 0:
            raise ValidationError("Amount should not be lesser than or equal to zero")
        payment_method = self.env["account.payment.method"].sudo().search([('code', '=', 'manual'),
                                                                           ('payment_type', '=', 'inbound')])
        vals = {
            'partner_type': 'customer',
            'payment_type': 'inbound',
            'payment_method_id': payment_method.id,
            'partner_id': self.company_id.partner_id.id,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'payment_date': self.payment_date,
            'name': self.name,
            'company_id': self.company_id.id,
            'total_commission': self.commission_id.total_commission,
            'commission_id': self.commission_id.id
        }
        self.env["commission.payment.history"].sudo().create(vals)
        self.commission_id.update({'state': 'paid', 'total_due': self.commission_id.total_due - self.amount})


class CommissionPaymentHistory(models.Model):
    _name = "commission.payment.history"
    _description = "Commission Payment History"

    name = fields.Text(string="Name")
    amount = fields.Float(string="Paid Amount")
    journal_id = fields.Many2one("account.journal", string="Payment Journal")
    payment_date = fields.Date(string="Payment Date")
    currency_id = fields.Many2one('res.currency', 'Currency')
    company_id = fields.Many2one("res.company")
    commission_id = fields.Many2one("sale.commission.report")
    total_commission = fields.Float(string="Total Commission")
