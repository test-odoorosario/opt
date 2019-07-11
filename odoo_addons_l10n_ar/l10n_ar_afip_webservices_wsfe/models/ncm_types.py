
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class NCMTypes(models.Model):

    _name = 'ncm.types'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Code', required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            return self.search(['|', ('name', operator, name), ('code', operator, name)] + args,
                               limit=limit).name_get()
        return super(NCMTypes, self).name_search(name, args, operator, limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: