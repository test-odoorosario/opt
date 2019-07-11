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


class LendingRateLine(models.Model):
    _inherit = 'lending.rate.line'

    value_final = fields.Float(
        string='Importe final',
        compute='calculate_value'
    )

    def calculate_value(self):
        for line in self:
            if not line.code_range:
                nomenclator_line = self.env['lending.nomenclator.line'].search(
                    [('code', '=', line.lending_id.code)],
                    limit=1
                )
                value = line.value
                if nomenclator_line and line.nomenclator_id:
                    CALCULATION_TYPE = {
                        'galeno': nomenclator_line.unit * line.value,
                        'expense': nomenclator_line.unit_expense * line.value,
                        'galeno_expense': nomenclator_line.unit * line.value_galeno + nomenclator_line.unit_expense * line.value,
                        'final_amount': nomenclator_line.amount_total * line.value
                    }
                    value = CALCULATION_TYPE.get(str(line.calculation_type))
                line.value_final = value
            else:
                line.value_final = 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
