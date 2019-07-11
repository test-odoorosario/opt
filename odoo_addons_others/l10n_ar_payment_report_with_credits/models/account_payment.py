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


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    imputation_debit_ids = fields.One2many(
        comodel_name='account.payment.imputation.line',
        inverse_name='payment_debit_id',
        string='Débitos'
    )
    imputation_credit_ids = fields.One2many(
        comodel_name='account.payment.imputation.line',
        inverse_name='payment_credit_id',
        string='Créditos'
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
