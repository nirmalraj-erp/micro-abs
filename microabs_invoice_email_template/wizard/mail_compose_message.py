from odoo import models, fields, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields_list):
        res = super(MailComposeMessage, self).default_get(fields_list)
        if self._context.get('active_model') == 'account.invoice':
            if self._context.get('active_ids'):
                invoice_ids = self.env['account.invoice'].browse(self._context.get('active_ids'))
                email_to = invoice_ids.partner_id.docs_to
                email_cc = invoice_ids.partner_id.docs_cc
                res['email_cc'] = email_cc
                res['email_to'] = email_to
        return res

    email_cc = fields.Char('Cc', help="Carbon copy recipients (placeholders may be used here)")
    email_to = fields.Char('To', help="Recipients Address (placeholders may be used here)")


