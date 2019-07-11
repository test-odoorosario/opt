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


class LendingKairosLine(models.Model):
    _name = 'lending.kairos.line'

    lending_id = fields.Many2one(
        comodel_name='lending',
        string='Medicamento'
    )
    code = fields.Char(
        related='lending_id.code',
        string='Codigo'
    )
    name = fields.Char(
        related='lending_id.name',
        string='Descripcion'
    )
    description_drug = fields.Char(
        related='lending_id.description_drug',
        string='Principio activo'
    )
    description_laboratory = fields.Char(
        related='lending_id.description_laboratory',
        string='Laboratorio'
    )
    description_presentation = fields.Char(
        related='lending_id.description_presentation',
        string='Gramaje y presentación'
    )
    description_product = fields.Char(
        related='lending_id.description_product',
        string='Marca comercial'
    )
    value = fields.Float(
        string='Valor',
        digits=(12, 6)
    )
    date = fields.Date(
        string='Fecha de vigencia'
    )
    value_line_ids = fields.One2many(
        'lending.kairos.value.line',
        'kairos_id',
        string="Valores"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
