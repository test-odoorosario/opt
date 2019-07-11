# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class AccountAbstractPayment(models.AbstractModel):  # Agrega los nuevos importes de las tarjetas al pago

    _inherit = 'account.abstract.payment'

    purchase_credit_card_line_ids = fields.One2many(
        'purchase.credit.card.line',
        'payment_id',
        'Pagos con tarjetas',
        copy=False
    )

    @api.onchange('purchase_credit_card_line_ids')
    def onchange_purchase_credit_card_line_ids(self):
        self.recalculate_amount()

    def set_payment_methods_vals(self):
        vals = super(AccountAbstractPayment, self).set_payment_methods_vals()

        for credit_card in self.purchase_credit_card_line_ids:
            vals.append({'amount': credit_card.amount, 'account_id': credit_card.get_account().id})

        return vals


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.multi
    def post_l10n_ar(self):
        for payment in self:
            payment.purchase_credit_card_line_ids.create_fees()
        return super(AccountPayment, self).post_l10n_ar()

    @api.multi
    def cancel(self):
        for payment in self:
            payment.purchase_credit_card_line_ids.delete_fees()
        return super(AccountPayment, self).cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
