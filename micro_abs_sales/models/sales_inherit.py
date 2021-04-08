# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import float_is_zero
from datetime import date


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    drawing_no = fields.Char(string='Drawing No.')
    specification = fields.Many2one('product.specification', string='Specification')
    application_ids = fields.Many2many('product.application', string='Applications')
    operation_id = fields.Many2one('product.operation', string='Operation')  
    product_kind = fields.Many2one('product.kind', string='Type')
    product_size = fields.Char(string='Size')
    product_recess_id = fields.Many2one("product.recess", string="Recess")
    offer_details_line = fields.One2many("product.offer.line", 'offer_line_id', string="Product Order Line")
    no_commission_required = fields.Boolean("No Commission Required", default=False)
    cutting_speed_id = fields.Many2one("cutting.speed", string="Cutting Speed")


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    specification = fields.Many2one('product.specification', string='Specification')
    application_ids = fields.Many2many('product.application', string='Applications')
    operation_id = fields.Many2one('product.operation', string='Operation')
    product_kind = fields.Many2one('product.kind', string='Type')
    product_size = fields.Many2one('product.size', string='Size')
    product_recess_id = fields.Many2one("product.recess", string="Recess")
    offer_details_line = fields.One2many("product.offer.line", 'offer_line_id', string="Product Order Line")
    no_commission_required = fields.Boolean("No Commission Required", default=False)
    cutting_speed_id = fields.Many2one("cutting.speed", string="Cutting Speed")


class ProductOfferLine(models.Model):
    _name = 'product.offer.line'
    _description = 'Product Offer line'
    _rec_name = 'offer_line_id'

    offer_line_id = fields.Many2one('product.product', string='')
    partner_id = fields.Many2one('res.partner', string='Customer Name')
    customer_item_code = fields.Char(string='Customer Item Code')
    offer_no = fields.Char(string='Offer No.')
    offer_date = fields.Date(string='Offer Dated')
    sequence = fields.Integer(string='Sequence')
    drawing_no = fields.Char(string='Drawing No.')
                

class CuttingSpeed(models.Model):
    _name = 'cutting.speed'
    _description = 'Cutting Speed'

    name = fields.Char(string='Cutting Speed')


class ProductRecess(models.Model):
    _name = 'product.recess'
    _description = 'Product Recess'

    name = fields.Char(string='Recess Name')


class ProductApplication(models.Model):
    _name = 'product.application'
    _description = 'Product Application'

    name = fields.Char(string='Application Name')


class ProductKind(models.Model):
    _name = 'product.kind'
    _description = 'Type'

    name = fields.Char(string='Type')


class ProductSize(models.Model):
    _name = 'product.size'
    _description = 'Size'

    name = fields.Char(string='Size')


class ProductSpecification(models.Model):
    _name = 'product.specification'
    _description = 'Specification'

    name = fields.Char(string='Specification')


class ProductOperation(models.Model):
    _name = 'product.operation'
    _description = 'Product Operation'

    name = fields.Char(string='Operation Name')


class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Customer Type'

    name = fields.Char(string='Customer Type')


class CustomerCode(models.Model):
    _name = 'customer.code'
    _description = 'Customer Type'

    name = fields.Char(string='Customer Code')


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    def _get_default_incoterm(self):
        return self.env.user.company_id.incoterm_id
    
    iec_code = fields.Char(string='IEC Code')
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm',
                                  default=_get_default_incoterm,
                                  help='International Commercial Terms are a series of predefined'
                                       ' commercial terms used in international transactions.')
    destination_ports_id = fields.Many2one('destination.port', string='Destination Port')
    application_ids = fields.Many2many('product.application', string='Applications')
    customer_code = fields.Many2one('customer.code', string='Customer Code')
    customer_type = fields.Many2one('customer.type', string='Customer Type')
    pan_no = fields.Char(string='PAN Number')
    commission_percentage = fields.Integer(string='Commission (%)')


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    order_conf_no = fields.Char(string='OC No.')
    order_conf_date = fields.Date(string='OC Date')
    supplier_expected_date = fields.Date(string='Supl. Del. Date')
    so_commitment_date = fields.Date(string='Cust. Reqd. Date')
    po_no = fields.Char(string='PO No')
    po_date = fields.Date(string='PO Date')
    po_received_date = fields.Date(string='PO Rcvd Date')
    order_type = fields.Many2one('order.type', string='Order Type')
    shipment_mode = fields.Many2one('shipment.mode', string='Shipment Mode')
    freight_forwarder = fields.Boolean(string='Freight Forwarder')
    freight_forwarder_details = fields.Many2one('freight.forward.details', string='FF Details')
    destination_ports_id = fields.Many2one('destination.port', string='Destination Port')
    res_contact_id = fields.Many2many('res.partner', string='Contact')
    official_contact_id = fields.Many2one('res.partner', string='Official Contact')
    inherit_order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                         states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
                                         copy=True, auto_join=True,
                                         domain=[('state', 'in', ('draft', 'sent', 'sale', 'cancel'))])
    vat = fields.Char(string='GST')
    iec_code = fields.Char(string='IEC Code')
    pan_no = fields.Char(string='PAN Number')
    report_partner_name = fields.Char('Report Partner Name', store=True)
    customer_type = fields.Many2one('customer.type', string='Customer Type')
    docs_address_id = fields.Many2one('docs.address', string='Docs Address')
    email_shipment_string = fields.Char(string='Email Shipment String')

    @api.onchange('order_line.delivery_date', 'so_commitment_date')
    @api.depends('order_line.delivery_date', 'so_commitment_date')
    def get_week_no_date(self):
        if self.so_commitment_date:
            wkno = 0
            for line in self.order_line:
                if line.delivery_date:
                    ndate = line.delivery_date.strftime('%Y,%m,%d')
                    d = ndate.split(',')
                    print(d)
                    wkno = date(int(d[0]), int(d[1]), int(d[2])).isocalendar()[1]
                    print(wkno)
                    line.wkno = wkno + 1


    @api.depends('so_commitment_date')
    @api.onchange('so_commitment_date')
    def get_delivery_date(self):
        for line in self.order_line:
            line.delivery_date = self.so_commitment_date

    @api.depends('partner_id','res_contact_id')
    @api.onchange('partner_id')
    def get_vat_values(self):
        """Customer master contact GST IEC and Incoterm values"""
        if self.partner_id:
            partner_id = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
            self.vat = partner_id.vat
            self.iec_code = partner_id.iec_code
            self.pan_no = partner_id.pan_no
            self.incoterm = partner_id.incoterm_id.id
            self.client_order_ref = partner_id.ref
            self.destination_ports_id = partner_id.destination_ports_id
            self.report_partner_name = self.partner_id.name.split()[0]
            self.customer_type = self.partner_id.customer_type.id
        return {'domain': {'res_contact_id': [('id', 'in', self.partner_id.child_ids.ids)],
                           'official_contact_id': [('id', 'in', self.partner_id.child_ids.ids)]}}

    # Create invoice - Core function inherited #
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        company_id = self.company_id.id
        journal_id = (self.env['account.invoice'].with_context(company_id=company_id or self.env.user.company_id.id).default_get(['journal_id'])['journal_id'])
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': company_id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'order_conf_no': self.order_conf_no,
            'order_conf_date': self.order_conf_date,
            'supplier_expected_date': self.supplier_expected_date,
            'pan_no': self.pan_no,
            'customer_type': self.customer_type.id,
            'po_no': self.po_no,
            'po_date': self.po_date,
            'po_received_date': self.po_received_date,
            'order_type': self.order_type.id,
            'shipment_mode': self.shipment_mode.id,
            'freight_forwarder': self.freight_forwarder,
            'freight_forwarder_details': self.freight_forwarder_details.id,
            'destination_ports_id': self.destination_ports_id.id,
            'res_contact_id': [(6, 0, self.res_contact_id.ids)],
            'official_contact_id': self.official_contact_id.id,
            'incoterm_id': self.incoterm.id,
            'commission_total': self.commission_total,
            'commission_percentage_total': self.commission_percentage_total,
            'total_taxed': self.total_taxed,
        }
        return invoice_vals

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        po_no = {}
        order_conf_no = {}
        invoices_name = {}
        order = {}

        # Keep track of the sequences of the lines
        # To keep lines under their section
        inv_line_sequence = 0
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            # sequence is the natural order of order_lines
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    po_no[group_key] = [invoice.po_no]
                    order_conf_no[group_key] = [invoice.order_conf_no]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.order_conf_no not in order_conf_no[group_key]:
                        order_conf_no[group_key].append(order.order_conf_no)
                    if order.po_no not in po_no[group_key]:
                        po_no[group_key].append(order.po_no)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        section_invoice = pending_section.invoice_line_create_vals(
                            invoices[group_key].id,
                            pending_section.qty_to_invoice
                        )
                        inv_line_sequence += 1
                        section_invoice[0]['sequence'] = inv_line_sequence
                        line_vals_list.extend(section_invoice)
                        pending_section = None

                    inv_line_sequence += 1
                    inv_line = line.invoice_line_create_vals(
                        invoices[group_key].id, line.qty_to_invoice
                    )
                    inv_line[0]['sequence'] = inv_line_sequence
                    line_vals_list.extend(inv_line)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env['account.invoice.line'].create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key])[:2000],
                                       'origin': ', '.join(invoices_origin[group_key]),
                                       'po_no': ', '.join(map(str, po_no[group_key])),
                                       'order_conf_no': ', `'.join(map(str, order_conf_no[group_key]))
                                       })
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        self._finalize_invoices(invoices, references)
        return [inv.id for inv in invoices.values()]


class DocsAddress(models.Model):
    _name = 'docs.address'
    _description = 'Docs Address'

    name = fields.Char(string='Docs Address')


class FreightForwardDetails(models.Model):
    _name = 'freight.forward.details'
    _description = 'Freight Forward Details'

    name = fields.Char(string='Freight Forward Details')


class DestinationPort(models.Model):
    _name = 'destination.port'
    _description = 'Destination Port'

    name = fields.Char(string='Destination Port')


class OrderType(models.Model):
    _name = 'order.type'
    _description = 'Order Type'

    name = fields.Char(string='Order Type')


class ShipmentMode(models.Model):
    _name = 'shipment.mode'
    _description = 'Shipment Mode'

    name = fields.Char(string='Shipment Mode Name')


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    description = fields.Text(string='Descriptions', required=True)
    customer_item_code = fields.Char(string='Customer Item Code')
    offer_no = fields.Char(string='Offer No.')
    offer_date = fields.Date(string='Offer Dated')
    drawing_no = fields.Char(string='Drawing No.')
    specification = fields.Many2one('product.specification', string='Specification')
    application_ids = fields.Many2many('product.application', string='Applications')
    operation_id = fields.Many2one('product.operation', string='Operation')
    product_kind = fields.Many2one('product.kind', string='Type')
    product_size = fields.Many2one('product.size', string='Size')
    product_recess_id = fields.Many2one("product.recess", string="Recess")
    sequence = fields.Integer(string='Sequence')
    delivery_date = fields.Date('Delivery Date')
    wkno = fields.Integer(string='Week No')

    @api.onchange('product_id')
    def get_product_line(self):
        """Description line based on Product master - Product Info"""
        if self.product_id:
            self.product_size = self.product_id.product_size.id
            self.product_kind = self.product_id.product_kind.id
            self.operation_id = self.product_id.operation_id.id
            self.product_recess_id = self.product_id.product_recess_id.id
            self.specification = self.product_id.specification.id
            self.application_ids = self.product_id.application_ids.ids
            self.no_commission_required = self.product_id.no_commission_required
            for line in self.product_id.offer_details_line:
                if self.order_id.partner_id == line.partner_id:
                    self.customer_item_code = line.customer_item_code if self.order_id.partner_id == line.partner_id else ''
                    self.offer_no = line.offer_no if self.order_id.partner_id == line.partner_id else ''
                    self.offer_date = line.offer_date if self.order_id.partner_id == line.partner_id else ''
                    self.drawing_no = line.drawing_no if self.order_id.partner_id == line.partner_id else ''
            offer_date = ''
            if self.offer_date:
                offer_date = datetime.strftime(self.offer_date, "%d/%m/%Y")
            vals =""""""
            if self.product_size.name:
                vals += 'Size : ' + str(self.product_size.name)
            if self.product_recess_id.name:
                vals += "\n" 'Recess : ' + str(self.product_recess_id.name)
            if self.specification.name:
                vals += "\n" 'Specification : ' + str(self.specification.name)
            if self.drawing_no:
                vals += "\n" 'Drawing No : ' + str(self.drawing_no)
            if self.product_id.cutting_speed_id.name:
                vals += "\n" 'Cutting Speed : ' + str(self.product_id.cutting_speed_id.name)
            if self.product_id.l10n_in_hsn_code:
                vals += "\n" 'HSN Code : ' + str(self.product_id.l10n_in_hsn_code)
            if self.offer_no or self.offer_date:
                vals += "\n" 'Offer No : ' + str(self.offer_no) + " " + "dtd." + " " + str(offer_date)
            if self.product_id.description_sale:
                vals += "\n" 'Product Description : ' + str(self.product_id.description_sale)
            if self.customer_item_code:
                vals += "\n" 'Customer Item Code : ' + str(self.customer_item_code)
            if self.product_id.default_code:
                vals += "\n" 'Supplier Item Code : ' + str(self.product_id.default_code)
            self.description = vals

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        product = self.product_id.with_context(force_company=self.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.description,
            # 'description': self.description,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'no_commission_required': self.no_commission_required,
            'quantity': qty,
            'discount': self.discount,
            'commission_percentage': self.commission_percentage,
            'commission_amount': self.commission_amount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
        }
        return res

                               
class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    order_conf_no = fields.Char(string='OC No.')
    order_conf_date = fields.Date(string='OC Date')
    po_no = fields.Char(string='PO No')
    po_date = fields.Date(string='PO Date')
    po_received_date = fields.Date(string='PO Rcvd Date')
    order_type = fields.Many2one('order.type', string='Order Type')
    shipment_mode = fields.Many2one('shipment.mode', string='Shipment Mode')
    freight_forwarder = fields.Boolean(string='Freight Forwarder')
    freight_forwarder_details = fields.Many2one('freight.forward.details', string='FF Details')
    destination_ports_id = fields.Many2one('destination.port', string='Destination Port')
    res_contact_id = fields.Many2many('res.partner', string='Contact')
    invoice_number = fields.Char(string="Invoice No.")
    bl_no = fields.Char(string='BL/AWB No')
    bl_date = fields.Date(string='BL/AWB Date')
    eta_date = fields.Date(string='ETA')
    supplier_expected_date = fields.Date(string='Supl. Del. Date')
    pan_no = fields.Char(string='PAN Number')
    customer_type = fields.Many2one('customer.type', string='Customer Type')
    official_contact_id = fields.Many2one('res.partner', string='Official Contact')
    email_shipment_string = fields.Char(string='Email Shipment String', store=True, compute='_get_email_shipment_string')

    @api.depends('partner_id')
    def get_contacts(self):
        """Customer contact ids domain"""
        if self.partner_id:
            return {'domain': {'res_contact_id': [('id', 'in', self.partner_id.child_ids.ids)],
                               'official_contact_id': [('id', 'in', self.partner_id.child_ids.ids)]}}

    @api.onchange('shipment_mode', 'bl_no')
    def onchange_email_shipment_string(self):
        if self.shipment_mode.name == 'Sea' and self.bl_no:
            self.email_shipment_string = 'Bill of Lading No.'
        elif self.shipment_mode.name == 'Air' and self.bl_no:
            self.email_shipment_string = 'Air way Bill No.'
        else:
            self.email_shipment_string = ''

    @api.depends('shipment_mode', 'bl_no')
    def _get_email_shipment_string(self):
        if self.shipment_mode.name == 'Sea' and self.bl_no:
            self.email_shipment_string = 'Bill of Lading No.'
        elif self.shipment_mode.name == 'Air' and self.bl_no:
            self.email_shipment_string = 'Air way Bill No.'
        else:
            self.email_shipment_string = ''

    def _get_refund_common_fields(self):
        return ['partner_id', 'payment_term_id', 'account_id', 'currency_id',
                'journal_id', 'po_date', 'po_no', 'po_received_date',
                'order_conf_no', 'order_type', 'order_conf_date',
                'shipment_mode', 'freight_forwarder_details', 'destination_ports_id',
                'res_contact_id', 'invoice_number', 'bl_no', 'bl_date', 'supplier_expected_date', 'pan_no']


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    agent = fields.Char("Agent")
    commission = fields.Float("Commission(%)")
    commission_agent = fields.Char("Commission Agent")
    c_street = fields.Char()
    c_street2 = fields.Char()
    c_zip = fields.Char(change_default=True)
    c_city = fields.Char()
    c_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                                 domain="[('country_id', '=?', country_id)]")
    c_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    current_account_no = fields.Char('Account No.')
    intermediary = fields.Char('Name of the Intermediary')
    beneficiary = fields.Char('Beneficiary Bank Name')
    bank_name = fields.Char('Bank Name')
    bank_branch = fields.Char('Bank Branch')
    swift = fields.Char('Beneficiary Bank Name')
    iban_no = fields.Char('IBAN NO')
    i_street = fields.Char()
    i_street2 = fields.Char()
    i_zip = fields.Char(change_default=True)
    i_city = fields.Char()
    i_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    i_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    bb_city = fields.Char()
    bb_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    bb_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    signature = fields.Binary("Signature")
    contact = fields.Char("Name of Signed person")
    com_logo = fields.Binary("Logo")
    website_address = fields.Char('Website Address')

    @api.onchange('website')
    @api.depends('website')
    def get_website_address(self):
        if self.website:
            url = self.website.replace("http://", "")
            self.website_address = url


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    active = fields.Boolean(default=True)


class SaleAdvancePaymentInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = order.fiscal_position_id.map_account(
                self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id).id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _(
                    'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
        else:
            tax_ids = taxes.ids

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'po_no': order.po_no,
            'order_conf_no': order.order_conf_no,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'po_no': order.po_no,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'account_analytic_id': order.analytic_account_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'company_id': order.company_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return invoice


class AccountMoveMicro(models.Model):
    _inherit = 'account.move'

    def update_move(self):
        print('HAHAHAH', self.line_ids)
        line_list = self.line_ids
        line_list.write({
                        'name': 'Special Premium',
                        'account_id': 31,
                        'debit': 5120,
                        'credit': 5120,
                        'quantity': 1,
                        'uom_id': 1,
        })
