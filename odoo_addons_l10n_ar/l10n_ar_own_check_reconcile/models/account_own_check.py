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

from openerp import models, fields
from openerp.exceptions import ValidationError


class AccountOwnCheck(models.Model):
    _inherit = 'account.own.check'

    reconcile_id = fields.Many2one(
        comodel_name='own.check.reconcile',
        string="Conciliacion",
    )
    state = fields.Selection(selection_add=[('reconciled', "Conciliado")])

    def reconcile_check(self, vals):
        """ Lo que deberia pasar con el cheque cuando se lo concilia.. """
        if any(c.state not in ['handed', 'collect'] for c in self):
            raise ValidationError("Los cheques propios a conciliar deben estar en estado entregado o cobrado")
        self.next_state('handed_collect_reconciled')
        vals = vals or {}
        self.write(vals)

    def cancel_reconcile(self):
        """ Lo que deberia pasar con el cheque cuando se cancela su conciliacion.. """
        if any(check.state != 'reconciled' for check in self):
            raise ValidationError("Los cheques propios deben estar en estado conciliado para cancelar la conciliacion")
        for c in self:
            if c.destination_payment_id:
                c.cancel_state('reconciled_handed')
            elif c.collect_move_id and c.collect_date:
                c.cancel_state('reconciled_collect')
            else:
                raise ValidationError("No es posible cancelar la conciliacion ya que no hay informacion suficiente para determinar el estado anterior del cheque")
        self.write({'reconcile_id': None})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
