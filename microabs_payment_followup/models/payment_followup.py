from odoo import api, fields, models, _


class PaymentFollowup(models.Model):
    _name = "payment.followup"
    _description = "Payment Followup"

    move_id = fields.Many2one(string="account.move")
    partner_id = fields.Many2one(string="res.partner")
    invoice_date = fields.Date(string="Invoice Date")
    due_date = fields.Date(string="Due Date")
    total_amount = fields.Float(string="Total Amount")
    due_amount = fields.Float(string="Due Amount")
    email_body = fields.Html(string="Email")

    @api.multi
    def send_email(self):
        print('1111111111111111111')
