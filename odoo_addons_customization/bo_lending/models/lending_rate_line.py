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


class LendingRateLine(models.Model):
    _name = 'lending.rate.line'
    _rec_name = 'lending_id'
    _order = 'id'

    lending_id = fields.Many2one(
        comodel_name='lending',
        string='Codigo',
        required=True,
    )
    code_range = fields.Char(
        string="Codigo hasta",
    )
    calculation_type = fields.Selection(
        selection=[
            ('galeno', 'Galeno'),
            ('expense', 'Gasto'),
            ('galeno_expense', 'Galeno y gasto'),
            ('final_amount', 'Importe final')],
        string='Tipo calculo'
    )
    value = fields.Float(
        string='Valor'
    )
    value_galeno = fields.Float(
        string='Valor Galeno'
    )
    lender_code = fields.Char(
        string='Codigo prestador',
    )
    description = fields.Text(
        string='Descripcion',
        required=True,
    )
    rate_id = fields.Many2one(
        comodel_name='lending.rate',
        string='Tarifario',
        ondelate='cascade'
    )
    nomenclator_id = fields.Many2one(
        comodel_name='lending.nomenclator',
        string='Basado en',
    )
    no_agreed = fields.Boolean(
        string='No convenido'
    )
    plan_ids = fields.Many2many(
        comodel_name='lending.plan.agreement',
        string='Planes',
        copy=False,
    )
    category_ids = fields.Many2many(
        comodel_name='lending.category',
        string='Categorias',
        copy=False,
    )

    @api.onchange('lending_id')
    def onchange_lending_id(self):
        self.description = self.lending_id.name

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
