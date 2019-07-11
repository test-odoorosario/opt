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


class LendingCie10(models.Model):
    _name = 'lending.cie10'

    name = fields.Char(
        string='Codigo',
        required=True,
    )
    description = fields.Text(
        string='Descripcion',
        required=True,
    )

    def name_get(self):
        vals = []
        for c in self:
            name_list = ["[{}] {} ".format(c.name, c.description)]
            vals.append((c.id, " ".join(name_list)))
        return vals

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            return self.search(['|', ('name', operator, name), ('description', operator, name)] + args, limit=limit).name_get()
        return super(LendingCie10, self).name_search(name, args, operator, limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
