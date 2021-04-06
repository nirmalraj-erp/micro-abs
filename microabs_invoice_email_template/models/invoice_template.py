from odoo import api, fields, models, _


class InvoiceTemplateInherit(models.Model):
    _inherit = 'account.invoice'

    def action_send_email(self):
        """This function opens a window to compose an email, with the email template message loaded by default"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('microabs_invoice_email_template', 'email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'account.invoice',
            'default_res_id': self.id,
            'default_email_to': self.partner_id.docs_to,
            'default_email_cc': self.partner_id.docs_cc,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [list_item for list_item in self.env[
                'ir.attachment'].search([('res_id', '=', self.id), ('res_model', '=', 'account.invoice')]).ids],
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
