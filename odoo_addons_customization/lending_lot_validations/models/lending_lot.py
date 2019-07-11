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


class LendingLot(models.Model):
    _inherit = 'lending.lot'

    total_to_pay = fields.Float(
        string='Total a pagar',
        compute='get_total_to_pay'
    )

    def validate_registry(self):
        self.ensure_one()
        for registry in self.registry_lending_ids:
            registry.validate()

    @api.model
    def create(self, vals):
        res = super(LendingLot, self).create(vals)
        res.registry_lending_ids.validate()
        return res

    def get_total_to_pay(self):
        for lot in self:
            lot.total_to_pay = sum(lot.registry_lending_ids.mapped('total_to_pay'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
