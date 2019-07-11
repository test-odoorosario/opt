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
from openerp import models, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange("bank_card_coupon_ids")
    def on_bank_card_coupon_ids_change(self):
        self.recalculate_amount()

    def update_coupons_state(self, state):
        for coupon in self.bank_card_coupon_ids:
            coupon.state = state

    @api.multi
    def write(self, vals):
        ret = super(AccountPayment, self).write(vals)
        for s in self:
            state = vals.get("state")
            if state:
                s.update_coupons_state(state)
        return ret

    @api.multi
    def post_l10n_ar(self):
        map(lambda p: p.bank_card_coupon_ids.post(), self)
        return super(AccountPayment, self).post_l10n_ar()

    def cancel(self):
        map(lambda p: p.bank_card_coupon_ids.cancel(), self)
        return super(AccountPayment, self).cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
