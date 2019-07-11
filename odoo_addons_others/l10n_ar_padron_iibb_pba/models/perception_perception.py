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

from openerp import models
from openerp.exceptions import ValidationError


class PerceptionPerception(models.Model):

    _inherit = 'perception.perception'

    def get_iibb_pba_perception(self):

        perception = self.search([
            ('type', '=', 'gross_income'),
            ('jurisdiction', '=', 'provincial'),
            ('state_id', '=', self.env.ref('base.state_ar_b').id),
            ('type_tax_use', '=', 'sale')
        ], limit=1)

        if not perception:
            raise ValidationError("No se encontro percepcion de IIBB de PBA, por favor, crear una")

        return perception

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
