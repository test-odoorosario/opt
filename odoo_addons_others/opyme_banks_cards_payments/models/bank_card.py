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


class BankCard(models.Model):
    _name = "bank.card"
    _rec_name = "name"

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    bank_account_id = fields.Many2one(
        string="Cuenta bancaria",
        comodel_name="account.journal",
        required=True,
    )

    account_id = fields.Many2one(
        string="Cuenta contable",
        comodel_name="account.account",
        required=True,
    )

    active = fields.Boolean(
        string="Activo?",
        default=True,
    )

    bank_card_fee_ids = fields.One2many(
        string="Cuotas",
        comodel_name="bank.card.fee",
        inverse_name="bank_card_id"
    )

    _sql_constraints = [
        (
            "bank_card_unique_name",
            "unique(name)",
            "Ya existe una tarjeta con el mismo nombre!"
        ),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
