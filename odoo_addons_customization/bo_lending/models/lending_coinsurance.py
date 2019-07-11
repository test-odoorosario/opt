# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class LendingCoinsurance(models.Model):
    _name = 'lending.coinsurance'
    _rec_name = 'lending_id'

    lending_id = fields.Many2one(
        comodel_name="lending",
        string="Codigo",
        required=True,
    )

    code_range = fields.Char(
        string="Codigo hasta",
    )

    value_type = fields.Selection(
        string="Tipo de valor",
        selection=[('net_value', "Valor neto"), ('percentage', "Porcentaje")],
        required=True,
    )

    value = fields.Float(
        string="Valor",
    )

    _sql_constraints = [
        ('code_uniq', 'unique (lending_id, code_range)', 'Ya existe un coseguro con este mismo codigo.')
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
