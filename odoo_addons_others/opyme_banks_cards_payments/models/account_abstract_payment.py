# coding: utf-8
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from openerp import models, fields, api


class AccountAbstractPayment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    bank_card_coupon_ids = fields.One2many(
        string="Cupones de Tarjetas",
        comodel_name="bank.card.coupon",
        inverse_name="account_payment_id",
    )

    @api.onchange("bank_card_coupon_ids")
    def on_bank_card_coupon_ids_change(self):
        self.recalculate_amount()

    def set_payment_methods_vals(self):
        vals = super(AccountAbstractPayment, self).set_payment_methods_vals()
        coupons_vals = self.get_coupons_vals()
        return vals + coupons_vals

    def get_coupons_vals(self):
        coupons_vals = []
        for coupon in self.bank_card_coupon_ids:
            bank_card = coupon.bank_card_id
            bank_account = bank_card.account_id
            coupons_vals.append({"amount": coupon.amount, "account_id": bank_account.id})
        return coupons_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
