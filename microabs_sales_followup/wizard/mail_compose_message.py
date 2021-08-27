from odoo import models, fields, api, _


class SaleFollowup(models.Model):
    _name = 'sale.followup'
    _description = "Invoice Followup"
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        res = super(SaleFollowup, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        sales_ids = self.env["sale.order"].sudo().browse(res_ids[0])
        # invoice_ids = self.env['account.invoice'].browse(self._context.get('active_ids'))
        email_to = sales_ids.partner_id.so_email_to
        email_cc = sales_ids.partner_id.so_email_cc
        email_subject = 'Order Request Form - %s - %s - %s - %s' % (sales_ids.partner_id.name,
                                                                    sales_ids.partner_id.city,
                                                                    sales_ids.po_no,
                                                                    sales_ids.po_date.strftime("%d-%m-%Y") if sales_ids.po_date else " ")
        attachments = self.env['ir.attachment'].search(
            [('res_id', '=', sales_ids.id), ('res_model', '=', 'sale.order')]).ids
        res.update({
            'email_cc': email_cc if email_cc else "",
            'email_to': email_to,
            'email_subject': email_subject,
            'email_attachment_ids': attachments
        })
        print('**********************', res)
        partner = ""
        for inv in sales_ids.partner_id.so_email_to_ids:
            title = sales_ids.partner_id.title.name if sales_ids.partner_id.title else inv.title.name
            print('title', title)
            partner += title + " " + inv.name + "/"
        partner = partner[:-1] if partner else "Customer"
        message = "<p>Dear %s,</p>" % partner
        message += "<p>Greetings of the day!<br/></p>"
        message += "<p>Pl. find the enclosed PO. %s dtd %s received from %s on %s " \
                   "Our corresponding Order Request Number is %s <br/>Kindly acknowledge the receipt of this order.</p>" \
                   % (sales_ids.po_no, sales_ids.po_date.strftime("%d-%m-%Y") if sales_ids.po_date else " ",
                      sales_ids.partner_id.name if sales_ids.partner_id.name else " ",
                      sales_ids.po_received_date.strftime("%d-%m-%Y") if sales_ids.po_received_date else " ", sales_ids.name)
        message += "<p>The delivery week required by the customer is mentioned in the enclosed Order Request form.<br/>"
        message += "Pl. let us know your Delivery week and packing list.<br/>"
        message += "Kindly let us know in case of any queries.</p>"
        message += "<p>Regards,<br/>"
        message += "<b>ERP Team.</b><br/>"
        message += "%s <br/>" % sales_ids.company_id.name
        message += "%s, <br/>" % sales_ids.company_id.street if sales_ids.company_id.street else ""
        message += "%s, <br/>" % sales_ids.company_id.street2 if sales_ids.company_id.street2 else ""
        message += "%s, <br/>" % sales_ids.company_id.city if sales_ids.company_id.city else ""
        message += "%s, <br/>" % sales_ids.company_id.state_id.name if sales_ids.company_id.state_id else ""
        message += "%s - %s. </p>" % (
            sales_ids.company_id.country_id.name if sales_ids.company_id.country_id else "",
            sales_ids.company_id.zip if sales_ids.company_id.zip else "")
        res.update({
            'email_body': message,
            'sale_id': sales_ids.id
        })
        return res

    sale_id = fields.Many2one("sale.order", string="Invoice")
    email_cc = fields.Text('Cc', help="Carbon copy recipients (placeholders may be used here)",
                           default='saba@microab.com,srini@microab.com')
    email_to = fields.Text('To', help="Recipients Address (placeholders may be used here)")
    email_from = fields.Text(string="From")
    reply_to = fields.Text(string="Reply To")
    email_subject = fields.Char(string="Subject")
    email_body = fields.Html(string="Email")
    email_attachment_ids = fields.Many2many('ir.attachment', string='')

    # Email function for sending mails
    @api.multi
    def send_email(self):
        mail_ids = []
        send_mail = self.env['mail.mail']
        res_ids = self._context.get('active_ids')
        sale_ids = self.env["sale.order"].sudo().browse(res_ids[0])
        body = _("%s" % self.email_body)
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
        sale_ids.message_post(body=body, attachment_ids=attachment_ids)
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)
