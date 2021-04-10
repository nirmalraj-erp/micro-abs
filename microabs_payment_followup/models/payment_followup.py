from odoo import api, fields, models, _
from datetime import datetime, date, time
from datetime import timedelta
from dateutil import relativedelta as rdelta


class PaymentFollowup(models.Model):
    _name = "payment.followup"
    _description = "Payment Followup"
    _rec_name = "invoice_id"

    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    partner_id = fields.Many2one("res.partner", string="Customer")
    invoice_date = fields.Date(string="Invoice Date")
    due_date = fields.Date(string="Due Date")
    total_amount = fields.Float(string="Total Amount")
    due_amount = fields.Float(string="Due Amount")
    email_body = fields.Html(string="Email")

    @api.model
    def create_payment_followup(self):
        self.env.cr.execute(""" delete from payment_followup """)
        today = datetime.now().date()
        previous_date = datetime.strptime(str(today),("%Y-%m-%d")) + rdelta.relativedelta(days=-2)
        previous_date = previous_date.strftime("%Y-%m-%d")
        invoices = self.env["account.invoice"].sudo().search([('date_due', '>=', previous_date),
                                                              ('date_due', '<=', str(today)),
                                                              ('state', '=', 'open')])
        for inv in invoices:
            self.env["payment.followup"].sudo().create({
                                                        'invoice_id': inv.id,
                                                        'partner_id': inv.partner_id.id,
                                                        'invoice_date': inv.date_invoice,
                                                        'due_date': inv.date_due,
                                                        'total_amount': inv.amount_total,
                                                        'due_amount': inv.residual
                                                        })
            inv.update({'payment_reminder_email': True})

    # Email function for sending mails
    @api.multi
    def send_email(self):
        mail_ids = []
        send_mail = self.env['mail.mail']
        email_to = self.partner_id.email
        subject = "Payment Followup"
        body = _("Dear %s," % self.partner_id.name)
        body += _("%s" % self.email_body)
        footer = "With Regards,<br/>Admin"
        mail_ids.append(send_mail.create({
            'email_to': email_to,
            'subject': subject,
            'body_html': '''<span  style="font-size:14px"><br/>
                        <br/>%s<br/>
                        <br/>%s</span>''' % (body, footer),
        }))
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)
