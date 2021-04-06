from odoo import api, fields, models, _


class CustomerStatusReport(models.AbstractModel):
    _name = 'report.microabs_reports.customer_status_report'
    _description = 'Sale Commission Report'

    @api.multi
    def _get_report_values(self, ids, data=None):
        partner = tuple([element for element in data['form'].get('partner_id')])
        if len(partner) > 1:
            self.env.cr.execute(""" SELECT ai.invoice_number, so.po_no, so.po_date, 
                                    sm.name as sm_name, ffd.name as ffd_name, 
                                    ai.bl_no, ai.bl_date, so.supplier_expected_date,
                                    ai.date_invoice, so.so_commitment_date, rp.name, rp.display_name,
                                    pt.name as pt_name, so.partner_id, ai.number, sol.qty_to_invoice,
                                    sol.qty_invoiced, sol.qty_to_invoice
                                    FROM sale_order so
                                    LEFT JOIN sale_order_line sol ON (sol.order_id = so.id)
                                    LEFT JOIN account_invoice ai ON (so.name = ai.origin) 
                                    LEFT JOIN product_product pp ON (pp.id = sol.product_id)
                                    LEFT JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                                    LEFT JOIN res_partner rp ON (rp.id = so.partner_id) 
                                    LEFT JOIN shipment_mode sm ON (sm.id = so.shipment_mode)
                                    LEFT JOIN freight_forward_details ffd 
                                    ON (ffd.id = so.freight_forwarder_details)
                                    WHERE so.partner_id in '%s' AND 
                                    so.state = 'sale' AND
                                    so.po_date BETWEEN '%s' AND '%s'
                                    ORDER BY so.po_no, so.po_date
                                     """ % (str(partner), data['form'].get('date_start'), data['form'].get('date_end')))
            invoice_list = self.env.cr.dictfetchall()
        else:
            self.env.cr.execute(""" SELECT ai.invoice_number, so.po_no, so.po_date, 
                                    sm.name as sm_name, ffd.name as ffd_name, 
                                    ai.bl_no, ai.bl_date, so.supplier_expected_date,
                                    ai.date_invoice, so.so_commitment_date, rp.name, rp.display_name,
                                    pt.name as pt_name, so.partner_id, ai.number, sol.qty_to_invoice,
                                    sol.qty_invoiced, sol.qty_to_invoice
                                    FROM sale_order so
                                    LEFT JOIN sale_order_line sol ON (sol.order_id = so.id)
                                    LEFT JOIN account_invoice ai ON (so.name = ai.origin) 
                                    LEFT JOIN product_product pp ON (pp.id = sol.product_id)
                                    LEFT JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                                    LEFT JOIN res_partner rp ON (rp.id = so.partner_id) 
                                    LEFT JOIN shipment_mode sm ON (sm.id = so.shipment_mode)
                                    LEFT JOIN freight_forward_details ffd 
                                    ON (ffd.id = so.freight_forwarder_details)
                                    WHERE so.partner_id = %s AND 
                                    so.state = 'sale' AND
                                    so.po_date BETWEEN '%s' AND '%s'
                                    ORDER BY so.po_no, so.po_date
                                     """ % (','.join(map(repr, partner)),
                                            data['form'].get('date_start'), data['form'].get('date_end')))
            invoice_list = self.env.cr.dictfetchall()
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': invoice_list,
            'company': data['form'].get('company_id'),
        }
