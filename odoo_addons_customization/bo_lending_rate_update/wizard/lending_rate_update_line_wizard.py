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


class LendingRateUpdateLineWizard(models.TransientModel):
    _name = 'lending.rate.update.line.wizard'

    def _get_available_lending_ids(self):
        prev_rate = self.env['lending.rate'].browse(self.env.context.get('rate_id'))
        return prev_rate.line_ids.mapped('lending_id')

    available_lending_ids = fields.Many2many(
        comodel_name="lending",
        string="Prestaciones disponibles",
        default=_get_available_lending_ids,
    )

    variation_percentage = fields.Float(
        string="Porcentaje de variacion",
    )

    wizard_id = fields.Many2one(
        comodel_name="lending.rate.update.wizard",
        string="Wizard",
    )

    lending_id = fields.Many2one(
        comodel_name="lending",
        string="Codigo",
        required=True,
        domain="[('id', 'in', available_lending_ids[0][2])]",
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
