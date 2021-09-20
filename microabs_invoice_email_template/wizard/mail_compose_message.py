from odoo import models, fields, api, _


class InvoiceFollowup(models.Model):
    _name = 'invoice.followup'
    _description = "Invoice Followup"
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        res = super(InvoiceFollowup, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        invoice_ids = self.env["account.invoice"].sudo().browse(res_ids[0])
        # invoice_ids = self.env['account.invoice'].browse(self._context.get('active_ids'))
        email_to = invoice_ids.partner_id.docs_to
        email_cc = invoice_ids.partner_id.docs_cc
        email_subject = str(invoice_ids.partner_id.name) + ' ' + '-' + ' ' + str(
            invoice_ids.shipment_mode.name) + ' ' + 'Shipment' + ' ' + '-' + ' ' + 'Inv.' + ' ' + str(
            invoice_ids.invoice_number) + ' ' + '-' + ' ' + 'PO.' + ' ' + str(invoice_ids.po_no)
        attachments = self.env['ir.attachment'].search(
            [('res_id', '=', invoice_ids.id), ('res_model', '=', 'account.invoice')]).ids
        res.update({
            'email_cc': email_cc if email_cc else "",
            'email_to': email_to,
            'email_subject': email_subject,
            'email_attachment_ids': attachments
        })
        print('**********************', res)
        partner = ""
        for inv in invoice_ids.partner_id.docs_to_ids:
            partner += inv.title.name if inv.title else " " + " " + inv.name + "/"
        partner = partner[:-1] if partner else "Customer"
        message = "<p>Dear  %s, <br/></p>" % partner
        message += "<p>We send you herewith a copy of our invoice no. <b>%s</b>, %s %s packing list and manufacturer's " \
                   "certificates of origin, corresponding to the %s shipment of %s's P.O. %s</p>" \
                   % (invoice_ids.invoice_number, invoice_ids.email_shipment_string or '',
                      invoice_ids.bl_no or '',
                      invoice_ids.shipment_mode.name, invoice_ids.partner_id.name, invoice_ids.po_no)
        # message += "<br/>"
        message += "<p>Regards,<br/>"
        message += "<b>ERP Team.</b><br/>"
        message += "%s <br/>" % invoice_ids.company_id.name
        message += "%s, <br/>" % invoice_ids.company_id.street if invoice_ids.company_id.street else ""
        message += "%s, <br/>" % invoice_ids.company_id.street2 if invoice_ids.company_id.street2 else ""
        message += "%s, <br/>" % invoice_ids.company_id.city if invoice_ids.company_id.city else ""
        message += "%s, <br/>" % invoice_ids.company_id.state_id.name if invoice_ids.company_id.state_id else ""
        message += "%s - %s. </p>" % (
            invoice_ids.company_id.country_id.name if invoice_ids.company_id.country_id else "",
            invoice_ids.company_id.zip if invoice_ids.company_id.zip else "")
        res.update({
            'email_body': message,
            'invoice_id': invoice_ids.id
        })
        return res

    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    email_cc = fields.Text('Cc', help="Carbon copy recipients (placeholders may be used here)")
    email_to = fields.Text('To', help="Recipients Address (placeholders may be used here)")
    email_from = fields.Text(string="From")
    reply_to = fields.Text(string="Reply To", default='saba@microab.com,srini@microab.com')
    email_subject = fields.Char(string="Subject")
    email_body = fields.Html(string="Email")
    email_attachment_ids = fields.Many2many('ir.attachment', string='')

    # Email function for sending mails
    @api.multi
    def send_email(self):
        mail_ids = []
        send_mail = self.env['mail.mail']
        res_ids = self._context.get('active_ids')
        invoice_ids = self.env["account.invoice"].sudo().browse(res_ids[0])
        body = _("%s" % self.email_body)
        user_id = self.env.user.name
        attachment_ids = self.email_attachment_ids.ids
        mail_ids.append(send_mail.create({
            'email_from': 'erp@microab.com',
            'email_to': self.email_to,
            'email_cc': self.email_cc,
            'reply_to': self.reply_to,
            'subject': self.email_subject,
            'attachment_ids': [(6, 0, self.email_attachment_ids.ids)],
            'body_html': '''<span  style="font-size:14px"><br/>
                         <br/>%s<br/>
                         </span>''' % body,
        }))
        invoice_ids.message_post(body=body + 'Triggered by: ' + user_id, attachment_ids=attachment_ids)
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)
