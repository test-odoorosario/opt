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

from openerp import models, api
from openerp.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('partner_document_type_id', 'vat')
    def check_document_type_vat(self):
        if any(r.vat and self.search_count([('partner_document_type_id', '=', r.partner_document_type_id.id),
            ('vat', '=', r.vat), ('id', '!=', r.id)]) for r in self):
            raise ValidationError("Ya existe un cliente o proveedor con ese documento")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
