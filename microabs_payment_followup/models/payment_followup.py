from odoo import api, fields, models, _


class PaymentFollowup(models.Model):
    _name = "payment.followup"
    _description = "Payment Followup"

    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    partner_id = fields.Many2one("res.partner", string="Customer")
    invoice_date = fields.Date(string="Invoice Date")
    due_date = fields.Date(string="Due Date")
    total_amount = fields.Float(string="Total Amount")
    due_amount = fields.Float(string="Due Amount")
    email_body = fields.Html(string="Email")

    @api.multi
    def send_email(self):
        print('1111111111111111111')
