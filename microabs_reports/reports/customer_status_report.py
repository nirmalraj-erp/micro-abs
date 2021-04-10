from odoo import api, fields, models, _


class CustomerStatusReportXLSX(models.AbstractModel):
    _name = 'report.microabs_reports.customer_status_template'
    _description = 'Sale Commission Report'
    _inherit = 'report.report_xlsx.abstract'

    # To Generate Excel Report
    def generate_xlsx_report(self, workbook, data, status_id):
        for obj in status_id:
            # report_name = obj.partner_id.name
            sheet = workbook.add_worksheet('customer_report.xlsx')
            po_header = workbook.add_format({
                'font_size': 12,
                'border': 1,
                'align': 'left',
                'bg_color': '#B6D0E2',
                'font_name': 'Liberation Serif', })
            po_values = workbook.add_format({
                'font_size': 12,
                'border': 1,
                'align': 'left',
                'font_name': 'Liberation Serif', })
            merge_header = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#fed8b1'})
            merge_customer = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#b2beb5'})
            sheet.set_column('C3:M3', 20)
            sheet.set_column('A9:A9', 2)
            sheet.set_column('B9:B9', 5)
            header_line = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'font_name': 'Liberation Serif',
                'valign': 'vcenter',
                'bg_color': '#B6D0E2'})
            line_values = workbook.add_format({
                'align': 'left',
                'font_name': 'Liberation Serif',
                'valign': 'vcenter'
            })
            sl_format = workbook.add_format({
                'align': 'center',
                'font_name': 'Liberation Serif',
                'valign': 'vcenter'
            })
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy',
                                               'align': 'left',
                                               'border': 1,
                                               'font_name': 'Liberation Serif'})
            date_format_lines = workbook.add_format({'num_format': 'dd/mm/yyyy',
                                                    'align': 'left',
                                                     'font_name': 'Liberation Serif'})
            sheet.merge_range('C2:H2', 'Customer Status Report', merge_header)
            row = 3
            for partners in obj.partner_id.ids:
                for data in self.get_po_common_data(partners, obj.date_start, obj.date_end):
                    row += 1
                    sheet.merge_range('C' + str(row) + ':' + 'E' + str(row), 'Customer Name', merge_customer)
                    sheet.merge_range('F' + str(row) + ':' + 'H' + str(row), data.get('partner'), merge_customer)
                    row += 2
                    sheet.write('D' + str(row), 'PO No.', po_header)
                    sheet.write('E' + str(row), data.get('po_no'), po_values)
                    sheet.write('F' + str(row), 'PO Date.', po_header)
                    sheet.write('G' + str(row), data.get('po_date'), date_format)
                    row += 1
                    sheet.write('D' + str(row), 'Shipping Mode', po_header)
                    sheet.write('E' + str(row), data.get('sm_name'), po_values)
                    sheet.write('F' + str(row), 'FF Details', po_header)
                    sheet.write('G' + str(row), data.get('ffd_name'), date_format)
                    row += 1
                    sheet.write('D' + str(row), 'Supplier Del. Date', po_header)
                    sheet.write('E' + str(row), data.get('supplier_expected_date'), date_format)
                    sheet.write('F' + str(row), 'Customer Req. Date', po_header)
                    sheet.write('G' + str(row), data.get('so_commitment_date'), date_format)
                    row += 2
                    sheet.write('B' + str(row), 'S.NO.', header_line)
                    sheet.write('C' + str(row), 'Product', header_line)
                    sheet.write('D' + str(row), 'Dispatch Status', header_line)
                    sheet.write('E' + str(row), 'Invoice No.', header_line)
                    sheet.write('F' + str(row), 'Invoice Date', header_line)
                    sheet.write('G' + str(row), 'BL/AWB No.', header_line)
                    sheet.write('H' + str(row), 'BL/AWB Date', header_line)
                    row += 2
                    counter = 1
                    for lines in self.get_order_line_data(partners, obj.date_start, obj.date_end):
                        sheet.write('B' + str(row), counter, sl_format)
                        counter += 1
                        sheet.write('C' + str(row), lines.get('pt_name'), line_values)
                        if not lines.get('invoice_number'):
                            sheet.write('D' + str(row), 'Yet to Dispatch', line_values)
                        else:
                            sheet.write('D' + str(row), 'Dispatched', line_values)
                            sheet.write('E' + str(row), lines.get('invoice_number'), line_values)
                            sheet.write('F' + str(row), lines.get('date_invoice'), date_format_lines)
                            sheet.write('G' + str(row), lines.get('bl_no'), line_values)
                            sheet.write('H' + str(row), lines.get('bl_date'), date_format_lines)
                        row += 1

    def get_order_line_data(self, partners, date_start, date_end):
        so_list_id = self.get_po_common_data(partners, date_start, date_end)
        for order in so_list_id:
            self.env.cr.execute(""" SELECT ai.invoice_number,
                                    ai.bl_no, ai.bl_date, 
                                    ai.date_invoice, rp.name partner, rp.display_name,
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
                                    so.id = %s AND
                                    so.po_date BETWEEN '%s' AND '%s'
                                    ORDER BY so.po_no, so.po_date
                                     """ % (partners, order['so_id'], date_start, date_end))
            invoice_list = self.env.cr.dictfetchall()
            return invoice_list

    def get_po_common_data(self, partners, date_start, date_end):
        self.env.cr.execute(""" SELECT so.po_no, so.po_date, 
                                   sm.name as sm_name, ffd.name as ffd_name, 
                                   so.supplier_expected_date, so.id as so_id,
                                   so.so_commitment_date, rp.name partner, rp.display_name
                                   FROM sale_order so
                                   LEFT JOIN res_partner rp ON (rp.id = so.partner_id) 
                                   LEFT JOIN shipment_mode sm ON (sm.id = so.shipment_mode)
                                   LEFT JOIN freight_forward_details ffd 
                                   ON (ffd.id = so.freight_forwarder_details)
                                   WHERE so.partner_id = %s AND 
                                   so.state = 'sale' AND
                                   so.po_date BETWEEN '%s' AND '%s'
                                   ORDER BY so.po_no, so.po_date
                                    """ % (partners, date_start, date_end))
        so_list = self.env.cr.dictfetchall()
        return so_list


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
