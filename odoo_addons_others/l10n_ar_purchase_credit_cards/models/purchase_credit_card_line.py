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
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class PurchaseCreditCard(models.Model):  # Se encarga de crear/elimininar las cuotas.

    _name = 'purchase.credit.card.line'

    payment_id = fields.Many2one(
        'account.payment',
        'Pago',
        ondelete="cascade"
    )
    partner_id = fields.Many2one(
        related='payment_id.partner_id'
    )
    currency_id = fields.Many2one(
        related='payment_id.currency_id'
    )
    credit_card_id = fields.Many2one(
        'credit.card',
        'Tarjeta',
        required=True,
        ondelete='restrict'
    )
    amount = fields.Monetary(
        'Importe',
        required=True
    )
    fees = fields.Integer(
        'Cuotas',
        required=True
    )
    description = fields.Char(
        'Descripción',
        helper='La descripcion que aparecera en las cuotas de las tarjetas'
    )
    card_fee_ids = fields.One2many(
        'purchase.credit.card.fee',
        'credit_card_line_id',
        'Cuotas creadas'
    )

    @api.constrains('fees', 'amount')
    def constraint_values(self):
        if any(line.amount <= 0 or line.fees <= 0 for line in self):
            raise ValidationError("Los valores del pago con tarjetas deben ser positivos")

    def get_account(self):
        self.ensure_one()
        return self.credit_card_id.account_id

    def create_fees(self):
        values = self.get_card_fee_values()
        fees = self.env['purchase.credit.card.fee']
        for fee_value in values:
            fees |= fees.create(fee_value)
        return fees

    def delete_fees(self):
        self.mapped('card_fee_ids').unlink()

    def get_card_fee_values(self):
        fees = []
        for line in self:
            accumulated = 0
            for fee in range(1, line.fees+1):

                due_date = fields.Date.from_string(line.payment_id.payment_date)+relativedelta(months=+(fee-1))

                # La ultima cuota es el restante entre el total y las anteriores
                amount = round(line.amount / line.fees, 2) if fee != line.fees else round(line.amount - accumulated, 2)
                fees.append(line._get_fee_vals(fee, amount, due_date))
                accumulated += amount

        return fees

    def _get_fee_vals(self, fee, amount, due_date):
        self.ensure_one()
        vals = {
            'name': self.description or self.payment_id.name,
            'credit_card_line_id': self.id,
            'total_fees': self.fees,
            'fee': fee,
            'due_date': due_date,
            'amount': amount
        }
        return vals


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
