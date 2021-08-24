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
    email_to = fields.Text(string="To")
    email_cc = fields.Text(string="CC", default='saba@microab.com,srini@microab.com')
    email_from = fields.Text(string="From")
    reply_to = fields.Text(string="Reply To")
    email_subject = fields.Char(string="Sub")
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
                raise ValidationError(
                    "Different Partner's have been selected. Kindly select records of same partner..!")
            else:
                partner_list.append(i.partner_id.id)
        invoice_id = self.env["account.invoice"].sudo().browse(res_ids[0])
        cc = res.get('email_cc')
        payment_cc = invoice_id.partner_id.payment_cc if invoice_id.partner_id.payment_cc else "saba@microab.com,srini@microab.com"
        company = invoice_id.company_id.name if invoice_id.company_id else ''
        partner = invoice_id.partner_id.name if invoice_id.partner_id else ''
        res.update({
            'email_to': invoice_id.partner_id.parent_id.payment_to if invoice_id.partner_id.parent_id.payment_to else invoice_id.partner_id.payment_to,
            'email_cc': str(cc) + ',' + payment_cc,
            'email_subject': company + " - " + partner + " - " + " Overdue and Pending Invoice",
            "invoice_ids": [(6, 0, invoice_list)]
        })
        partner = ""
        for inv in invoice_id.partner_id.payment_to_ids:
            title = invoice_id.partner_id.title.name if invoice_id.partner_id.title else inv.title.name
            partner += title + " " + inv.name + "/"
        today = datetime.now().date()
        overdue_invoices = self.env["account.invoice"].sudo().search([('date_due', '<', str(today)),
                                                                      ('id', 'in', invoice_list),
                                                                      ('state', 'in', ('open', 'in_payment'))])
        pending_invoices = self.env["account.invoice"].sudo().search([('date_due', '>=', str(today)),
                                                                      ('id', '=', invoice_list),
                                                                      ('state', 'in', ('open', 'in_payment'))])
        message = "<p style='font-size:15px;'>MATTER URGENT!</p>"
        partner = partner[:-1] if partner else "Customer"
        message += "<p style='font-size:15px;'>Dear %s,</p>" % partner
        message += "<span style='font-size:15px;'>We sincerely thank you for" \
                   " your POs and also " \
                   "for the continuous patronage to us.</span>"
        message += "<br/><span style='font-size:15px;'>" \
                   "Pl. find the below list of overdue/pending invoices." \
                   " </span>"
        message += "<br/><span style='font-size:15px;'> Pl. clear them at the earliest " \
                   "<span style='font-size:15px;'> ON TOP PRIORITY </span> " \
                   "and kindly share swift copy once paid.</span><br/><br/>"

        if overdue_invoices:
            message += "<b style='font-size:15px;'><u> OVERDUE INVOICES: <u></b><br/>"
            for due in overdue_invoices:
                overdue_days = (today - due.date_due).days
                message += "<p> <span style='font-size:15px;'>" \
                           "Already overdue since the past %s days.</span><br/>" % overdue_days
                message += "<span style='color:red;font-size:15px;'> " \
                           "<b>PO. %s Inv. %s dtd. %s for %s %s - Due Date %s, Delay Days %s</b></span></p> " % (
                               due.po_no,
                               due.invoice_number,
                               due.date_invoice.strftime("%d-%m-%Y"),
                               due.currency_id.name,
                               due.residual,
                               due.date_due.strftime("%d-%m-%Y"),
                               overdue_days)

            message += "<p> <span style='font-size:15px; background-color: #FFFF00;color: " \
                       "black;'>" \
                       "Pl. clear all " \
                       "the overdue invoices with " \
                       "immediate effect.</mark></span></p>"

        else:
            message += "<b style='font-size:15px;'><u> OVERDUE INVOICES: <u></b><br/>"
            message += "<br/><p style='font-size:15px;'> No overdue as on date. </p>"

        if pending_invoices:
            message += "<b style='font-size:15px;'><u> PENDING INVOICES: <u></b><br/>"
            for pen in pending_invoices:
                pending_days = -(today - pen.date_due).days
                message += "<p> <span style='font-size:15px'> This invoice will expire in " \
                           "%s</span><br/>" % pending_days
                message += "<span style='font-size:15px;'> " \
                           "<b>PO. %s Inv. %s dtd. %s for %s %s - Due Date %s, Days of Expiry %s</b></span></p>" % (
                               pen.po_no,
                               pen.invoice_number,
                               pen.date_invoice.strftime("%d-%m-%Y"),
                               pen.currency_id.name,
                               pen.residual,
                               pen.date_due.strftime("%d-%m-%Y"),
                               pending_days)
            message += "<p> <span style='font-size:15px; background-color: #FFFF00;color: " \
                       "black;'>" \
                       "Pl. clear all the pending invoices before the due date.</span> </p>"
        else:
            message += "<b style='font-size:15px;'><u> PENDING INVOICES: <u></b><br/>"
            message += "<br/> <p style='font-size:15px;'> No pending invoices as on date. </p> <br/>"

        message += "<b style='font-size:15px;color:red;'> CYBERCRIME ALERT: </b>"
        message += "<p style='font-size:15px;'>Please note that our bank account details have " \
                   "not changed and will not change. If you receive an email requesting funds " \
                   "via wire please contact us immediately over phone to Mr. Srini: +91 98840 38805 " \
                   "or Mr. Saba: +91 984 000 3937. We will never change our bank details via email." \
                   "In case of any changes, we will courier the hard copy of the bank details to you. " \
                   "Thank you in advance for your attention on this matter.</p>"
        message += "<b style='font-size:15px;color:red;'>PAYMENT ALERT</b>"
        message += "<p style='font-size:15px;'>When there is an overdue payment, " \
                   "our ERP system will put the Customer’s account under Embargo automatically." \
                   "In such cases we will not be able to dispatch shipments or accept your Purchase Orders. " \
                   "Hence, always, pl. make the payment on or before the due date.</p>"

        message += "<p style='font-size:15px;'>Regards,<br/>"
        message += "ERP Team.<br/>"
        message += "<b style='font-size:15px;'>%s</b> <br/>" % invoice_id.company_id.name
        message += "%s, <br/>" % invoice_id.company_id.street if invoice_id.company_id.street else ""
        message += "%s, <br/>" % invoice_id.company_id.street2 if invoice_id.company_id.street2 else ""
        message += "%s, <br/>" % invoice_id.company_id.city if invoice_id.company_id.city else ""
        message += "%s, <br/>" % invoice_id.company_id.state_id.name if invoice_id.company_id.state_id else ""
        message += "%s - %s. </p>" % (
            invoice_id.company_id.country_id.name if invoice_id.company_id.country_id else "",
            invoice_id.company_id.zip if invoice_id.company_id.zip else "")
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
                company = inv.company_id.name if inv.company_id else ''
                partner = inv.partner_id.name if inv.partner_id else ''
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
                    'email_subject': company + " - " + partner + " - " + " Overdue and Pending Invoice"
                })
                message = "Dear %s, <br/>" % res.partner_id.name
                message += " <br/> Please find the below list of overdue/pending invoices. <br/>"
                message += "Please clear them at the earliest and kindly share swift copy once paid. <br/><br/>"

                message += "<b> Overdue: </b>"
                message += "<p> No overdue as on date. </p>"
                message += "<br/>"

                message += "<b> Pending Invoices: </b>"
                message += "<p> <b> Inv. %s dtd. %s for %s %s - Due Date %s </b> </p>" % (res.invoice_id.invoice_number,
                                                                                          res.invoice_date.strftime(
                                                                                              "%d-%m-%Y"),
                                                                                          res.currency_id.name,
                                                                                          res.due_amount,
                                                                                          res.due_date.strftime(
                                                                                              "%d-%m-%Y"))
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
                company = inv.company_id.name if inv.company_id else ''
                partner = inv.partner_id.name if inv.partner_id else ''
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
                    'email_subject': company + " - " + partner + " - " + "Overdue and Pending Invoice"
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
            'email_from': 'erp@microab.com',
            'email_to': self.email_to,
            'email_cc': self.email_cc,
            'reply_to': self.reply_to,
            'subject': self.email_subject,
            'body_html': '''<span  style="font-size:12px"><br/>
                        <br/>%s<br/>
                        </span>''' % body,
        }))
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)
        for inv in self.invoice_ids:
            follow_date = datetime.today()
            if not inv.followup_date:
                inv.followup_date = str(follow_date.strftime("%d/%m/%Y"))
            else:
                inv.followup_date += ", " + str(follow_date.strftime("%d/%m/%Y"))
