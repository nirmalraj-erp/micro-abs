from odoo import api, fields, models, _


class PartnerPaymentDetails(models.Model):
    _inherit = 'res.partner'

    payment_to = fields.Char(string='Email Payment To')
    payment_cc = fields.Char(string='Email Payment CC')
    docs_to = fields.Text(string='Email Docs To')
    docs_cc = fields.Text(string='Email Docs CC')
    official_contact_id = fields.Many2one("res.partner", string='Official Contact 1')
    official_contact_two_id = fields.Many2one("res.partner", string='Official Contact 2')
    docs_to_ids = fields.Many2many("res.partner", "res_partner_to_rel", "partner_id", "to_id", string="Docs To")
    docs_cc_ids = fields.Many2many("res.partner", "res_partner_cc_rel", "partner_id", "cc_id", string="Docs CC")
    payment_to_ids = fields.Many2many("res.partner", "pay_partner_to_rel", "partner_id", "to_id", string="Payment To")
    payment_cc_ids = fields.Many2many("res.partner", "pay_partner_cc_rel", "partner_id", "cc_id", string="Payment CC")

    @api.onchange("docs_to_ids")
    def onchange_docs_to_ids(self):
        if self.docs_to_ids:
            self.docs_to = False
            for i in self.docs_to_ids:
                if self.docs_to and i.email:
                    self.docs_to = self.docs_to + i.email + ", "
                elif i.email:
                    self.docs_to = i.email + ", "
        else:
            self.docs_to = False

    @api.onchange("docs_cc_ids")
    def onchange_docs_cc_ids(self):
        if self.docs_cc_ids:
            self.docs_cc = False
            for i in self.docs_cc_ids:
                if self.docs_cc and i.email:
                    self.docs_cc = self.docs_cc + i.email + ", "
                elif i.email:
                    self.docs_cc = i.email + ", "
        else:
            self.docs_cc = False

    @api.onchange("payment_to_ids")
    def onchange_payment_to_ids(self):
        if self.payment_to_ids:
            self.payment_to = False
            for i in self.payment_to_ids:
                if self.payment_to and i.email:
                    self.payment_to = self.payment_to + i.email + ", "
                elif i.email:
                    self.payment_to = i.email + ", "
        else:
            self.payment_to = False

    @api.onchange("payment_cc_ids")
    def onchange_payment_cc_ids(self):
        if self.payment_cc_ids:
            self.payment_cc = False
            for i in self.payment_cc_ids:
                if self.payment_cc and i.email:
                    self.payment_cc = self.payment_cc + i.email + ", "
                elif i.email:
                    self.payment_cc = i.email + ", "
        else:
            self.payment_cc = False
