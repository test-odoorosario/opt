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
from openerp.exceptions import ValidationError


class PosAr(models.Model):

    _inherit = 'pos.ar'

    COPIES = {
        0: 'ORIGINAL',
        1: 'DUPLICADO',
        2: 'TRIPLICADO',
        3: 'CUADRIPLICADO'
    }

    invoicing_address_id = fields.Many2one(
        'res.partner',
        'Dirección de facturación',
        help='Se utilizará la dirección de este partner en las facturas electrónicas'
    )
    copies_quantity = fields.Integer(
        string='Cantidad de copias',
        default=2,
    )

    def get_copie_name(self, key):
        """ Devuelvo el nombre de la copia del reporte """
        if self.COPIES.get(key):
            return self.COPIES[key]

    @api.constrains('copies_quantity')
    def check_quantity(self):
        """ Chequeo los valores de la cantidad de copias"""
        if self.copies_quantity < 1:
            raise ValidationError('La cantidad de copias no puede ser menor que 1.')
        if self.copies_quantity > 4:
            raise ValidationError('Si desea imprimir más de 4 copias por favor contáctese con el administrador.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
