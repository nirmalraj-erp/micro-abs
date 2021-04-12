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
    currency_id = fields.Many2one("res.currency", string="Currency")
    email_body = fields.Html(string="Email")
    email_to = fields.Char(string="Email To")
    email_cc = fields.Char(string="Email CC")
    email_subject = fields.Char(string="Subject")
    state = fields.Selection([('draft', 'Waiting'), ('sent', 'Email Sent'), ('cancel', 'Cancel')], default="draft",
                             string="Status")

    @api.model
    def create_payment_followup(self):
        self.env.cr.execute(""" delete from payment_followup """)
        today = datetime.now().date()
        overdue_invoices = self.env["account.invoice"].sudo().search([('date_due', '<', str(today)),
                                                                      ('state', 'in', ('open', 'in_payment'))])
        pending_invoices = self.env["account.invoice"].sudo().search([('date_due', '>=', str(today)),
                                                                      ('state', 'in', ('open', 'in_payment'))])
        if pending_invoices:
            for inv in pending_invoices:
                res = self.env["payment.followup"].sudo().create({
                                                            'invoice_id': inv.id,
                                                            'partner_id': inv.partner_id.id,
                                                            'invoice_date': inv.date_invoice,
                                                            'due_date': inv.date_due,
                                                            'total_amount': inv.amount_total,
                                                            'due_amount': inv.residual,
                                                            'currency_id': inv.currency_id.id,
                                                            'email_to': inv.partner_id.email,
                                                            'email_cc': inv.partner_id.payment_cc,
                                                            'email_subject': inv.company_id.name + " - " + inv.partner_id.
                                                            name + " - " + " Overdue and Pending Invoice"
                                                            })
                message = "Dear %s, <br/>" % res.partner_id.name
                message += " <br/> Please find the below list of overdue/pending invoices. <br/>"
                message += "Please clear them at the earliest and kindly share swift copy once paid. <br/><br/>"

                message += "<b> Overdue Invoices: </b>"
                message += "<p> No overdue as on date. </p>"
                message += "<br/><br/>"

                message += "<b> Pending Invoices: </b>"
                message += "<p> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </p>" % (res.invoice_id.number,
                                                                                          res.invoice_date.strftime("%d-%m-%Y"),
                                                                                          res.currency_id.name,
                                                                                          res.due_amount,
                                                                                          res.due_date.strftime("%d-%m-%Y"))
                message += "<br/><br/>"
                message += "Regards, <br/> ERP Team. <br/>"
                message += "%s, " % res.partner_id.street
                message += "%s, <br/>" % res.partner_id.street2
                message += "%s, " % res.partner_id.city
                message += "%s, <br/>" % res.partner_id.state_id.name
                message += "%s - %s. " % (res.partner_id.country_id.name, res.partner_id.zip)
                res.email_body = message

        if overdue_invoices:
            for inv in overdue_invoices:
                res = self.env["payment.followup"].sudo().create({
                    'invoice_id': inv.id,
                    'partner_id': inv.partner_id.id,
                    'invoice_date': inv.date_invoice,
                    'due_date': inv.date_due,
                    'total_amount': inv.amount_total,
                    'due_amount': inv.residual,
                    'currency_id': inv.currency_id.id,
                    'email_to': inv.partner_id.email,
                    'email_cc': inv.partner_id.payment_cc,
                    'email_subject': inv.company_id.name + " - " + inv.partner_id.name + " - " + " "
                    "Overdue and Pending Invoice"
                })
                message = "Dear %s, <br/>" % res.partner_id.name
                message += " <br/> Please find the below list of overdue/pending invoices. <br/>"
                message += "Please clear them at the earliest and kindly share swift copy once paid. <br/><br/>"

                message += "<b> Overdue Invoices: </b>"
                message += "<p <span style='color:red;'> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </span> " \
                           "</p>" \
                           % (res.invoice_id.number,
                              res.invoice_date.strftime("%d-%m-%Y"),
                              res.currency_id.name,
                              res.due_amount,
                              res.due_date.strftime("%d-%m-%Y"))
                message += "<br/><br/>"

                message += "<b> Pending Invoices: </b> <br/><br/>"
                message += " <p> No pending invoices as on date. </p>"
                message += "<br/><br/>"
                message += "Regards, <br/> ERP Team. <br/>"
                message += "%s, " % res.partner_id.street
                message += "%s, <br/>" % res.partner_id.street2
                message += "%s, " % res.partner_id.city
                message += "%s, <br/>" % res.partner_id.state_id.name
                message += "%s - %s. " % (res.partner_id.country_id.name, res.partner_id.zip)
                res.email_body = message

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
