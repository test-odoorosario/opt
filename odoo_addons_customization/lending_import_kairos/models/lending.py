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


class Lending(models.Model):
    _inherit = 'lending'

    description_drug = fields.Char(
        string='Principio activo'
    )
    description_laboratory = fields.Char(
        string='Laboratorio'
    )
    description_presentation = fields.Char(
        string='Gramaje y presentación'
    )
    description_product = fields.Char(
        string='Marca comercial'
    )

    def name_get(self):
        vals = []
        for r in self:
            name_list = ["[{}] {}".format(r.code, r.name)]
            if r.medicine:
                name_list.append("{} - {}".format(r.description_drug, r.description_presentation))
            vals.append((r.id, " ".join(name_list)))
        return vals

    @api.onchange('medicine')
    def onchange_medicine(self):
        self.update({
            'description_drug': False,
            'description_laboratory': False,
            'description_presentation': False,
            'description_product': False,
            'lending_ids': False,
            'has_coinsurance': False
        })

    @api.constrains('code', 'medicine')
    def check_code_unique_no_medicine(self):
        """ Creo esta restricción porque la de SQL no salta cuando los datos de medicamento están vacíos """
        if any(self.search_count([('code', '=', r.code), ('id', '!=', r.id), ('medicine', '=', False)]) >= 1 for r in self):
            raise ValidationError("Ya existe una prestación con este mismo código")

    _sql_constraints = [
        ('code_uniq',
         'unique (code, description_drug, description_laboratory, description_presentation, description_product)',
         'Ya existe una prestación con este mismo código y datos de medicamento.')
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
