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


class AccountPaymentImputation(models.Model):
    _name = 'account.payment.imputation.line'
    _inherit = 'payment.imputation.line'

    payment_credit_id = fields.Many2one(
        comodel_name='account.payment',
        string='Pago'
    )

    payment_debit_id = fields.Many2one(
        comodel_name='account.payment',
        string='Pago'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
