# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo import tools
from datetime import datetime, date, time
import calendar


def get_years():
    year_list = []
    for i in range(2016, 2036):
        year_list.append((i, str(i)))
    return year_list


class InvoiceCustomerStatusWizard(models.TransientModel):
    _name = 'invoice.customer.wizard'
    _description = 'Wizard Customer Status'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True)
    partner_ids = fields.Many2many('res.partner', string='Customers')
    customer_id = fields.Many2one('res.partner', string='Customer')
    date_from = fields.Date('Date to', compute='get_date')
    date_to = fields.Date('Date to', compute='get_date')
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')],
                             string='Month')
    year = fields.Selection(get_years(), string='Year', )
    month_to = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                                 (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                                 (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')],
                                string='Month')
    year_to = fields.Selection(get_years(), string='Year', )

    def get_date(self):
        if self.month and self.year and self.month_to and self.year:
            self.update({'date_from': date.today().replace(day=1, month=self.month, year=self.year),
                         'date_to': date.today().replace(day=calendar.monthrange(self.year_to, self.month_to)[1], month=self.month_to, year=self.year_to)})
            return True

    # Function call to generate report
    @api.multi
    def invoice_pivot_view(self):
        ctx = self.env.context.copy()
        ctx.update({'invoice_form_id': self.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'partner_ids': self.partner_ids.ids,
                    })
        print('**************CTX', ctx)
        return {
            'name': _('Invoice Pivot View'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.report',
            'view_type': 'form',
            'view_mode': 'pivot',
            'view_id': self.env.ref('account.view_account_invoice_report_pivot').id,
            'target': 'current',
            'context': self.env['account.invoice.report'].with_context(ctx).init(),
        }


class InvoiceCustomerStatusForm(models.Model):
    _name = 'invoice.customer.form'
    _description = 'Customer Status'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True)
    partner_ids = fields.Many2many('res.partner', string='Customers')
    customer_id = fields.Many2one('res.partner', string='Customer')
    date_from = fields.Date('Date to', compute='get_date')
    date_to = fields.Date('Date to', compute='get_date')
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')],
                             string='Month')
    year = fields.Selection(get_years(), string='Year', )
    month_to = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                                 (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                                 (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')],
                                string='Month')
    year_to = fields.Selection(get_years(), string='Year', )

    def get_date(self):
        if self.month and self.year and self.month_to and self.year:
            self.update({'date_from': date.today().replace(day=1, month=self.month, year=self.year),
                         'date_to': date.today().replace(day=calendar.monthrange(self.year_to, self.month_to)[1], month=self.month_to, year=self.year_to)})
            print('********DATES**********', self.date_to, self.date_from)
            return True

    # Function call to generate report
    @api.multi
    def invoice_pivot_view(self):
        ctx = self.env.context.copy()
        ctx.update({'invoice_form_id': self.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to, })
        print('**************CTX', ctx)
        return {
            'name': _('Invoice Pivot View'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.report',
            'view_type': 'form',
            'view_mode': 'pivot',
            'view_id': self.env.ref('account.view_account_invoice_report_pivot').id,
            'target': 'current',
            'context': self.env['account.invoice.report'].with_context(ctx).init(),
        }


class AccountInvoiceReportInherit(models.Model):
    _inherit = "account.invoice.report"

    invoice_form_id = fields.Many2one('invoice.customer.form', 'Form ID')
    partner_ids = fields.Many2many('res.partner', string='Customers')
    date_from = fields.Date('Date to', compute='get_date')
    date_to = fields.Date('Date to', compute='get_date')

    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                JOIN res_partner partner_ai ON ai.partner_id = partner_ai.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                LEFT JOIN invoice_customer_form icf ON icf.id = %s
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN uom_uom u ON u.id = ail.uom_id
                LEFT JOIN uom_uom u2 ON u2.id = pt.uom_id
                JOIN (
                    -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Credit Note)
                    SELECT id,(CASE
                         WHEN ai.type::text = ANY (ARRAY['in_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign,(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign_qty
                    FROM account_invoice ai
                ) AS invoice_type ON invoice_type.id = ai.id
        """ % self.env.context.get('invoice_form_id')
        return from_str

    def _select(self):
        select_str = """
              SELECT sub.id, sub.number, sub.date, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
                  sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
                  sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.invoice_id, sub.type, sub.state,
                  sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
                  sub.product_qty, sub.price_total as price_total, sub.price_average as price_average, sub.amount_total / COALESCE(cr.rate, 1) as amount_total,
                  COALESCE(cr.rate, 1) as currency_rate, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id
          """
        return select_str

    def _sub_select(self):
        select_str = """
                  SELECT ail.id AS id,
                       ai.date_invoice AS date,
                      ai.number as number,
                      ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
                      u2.name AS uom_name,
                      ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id,
                      1 AS nbr,
                      ai.id AS invoice_id, ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                      ai.partner_bank_id,
                      SUM ((invoice_type.sign_qty * ail.quantity) / COALESCE(u.factor,1) * COALESCE(u2.factor,1)) AS product_qty,
                      SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
                      SUM(ail.price_total * invoice_type.sign_qty) AS amount_total,
                      SUM(ABS(ail.price_subtotal_signed)) / CASE
                              WHEN SUM(ail.quantity / COALESCE(u.factor,1) * COALESCE(u2.factor,1)) <> 0::numeric
                                 THEN SUM(ail.quantity / COALESCE(u.factor,1) * COALESCE(u2.factor,1))
                                 ELSE 1::numeric
                              END AS price_average,
                      ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                      count(*) * invoice_type.sign AS residual,
                      ai.commercial_partner_id as commercial_partner_id,
                      coalesce(partner.country_id, partner_ai.country_id) AS country_id
          """
        return select_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        if self.env.context.get('invoice_form_id', False):
            partner = tuple([element for element in self.env.context.get('partner_ids')])
            if len(partner) > 1:
                print("get Context of Wizard HERE", self.env.context.get('invoice_form_id'),
                      type(self.env.context.get('date_from')),
                      self.env.context.get('partner_ids'),
                      tuple(self.env.context.get('partner_ids')), str(self.env.context.get('date_from')))

                tools.drop_view_if_exists(self.env.cr, self._table)

                self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                    WITH currency_rate AS (%s)
                    %s
                    FROM (
                            %s %s WHERE ail.account_id IS NOT NULL and ai.date_invoice >= '%s' 
                        and ai.date_invoice <= '%s' and ai.partner_id in %s %s
                    ) AS sub
                    LEFT JOIN currency_rate cr ON
                        (cr.currency_id = sub.currency_id AND
                         cr.company_id = sub.company_id AND
                         cr.date_start <= COALESCE(sub.date, NOW()) AND
                         (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
                )""" % (
                    self._table, self.env['res.currency']._select_companies_rates(),
                    self._select(), self._sub_select(), self._from(),
                    str(self.env.context.get('date_from')),
                    str(self.env.context.get('date_to')),
                    tuple(self.env.context.get('partner_ids')), self._group_by()))
            else:
                print("ELSEEEEEEEEEEEEEEEEEEEE", self.env.context.get('invoice_form_id'),
                      type(self.env.context.get('date_from')),
                      self.env.context.get('partner_ids'),
                      tuple(self.env.context.get('partner_ids')), str(self.env.context.get('date_from')))

                tools.drop_view_if_exists(self.env.cr, self._table)

                self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                                    WITH currency_rate AS (%s)
                                    %s
                                    FROM (
                                            %s %s WHERE ail.account_id IS NOT NULL and ai.date_invoice >= '%s' 
                                        and ai.date_invoice <= '%s' and ai.partner_id = %s %s
                                    ) AS sub
                                    LEFT JOIN currency_rate cr ON
                                        (cr.currency_id = sub.currency_id AND
                                         cr.company_id = sub.company_id AND
                                         cr.date_start <= COALESCE(sub.date, NOW()) AND
                                         (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
                                )""" % (
                    self._table, self.env['res.currency']._select_companies_rates(),
                    self._select(), self._sub_select(), self._from(),
                    str(self.env.context.get('date_from')),
                    str(self.env.context.get('date_to')),
                    ','.join(map(repr, partner)), self._group_by()))
