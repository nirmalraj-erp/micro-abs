from odoo import api, fields, models, _
from datetime import date
from datetime import datetime


class SaleOrderReportInherit(models.AbstractModel):
    _name = 'report.micro_abs_sales.sale_order_report'
    _description = 'Sale Order Report'

    @api.multi
    def _get_report_values(self, ids, data=None):
        report_obj = self.env['sale.order'].browse(ids)
        return {
            'doc_ids': ids,
            'doc_model': 'sale.order',
            'docs': report_obj,
            'data': data,
        }
