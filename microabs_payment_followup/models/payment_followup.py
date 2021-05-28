from odoo import api, fields, models, _
from datetime import datetime, date, time
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from dateutil import relativedelta as rdelta


class PaymentFollowup(models.Model):
    _name = "payment.followup"
    _description = "Payment Followup"
    _rec_name = "invoice_id"
    _order = "due_date"

    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    invoice_ids = fields.Many2many("account.invoice", string="Invoice")
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
                             string="Email Status")
    due_status = fields.Selection([('overdue', 'Overdue'), ('pending', 'Pending Invoice'), ('paid', 'Paid')],
                                  default="pending", string="Due Status")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))

    @api.model
    def default_get(self, fields):
        res = super(PaymentFollowup, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        partner_list = []
        invoice_list = []
        partner = self.env["account.invoice"].sudo().browse(res_ids)
        for i in partner:
            invoice_list.append(i.id)
            if i.partner_id.id not in partner_list and len(partner_list) >= 1:
                raise ValidationError("Different Partner's have been selected. Kindly select records of same partner..!")
            else:
                partner_list.append(i.partner_id.id)
        invoice_id = self.env["account.invoice"].sudo().browse(res_ids[0])
        res.update({
            'email_to': invoice_id.partner_id.payment_to,
            'email_cc': invoice_id.partner_id.payment_cc,
            'email_subject': invoice_id.company_id.name + " - " + invoice_id.partner_id.name + " - " +
            " Overdue and Pending Invoice",
            "invoice_ids": [(6, 0, invoice_list)]
        })
        partner = ""
        for inv in invoice_id.partner_id.payment_to_ids:
            partner += "Mr." + inv.name + "/"

        today = datetime.now().date()
        overdue_invoices = self.env["account.invoice"].sudo().search([('date_due', '<', str(today)),
                                                                      ('id', 'in', invoice_list),
                                                                      ('state', 'in', ('open', 'in_payment'))])
        pending_invoices = self.env["account.invoice"].sudo().search([('date_due', '>=', str(today)),
                                                                      ('id', '=', invoice_list),
                                                                      ('state', 'in', ('open', 'in_payment'))])
        partner = partner[:-1] if partner else "Customer"
        message = "Dear %s, <br/>" % partner
        message += " <br/> Please find the below list of overdue/pending invoices. <br/>"
        message += "Please clear them at the earliest and kindly share swift copy once paid. <br/><br/>"

        if overdue_invoices:
            message += "<b> Overdue: </b>"
            for due in overdue_invoices:
                message += "<p <span style='color:red;'> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </span> " \
                           "</p>" \
                           % (due.invoice_number,
                              due.date_invoice.strftime("%d-%m-%Y"),
                              due.currency_id.name,
                              due.residual,
                              due.date_due.strftime("%d-%m-%Y"))
        else:
            message += "<b> Overdue: </b>"
            message += "<p> No overdue as on date. </p>"

        if pending_invoices:
            message += "<br/>"
            message += "<b> Pending Invoices: </b>"
            for pen in pending_invoices:
                message += "<p> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </p>" % (pen.invoice_number,
                                                                                          pen.date_invoice.strftime("%d-%m-%Y"),
                                                                                          pen.currency_id.name,
                                                                                          pen.residual,
                                                                                          pen.date_due.strftime("%d-%m-%Y"))
        else:
            message += "<br/>"
            message += "<b> Pending Invoices: </b>"
            message += " <p> No pending invoices as on date. </p>"

        message += "<br/><br/>"
        message += "Regards, <br/> ERP Team. <br/>"
        message += "%s, " % invoice_id.company_id.street if invoice_id.company_id.street else ""
        message += "%s, <br/>" % invoice_id.company_id.street2 if invoice_id.company_id.street2 else ""
        message += "%s, " % invoice_id.company_id.city if invoice_id.company_id.city else ""
        message += "%s, <br/>" % invoice_id.company_id.state_id.name if invoice_id.company_id.state_id else ""
        message += "%s - %s. " % (invoice_id.company_id.country_id.name if invoice_id.company_id.country_id else "", invoice_id.company_id.zip if invoice_id.company_id.zip else "")
        res.update({
                'email_body': message,
                'invoice_id': invoice_id.id
                })
        return res

    @api.model
    def create_payment_followup(self):
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
                                                            'due_status': 'pending',
                                                            'invoice_date': inv.date_invoice,
                                                            'due_date': inv.date_due,
                                                            'total_amount': inv.amount_total,
                                                            'due_amount': inv.residual,
                                                            'currency_id': inv.currency_id.id,
                                                            'email_to': inv.partner_id.payment_to,
                                                            'email_cc': inv.partner_id.payment_cc,
                                                            'email_subject': inv.company_id.name + " - " + inv.partner_id.
                                                            name + " - " + " Overdue and Pending Invoice"
                                                            })
                message = "Dear %s, <br/>" % res.partner_id.name
                message += " <br/> Please find the below list of overdue/pending invoices. <br/>"
                message += "Please clear them at the earliest and kindly share swift copy once paid. <br/><br/>"

                message += "<b> Overdue: </b>"
                message += "<p> No overdue as on date. </p>"
                message += "<br/>"

                message += "<b> Pending Invoices: </b>"
                message += "<p> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </p>" % (res.invoice_id.invoice_number,
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
                    'due_status': 'overdue',
                    'invoice_date': inv.date_invoice,
                    'due_date': inv.date_due,
                    'total_amount': inv.amount_total,
                    'due_amount': inv.residual,
                    'currency_id': inv.currency_id.id,
                    'email_to': inv.partner_id.email,
                    'email_cc': inv.partner_id.payment_cc,
                    'email_subject': inv.company_id.name if inv.company_id else '' + " - " + inv.partner_id.name if inv.partner_id else '' + " - " + " "
                    "Overdue and Pending Invoice"
                })
                message = "Dear %s, <br/>" % res.partner_id.name
                message += " <br/> Please find the below list of overdue/pending invoices. <br/>"
                message += "Please clear them at the earliest and kindly share swift copy once paid. <br/><br/>"

                message += "<b> Overdue: </b>"
                message += "<p <span style='color:red;'> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </span> " \
                           "</p>" \
                           % (res.invoice_id.invoice_number,
                              res.invoice_date.strftime("%d-%m-%Y"),
                              res.currency_id.name,
                              res.due_amount,
                              res.due_date.strftime("%d-%m-%Y"))
                message += "<br/>"

                message += "<b> Pending Invoices: </b>"
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
        body = _("%s" % self.email_body)
        mail_ids.append(send_mail.create({
            'email_to': self.email_to,
            'email_cc': self.email_cc,
            'subject': self.email_subject,
            'body_html': '''<span  style="font-size:14px"><br/>
                        <br/>%s<br/>
                        </span>''' % body,
        }))
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)
        for inv in self.invoice_ids:
            follow_date = datetime.today()
            inv.followup_date = follow_date.strftime("%d-%m-%y %H:%M:%S")
