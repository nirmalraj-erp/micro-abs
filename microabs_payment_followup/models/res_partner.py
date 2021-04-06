from odoo import api, fields, models, _


class PartnerPaymentDetails(models.Model):
    _inherit = 'res.partner'

    payment_to = fields.Char(string='Payment To')
    payment_cc = fields.Char(string='Payment CC')
    docs_to = fields.Char(string='Docs To')
    docs_cc = fields.Char(string='Docs CC')
    official_contact = fields.Char(string='Official Contact')

