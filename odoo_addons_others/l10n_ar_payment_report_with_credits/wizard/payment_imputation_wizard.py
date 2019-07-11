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


class PaymentImputationWizard(models.TransientModel):
    _inherit = 'payment.imputation.wizard'

    def create_payment(self):
        previous_debit_ids = self._get_imputation_vals_for_payment()
        previous_credit_ids = self._get_imputation_credit_vals_for_payment()
        self._validate_payment_imputation()
        self.reconcile_credits()
        payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids \
                          or self.journal_id.outbound_payment_method_ids

        payment = self.env['account.payment'].create({
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'payment_type': self.payment_type,
            'partner_type': 'customer' if self.payment_type == 'inbound' else 'supplier',
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'amount': self.total,
            'payment_imputation_ids': self._get_imputation_vals_for_payment(),
            'imputation_debit_ids': previous_debit_ids,
            'imputation_credit_ids': previous_credit_ids,
            'payment_date': self.date or fields.Date.today(),
            'currency_id': self.currency_id.id,
            'advance_amount': self.advance_amount
        })

        return {
            'name': 'Pago',
            'views': [[False, "form"], [False, "tree"]],
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': payment.id,
        }

    def _get_imputation_credit_vals_for_payment(self):
        payment_credit_imputations = []
        for imputation in self.credit_imputation_line_ids.filtered(lambda x: x.amount):
            payment_credit_imputations.append((0, 0, {
                'invoice_id': imputation.invoice_id.id,
                'move_line_id': imputation.move_line_id.id,
                'concile': imputation.concile,
                'amount': imputation.amount,
            }))

        return payment_credit_imputations

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
