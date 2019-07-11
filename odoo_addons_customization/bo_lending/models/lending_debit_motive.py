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

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class LendingDebitMotive(models.Model):
    _name = 'lending.debit.motive'
    _order = 'code'

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    code = fields.Integer(
        string="Codigo",
        required=True,
    )

    percentage = fields.Integer(
        string="Porcentaje",
        required=True,
    )

    is_re_invoice = fields.Boolean(
        string="Es refacturable?"
    )

    @api.constrains('percentage')
    def check_percentage(self):
        if self.percentage < 0 or self.percentage > 100:
            raise ValidationError("Porcentaje incorrecto")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Ya existe un motivo con este mismo nombre.'),
        ('code_uniq', 'unique (code)', 'Ya existe un motivo con este mismo codigo.'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
