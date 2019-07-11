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


class LendingLotType(models.Model):
    _inherit = 'lending.lot.type'

    medical_audit = fields.Boolean(
        string='Auditoría médica'
    )
    dental_audit = fields.Boolean(
        string='Auditoría odontológica'
    )

    @api.constrains('medical_audit', 'dental_audit')
    def check_type_audit(self):
        for lot_type in self:
            if lot_type.medical_audit and lot_type.dental_audit:
                raise ValidationError('El tipo de lote solo puede pertenecer a una sola auditoría o ninguna.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
