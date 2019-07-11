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


class LendingNomenclatorLine(models.Model):
    _name = 'lending.nomenclator.line'

    lending_id = fields.Many2one(
        comodel_name='lending',
        string='Prestacion',
        required=True
    )
    expense_type_id = fields.Many2one(
        comodel_name='lending.expense.type',
        string='Tipo de gasto',
    )
    unit_type_id = fields.Many2one(
        comodel_name='lending.expense.type',
        string='Tipo de gasto (galeno)',
    )
    code = fields.Char(
        string='Codigo',
        related='lending_id.code',
    )
    description = fields.Char(
        string='Descripcion',
        related='lending_id.name',
    )
    unit = fields.Float(
        string='Unidades',
    )
    unit_expense = fields.Float(
        string='Gastos',
    )
    amount = fields.Float(
        string='Importe',
    )
    amount_total = fields.Float(
        string='Importe',
        compute='_compute_amount_total',
        store=True,
    )
    nomenclator_id = fields.Many2one(
        comodel_name='lending.nomenclator',
        string='Nomenclador'
    )

    @api.multi
    @api.depends('unit', 'unit_expense', 'expense_type_id', 'unit_type_id')
    def _compute_amount_total(self):
        """ Calculo el importe de la prestacion segun las unidades y tipo de gasto"""
        for line in self:
            total = line.amount or 0
            if line.expense_type_id or line.unit_type_id:
                coefficient = line.expense_type_id.coefficient if line.expense_type_id else 1
                coefficient_galeno = line.unit_type_id.coefficient if line.unit_type_id else 1
                total = line.unit * coefficient_galeno + line.unit_expense * coefficient
            line.amount_total = round(total, 2)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
