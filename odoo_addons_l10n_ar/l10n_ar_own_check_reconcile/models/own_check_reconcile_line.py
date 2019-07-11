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


class OwnCheckReconcileLine(models.Model):
    _name = 'own.check.reconcile.line'

    reconcile_id = fields.Many2one(
        comodel_name='own.check.reconcile',
        string="Conciliacion",
    )

    check_id = fields.Many2one(
        comodel_name='account.own.check',
        string="Cheque",
        required=True,
    )

    check_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Contrapartida",
        compute='get_check_account'
    )

    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Cuenta",
    )

    amount = fields.Monetary(
        string="Monto",
        related='check_id.amount',
    )

    currency_id = fields.Many2one(
        string="Moneda",
        related='check_id.currency_id',
    )

    def get_check_account(self):
        for line in self:
            line.check_account_id = line.check_id.checkbook_id.account_id or line.check_id.checkbook_id.journal_id.default_debit_account_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
