# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class CommissionMaster(models.Model):
    _name = 'commission.master'
    _description = 'Commission Master'
    _rec_name = 'commission_percentage'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    commission_percentage = fields.Integer( string='Commission (%)')
    product_id = fields.Many2one('product.product', string='Product')


class SaleCommission(models.Model):
    _name = 'sale.commission'
    _description = 'Sale Commission'

    name = fields.Char(string='Agent')
    invoice_no = fields.Char(string='Invoice No.')
    invoice_date = fields.Date(string='Inv. Date')
    customer_code = fields.Char(string='Cust. Code')
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    invoice_amount = fields.Float(string='Inv. Amount')
    actual_received = fields.Float(string='Actually Received')
    commission_amount = fields.Float(string='Commission Amount')
    commission_percentage = fields.Integer(string='% Age')
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('paid', 'Paid')], string='Status', readonly=True,
                             copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')


class SaleOrderCommission(models.Model):
    _inherit = 'sale.order.line'

    commission_id = fields.Many2one('commission.master', string='Commission ID')
    commission_name = fields.Char(string='Commission')
    no_commission_required = fields.Boolean(string='Is Commission')
    commission_percentage = fields.Integer(string='Commission (%)')
    commission_amount = fields.Float(string='Commission Amount', compute='_get_commission_amount')
    commission_amount_wod = fields.Float(string='Commission Amount without Discount', compute='_get_commission_amount')

    @api.onchange('product_id')
    def get_commission_details(self):
        """Commission line based on commission master"""
        for line in self:
            if line.product_id:
                line.commission_percentage = self.order_id.partner_id.commission_percentage
                # commission_obj = self.env['commission.master'].search([('product_id', '=', line.product_id.id),
                #                                                        ('customer_id', '=', line.order_id.partner_id.id)])
                # line.commission_percentage = commission_obj.commission_percentage

    def _get_commission_amount(self):
        """Get the commission amount for the data given. To be called by
        compute methods of children models.
        """
        for line in self:
            if not line.no_commission_required:
                if line.commission_percentage:
                    price_total = line.product_uom_qty * line.price_unit
                    line.commission_amount_wod = price_total
                    commission_percentage = line.commission_amount_wod * line.commission_percentage
                    line.commission_amount = (commission_percentage / 100)


class SaleOrderCommissionInherit(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.commission_amount', 'order_line.commission_percentage')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            record.commission_percentage_total = 0.0
            for line in record.order_line:
                if not line.no_commission_required:
                    if line.commission_percentage:
                        record.total_taxed += sum(x.commission_amount_wod for x in line)
                        record.commission_total += sum(x.commission_amount for x in line)
                        if record.total_taxed != 0:
                            record.commission_percentage_total = (record.commission_total/record.total_taxed) * 100

    total_taxed = fields.Float(
        string="Total Excluding Freight",
        compute="_compute_commission_total",
        store=True,
    )
    commission_total = fields.Float(
        string="Commission Amount",
        compute="_compute_commission_total",
        store=True,
    )
    commission_percentage_total = fields.Float(
        string="Commission Percentage",
        compute="_compute_commission_total",
        store=True, digits=(12, 3),

    )


class AccountInvoiceLineCommission(models.Model):
    _inherit = 'account.invoice.line'

    commission_id = fields.Many2one('commission.master', string='Commission ID')
    commission_name = fields.Char(string='Commission')
    commission_percentage = fields.Integer(string='Commission (%)')
    commission_amount = fields.Float(string='Commission Amount', compute='_get_commission_amount')
    no_commission_required = fields.Boolean(string='Is Commission')

    def _get_commission_amount(self):
        """Get the commission amount for the data given. To be called by
        compute methods of children models.
        """
        for line in self:
            if line.commission_percentage:
                price_total = line.quantity * line.price_unit
                commission_percentage = price_total * line.commission_percentage
                line.commission_amount = (commission_percentage / 100)


class AccountInvoiceCommissionInherit(models.Model):
    _inherit = "account.invoice"

    @api.depends('invoice_line_ids.commission_amount', 'invoice_line_ids.commission_percentage')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            record.commission_percentage_total = 0.0
            for line in record.invoice_line_ids:
                if not line.no_commission_required:
                    record.total_taxed += sum(y.price_total for y in line)
                    record.commission_total += sum(x.commission_amount for x in line)
                    record.commission_percentage_total = (record.commission_total / record.total_taxed) * 100

    total_taxed = fields.Float(
        string="Total Excluding Freight",
        compute="_compute_commission_total",
        store=True,
    )

    commission_total = fields.Float(
        string="Commission Amount",
        compute="_compute_commission_total",
        store=True,
    )
    commission_percentage_total = fields.Float(
        string="Commission Percentage",
        compute="_compute_commission_total",
        store=True, digits=(12, 3),
    )

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(
                lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_(
                "You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _('No account was found to create the invoice, be sure you have installed a chart of account.'))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        to_open_invoices.action_commission_create()
        return to_open_invoices.invoice_validate()

    @api.multi
    def action_commission_create(self):
        if self.commission_percentage_total != 0:
            sale_commission = self.env['sale.commission']
            for inv in self:
                move_vals = {
                    'name': inv.partner_id.company_id.commission_agent,
                    'customer_id': inv.partner_id.id,
                    'invoice_no': inv.invoice_number,
                    'invoice_date': inv.date_invoice,
                    'customer_code': inv.partner_id.customer_code,
                    'invoice_amount': inv.amount_total,
                    'actual_received': inv.amount_total,
                    'commission_amount': inv.commission_total,
                    'commission_percentage': inv.commission_percentage_total,
                    'company_id': inv.company_id.id,
                    'currency_id': inv.currency_id.id,
                    'state': 'open',
                }
                return sale_commission.create(move_vals)

