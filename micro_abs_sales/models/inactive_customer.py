# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import xlsxwriter
import base64
import datetime


class InactiveCustomerList(models.Model):
    _name = "inactive.customer.list"
    _description = "Inactive Sales Customer List"
    _inherit = ['mail.thread']

    name = fields.Char("File", track_visibitity='always')
    customer_file = fields.Binary(string='Download File')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))

    @api.model
    def create_inactive_customer_record(self):
        company_ids = self.env['res.company'].search([])
        for company in company_ids:
            cust_vals = {
                'name': 'Inactive Customer',
                'company_id': company.id,
            }
            sync_id = self.create(cust_vals)
            self.get_customer_data(sync_id,company.id)

    def get_customer_data(self, sync_id, company_id):
        workbook = xlsxwriter.Workbook('customer_list' + '.xlsx')
        sheet = workbook.add_worksheet('customer_report.xlsx')
        po_header = workbook.add_format({
            'font_size': 12,
            'border': 1,
            'align': 'left',
            'bg_color': '#B6D0E2',
            'font_name': 'Liberation Serif', })
        merge_header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#fed8b1'})
        sheet.set_column('B3:B3', 25)
        sheet.set_column('A3:A3', 10)

        sl_format = workbook.add_format({
            'align': 'left',
            'font_name': 'Liberation Serif',
            'valign': 'vcenter'
        })
        sheet.merge_range('A2:D2', 'Inactive Customer List', merge_header)
        row = 3
        self.env.cr.execute("""   SELECT id, name, company_id
                                   FROM res_partner
                                   WHERE id not IN (SELECT partner_id
                                      FROM sale_order
                                      WHERE date_order >= date_trunc('month', now()) - interval '1 month'
                                  and date_order <  date_trunc('month', now()) and state = 'sale') and company_id = %d
                                             """ % company_id)
        customer_list = self.env.cr.dictfetchall()
        sheet.write('A' + str(row), 'Sl.NO', po_header)
        sheet.write('B' + str(row), 'Customer Name', po_header)
        counter = 1
        for lines in customer_list:
            row += 1
            sheet.write('A' + str(row), counter, sl_format)
            counter += 1
            sheet.write('B' + str(row), lines.get('name'), sl_format)
        workbook.close()
        file_save = open('customer_list.xlsx', 'rb')
        out = file_save.read()
        file_save.close()
        sync_id.customer_file = base64.b64encode(out)
        # Create an Attachment
        attachment_vals = {
            'name': 'Inactive Customer List',
            'type': 'binary',
            'res_model': 'inactive.customer.list',
            'res_id': sync_id.ids[0],
            'datas': sync_id.customer_file,
        }
        attachment_id = self.env['ir.attachment'].create(attachment_vals)
        mail_ids = []
        send_mail = self.env['mail.mail']
        today = datetime.date.today()
        first = today.replace(day=1)
        get_previous_month = first - datetime.timedelta(days=1)
        previous_month = get_previous_month.strftime("%B, %Y")
        mail_ids.append(send_mail.create({
            'email_from': 'erp@microab.com',
            'email_to': 'srini@microab.com,saba@microab.com',
            'subject': '%s - %s: Inactive Customers' % (previous_month, sync_id.company_id.name),
            'attachment_ids': [(6, 0, attachment_id.ids)],
            'body_html': '''<span  style="font-size:12px">
                                Hello Team,<br/>
                                <br/>Please find the Inactive customer list attached as of %s<br/>
                                </span>''' % previous_month,
        }))
        for i in range(len(mail_ids)):
            mail_ids[i].send(self)


