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
import re


class ResCompany(models.Model):
    _inherit = 'res.company'

    configuration_hour_projection = fields.Char(
        string='Horario para proyeccion de cupones',
    )

    @api.constrains('configuration_hour_projection')
    def constrain_hour(self):
        obj = re.match(r"^((1|0)?[0-9]|2[0-3]):[0-5][0-9]$",
                       self.configuration_hour_projection or '')
        if not obj and self.configuration_hour_projection:
            raise ValidationError("Hora invalida, por favor ingrese un horario valido.")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
