from odoo import api, fields, models, _


class PartnerSalesDetails(models.Model):
    _inherit = 'res.partner'

    so_email_to = fields.Text(string='SO Email To')
    so_email_cc = fields.Text(string='SO Email CC')
    so_email_to_ids = fields.Many2many("res.partner", "res_partner_so_to_rel", "partner_id", "so_to_id",
                                       string="SO To")
    so_email_cc_ids = fields.Many2many("res.partner", "res_partner_so_cc_rel", "partner_id", "so_cc_id",
                                       string="SO CC")

    @api.onchange("so_email_to_ids")
    def onchange_so_email_to_ids(self):
        if self.so_email_to_ids:
            self.so_email_to = False
            for i in self.so_email_to_ids:
                if self.so_email_to and i.email:
                    self.so_email_to = self.so_email_to + i.email + ", "
                elif i.email:
                    self.so_email_to = i.email + ", "
        else:
            self.so_email_to = False

    @api.onchange("so_email_cc_ids")
    def onchange_so_email_cc_ids(self):
        if self.so_email_cc_ids:
            self.so_email_cc = False
            for i in self.so_email_cc_ids:
                if self.so_email_cc and i.email:
                    self.so_email_cc = self.so_email_cc + i.email + ", "
                elif i.email:
                    self.so_email_cc = i.email + ", "
        else:
            self.so_email_cc = False


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('microabs_sales_followup', 'microabs_email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids[0])
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_send_email(self):
        """This function opens a window to compose an email, with the email template message loaded by default"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('microabs_sales_followup', 'microabs_email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            print('**************-->', ValueError)
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            # 'default_email_to': self.partner_id.docs_to,
            'default_email_cc': self.partner_id.docs_cc,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            # 'default_use_template': bool(template_id),
            'default_composition_mode': 'comment',
            'default_attachment_ids': [list_item for list_item in self.env[
                'ir.attachment'].search([('res_id', '=', self.id), ('res_model', '=', 'sale.order')]).ids],
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
