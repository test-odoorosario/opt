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

from openerp import models, fields
from openerp.exceptions import ValidationError


class LendingLot(models.Model):
    _inherit = 'lending.lot'

    state = fields.Selection(
        string='Estado',
        selection=[('in_progress', 'En proceso'), ('revised', 'Revisado'), ('done', 'Finalizado')],
        default='in_progress'
    )

    def finish_lot(self):
        """ Cambio de estado de lote a finalizado"""
        if any((lot.lending_lot_type_id.medical_audit or lot.lending_lot_type_id.dental_audit) and lot.state == 'in_progress' for lot in self):
            raise ValidationError('Los lotes deben ser revisados por la auditoría antes de finalizarlos.')
        return super(LendingLot, self).finish_lot()

    def revised_lot(self):
        """ Cambio de estado de lote a Revisado"""
        for lot in self:
            if lot.lending_lot_type_id.medical_audit or lot.lending_lot_type_id.dental_audit:
                lot.update({'state': 'revised'})

    def unlink(self):
        """ Se redefine la eliminacion de lote"""
        for lot in self:
            if lot.state in ['revised', 'done']:
                raise ValidationError('No se puede eliminar un lote finalizado o revisado.')
            return super(LendingLot, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
