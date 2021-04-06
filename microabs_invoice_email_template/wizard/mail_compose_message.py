##############################################################################
#
#     This file is part of mail_attach_existing_attachment,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_attach_existing_attachment is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_attach_existing_attachment is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_attach_existing_attachment.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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


