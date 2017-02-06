# -*- coding: utf-8 -*-
# See README file for full copyright and licensing details.

from openerp import models, api, _, fields
from openerp.exceptions import except_orm


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_layout_cat_ids = fields.One2many(comodel_name='sale_layout.category', inverse_name="sale_order",
                                          string='Section')


class SaleLayout(models.Model):
    _inherit = "sale_layout.category"

    sale_order = fields.Many2one(comodel_name='sale.order', string='Sale')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_id = fields.Many2one(states={'draft': [('required', False)]})
    sale_layout_cat_id = fields.Many2one(domain="['|', ('sale_order', '=', order_id), ('sale_order', '=', False)]")
