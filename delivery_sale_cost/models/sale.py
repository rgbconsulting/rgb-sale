# -*- coding: utf-8 -*-
# See README file for full copyright and licensing details.

import time

from openerp.osv import osv


class Sale(osv.Model):
    _inherit = 'sale.order'

    def delivery_set(self, cr, uid, ids, context=None):
        delivery_ids = super(Sale, self).delivery_set(cr, uid, ids, context)
        line_ids = []
        for delivery in delivery_ids:
            line_obj = self.pool.get('sale.order.line').browse(cr, uid, delivery, context=context)
            grid_obj = self.pool.get('delivery.grid')
            carrier_obj = self.pool.get('delivery.carrier')
            order = self.browse(cr, uid, ids, context=context)
            grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id], order.partner_shipping_id.id)
            grid = grid_obj.browse(cr, uid, grid_id, context=context)
            line_obj['purchase_price'] = grid_obj.get_standard_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'),
                                                                     context)
            line_ids.append(line_obj.id)
        return line_ids
