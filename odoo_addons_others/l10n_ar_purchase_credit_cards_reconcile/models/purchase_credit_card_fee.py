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


class PurchaseCreditCardFee(models.Model):

    _inherit = 'purchase.credit.card.fee'

    reconciled = fields.Boolean('Conciliado', readonly=True)
    conciliation_ids = fields.Many2many(
        'purchase.credit.card.fee',
        'credit_card_fee_conciliation_rel',
        'fee_id',
        'conciliation_id',
        string='conciliaciones'
    )

    @api.constrains('conciliation_ids')
    def constraint_multiple_conciliations(self):
        for fee in self:
            if len(fee.conciliation_ids) > 1:
                raise ValidationError("Una cuota no puede pertenecer a múltiples conciliaciones.")

    def reconcile(self):
        self.write({'reconciled': True})

    def cancel_reconcile(self):
        self.write({'reconciled': False})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
