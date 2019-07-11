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
from openerp import models, fields


class BankCardFee(models.Model):
    _name = "bank.card.fee"
    _rec_name = "name"

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    bank_card_id = fields.Many2one(
        string="Tarjeta",
        comodel_name="bank.card",
        required=True,
        ondelete="cascade",
    )

    fee_quantity = fields.Char(
        string="Cuotas",
        required=True,
    )

    active = fields.Boolean(
        string="Activo?",
        default=True,
    )

    _sql_constraints = [
        (
            "bank_card_fee_unique_name_for_card",
            "unique(name, bank_card_id)",
            "Ya existe una cuota con el mismo nombre para la tarjeta seleccionada!"
        ),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
