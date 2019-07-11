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


class BankCardFee(models.Model):
    _inherit = 'bank.card.fee'

    percentage_of_accreditation = fields.Float(
        string='Porcentaje de acreditacion',
    )
    estimated_days_accreditation = fields.Integer(
        string='Dias estimados de acreditacion',
    )

    @api.constrains('percentage_of_accreditation')
    def validate_percentage(self):
        if self.percentage_of_accreditation > 100 or self.percentage_of_accreditation < 0:
            raise ValidationError('El porcentaje de acreditacion debe estar entre '
                                  '0 y 100.')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
