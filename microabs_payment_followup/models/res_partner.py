from odoo import api, fields, models, _


class PartnerPaymentDetails(models.Model):
    _inherit = 'res.partner'

    payment_to = fields.Char(string='Payment To')
    payment_cc = fields.Char(string='Payment CC')
    docs_to = fields.Char(string='Email Docs To')
    docs_cc = fields.Char(string='Email Docs CC')
    official_contact = fields.Char(string='Official Contact')
    docs_to_ids = fields.Many2many("res.partner", "res_partner_to_rel", "partner_id", "to_id", string="Docs To")
    docs_cc_ids = fields.Many2many("res.partner", "res_partner_cc_rel", "partner_id", "cc_id", string="Docs CC")

    @api.onchange("docs_to_ids")
    def onchange_docs_to_ids(self):
        if self.docs_to_ids:
            self.docs_to = False
            for i in self.docs_to_ids:
                if self.docs_to:
                    self.docs_to = self.docs_to + i.email + ","
                else:
                    self.docs_to = i.email + ","

    @api.onchange("docs_cc_ids")
    def onchange_docs_cc_ids(self):
        if self.docs_cc_ids:
            self.docs_cc = False
            for i in self.docs_cc_ids:
                if self.docs_cc:
                    self.docs_cc = self.docs_cc + i.email + ","
                else:
                    self.docs_cc = i.email + ","
