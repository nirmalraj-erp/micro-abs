from odoo import api, fields, models, _
from datetime import date
from datetime import datetime


class SaleOrderReportInherit(models.AbstractModel):
    _name = 'report.micro_abs_sales.sale_order_report'
    _description = 'Sale Order Report'

    @api.multi
    def _get_report_values(self, ids, data=None):
        report_obj = self.env['sale.order'].browse(ids)
        so_line = self.env['sale.order.line'].search([('order_id', '=', report_obj.id)])
        wkno = 0
        for line in so_line:
            d_date = line.delivery_date

            if d_date:
                ndate = d_date.strftime('%Y,%m,%d')
                d = ndate.split(',')
                wkno = date(int(d[0]), int(d[1]), int(d[2])).isocalendar()[1]
        return {
            'doc_ids': ids,
            'doc_model': 'sale.order',
            'docs': report_obj,
            'data': data,
            'wkno': wkno+1,
        }
