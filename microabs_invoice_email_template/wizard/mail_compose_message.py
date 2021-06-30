from odoo import models, fields, api, _


class InvoiceFollowup(models.Model):
    _name = 'invoice.followup'
    _description = "Invoice Followup"

    @api.model
    def default_get(self, fields):
        res = super(InvoiceFollowup, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        invoice_ids = self.env["account.invoice"].sudo().browse(res_ids[0])
        # invoice_ids = self.env['account.invoice'].browse(self._context.get('active_ids'))
        email_to = invoice_ids.partner_id.docs_to
        email_cc = invoice_ids.partner_id.docs_cc
        email_subject = str(invoice_ids.partner_id.name) + '-' + str(invoice_ids.shipment_mode.name) + 'Shipment' + '-' + 'Inv.' + str(invoice_ids.invoice_number) + '-' + 'PO.' + str(invoice_ids.po_no)
        attachments = self.env['ir.attachment'].search(
                [('res_id', '=', invoice_ids.id), ('res_model', '=', 'account.invoice')]).ids
        res.update({
            'email_cc': "erp@microab.com, " + email_cc if email_cc else "erp@microab.com, ",
            'email_to': email_to,
            'email_subject': email_subject,
            'email_attachment_ids': attachments
        })
        print('**********************', res)
        partner = ""
        for inv in invoice_ids.partner_id.docs_to_ids:
            partner += "Mr." + inv.name + "/"
        partner = partner[:-1] if partner else "Customer"
        message = "Dear %s," % partner
        message += "<br/><br/>"
        message += "We send you herewith a copy of our invoice no. <b>%s</b>, %s %s packing list and manufacturer's " \
                   "certificates of origin, corresponding to the %s shipment of %s's P.O. %s" \
                   % (invoice_ids.invoice_number, invoice_ids.email_shipment_string or '',
                      invoice_ids.bl_no or '',
                      invoice_ids.shipment_mode.name, invoice_ids.partner_id.name, invoice_ids.po_no)
        message += "<br/><br/>"
        message += "<p>Regards, <br/>" \
                   "<b> ERP Team. </b><br/>" \
                   "%s <br/>" \
                   "%s, %s<br/>" \
                   "%s, %s<br/>" \
                   "%s<br/>" \
                   "%s<br/>" \
                   "<u>%s</u></p>" % (invoice_ids.company_id.name, invoice_ids.company_id.street or '',
                                      invoice_ids.company_id.street2 or '', invoice_ids.company_id.city or '',
                                      invoice_ids.company_id.state_id.name or '',
                                      invoice_ids.company_id.country_id.name or '',
                                      invoice_ids.company_id.phone or '',
                                      invoice_ids.company_id.website_address or '')
        res.update({
            'email_body': message,
            'invoice_id': invoice_ids.id
        })
        return res

    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    email_cc = fields.Text('Cc', help="Carbon copy recipients (placeholders may be used here)")
    email_to = fields.Text('To', help="Recipients Address (placeholders may be used here)")
    email_subject = fields.Char(string="Subject")
    email_body = fields.Html(string="Email")
    email_attachment_ids = fields.Many2many('ir.attachment', string='')

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
            'attachment_ids': [(6, 0, self.email_attachment_ids.ids)],
            'body_html': '''<span  style="font-size:14px"><br/>
                         <br/>%s<br/>
                         </span>''' % body,
        }))
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)
