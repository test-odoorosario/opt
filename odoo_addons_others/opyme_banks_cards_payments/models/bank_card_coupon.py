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
import odoo.addons.decimal_precision as dp


class BankCardCoupon(models.Model):
    _name = "bank.card.coupon"
    _rec_name = "number"

    STATES = [
        ("draft", "Borrador"),
        ("posted", "Publicado"),
        ("sent", "Enviado"),
        ("reconciled", "Conciliado"),
    ]

    def get_states(self):
        return self.STATES

    def get_payment_date(self):
        date = None
        if self.account_payment_id:
            date = self.account_payment_id.payment_date
        return date

    number = fields.Char(
        string="Numero",
        required=True,
        copy=False,
    )

    bank_card_id = fields.Many2one(
        string="Tarjeta",
        comodel_name="bank.card",
        required=True,
        copy=False,
        ondelete="restrict",
    )

    bank_card_fee_id = fields.Many2one(
        string="Cuotas",
        comodel_name="bank.card.fee",
        required=True,
        copy=False,
        ondelete="restrict",
    )

    amount = fields.Float(
        string="Importe",
        digits=dp.get_precision("Product Price"),
        required=True,
    )

    date = fields.Date(
        string="Fecha",
        required=True,
        default=lambda self: self.get_payment_date(),
    )

    state = fields.Selection(
        string="Estado",
        selection=get_states,
        required=True,
        default="draft",
        copy=False,
    )

    account_payment_id = fields.Many2one(
        string="Pago",
        comodel_name="account.payment",
        ondelete="cascade",
    )

    @api.onchange("bank_card_id")
    def on_bank_card_id_change(self):
        self.bank_card_fee_id = None
        ids = self.bank_card_id.bank_card_fee_ids.ids
        return {
            "domain": {
                "bank_card_fee_id": [
                    ("id", "in", ids)
                ]
            }
        }

    @api.multi
    def post(self):
        self.write({
            "state": "posted"
        })

    @api.multi
    def cancel(self):
        self.write({
            "state": "draft"
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
