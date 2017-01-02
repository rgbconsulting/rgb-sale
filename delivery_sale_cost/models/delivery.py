# -*- coding: utf-8 -*-
# See README file for full copyright and licensing details.

from openerp.osv import osv


class Delivery(osv.Model):
    _inherit = 'delivery.grid'

    def get_standard_price(self, cr, uid, id, order, dt, context=None):
        total = 0
        weight = 0
        volume = 0
        quantity = 0
        total_delivery = 0.0
        product_uom_obj = self.pool.get('product.uom')
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_subtotal + self.pool['sale.order']._amount_line_tax(cr, uid, line,
                                                                                                 context=context)
            if not line.product_id or line.is_delivery:
                continue
            q = product_uom_obj._compute_qty(cr, uid, line.product_uom.id, line.product_uom_qty,
                                             line.product_id.uom_id.id)
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q
            quantity += q
        total = (order.amount_total or 0.0) - total_delivery

        ctx = context.copy()
        ctx['date'] = order.date_order
        total = self.pool['res.currency'].compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, total,
                                                  context=ctx)
        return self.get_standard_price_from_picking(cr, uid, id, total, weight, volume, quantity, context=context)

    def get_standard_price_from_picking(self, cr, uid, id, total, weight, volume, quantity, context=None):
        grid = self.browse(cr, uid, id, context=context)
        standard_price = 0.0
        ok = False
        price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity}
        for line in grid.line_ids:
            test = eval(line.type + line.operator + str(line.max_value), price_dict)
            if test:
                if line.price_type == 'variable':
                    standard_price = line.standard_price * price_dict[line.variable_factor]
                else:
                    standard_price = line.standard_price
                ok = True
                break
        if not ok:
            raise osv.except_osv(_("Unable to fetch delivery method!"), _(
                "Selected product in the delivery method doesn't fulfill any of the delivery grid(s) criteria."))

        return standard_price
