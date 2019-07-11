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


class PaymentImputationLineWizardAbstract(models.AbstractModel):

    _name = 'payment.imputation.line.wizard.abstract'
    _inherit = 'abstract.payment.imputation.line'

    @api.depends('wizard_id.date', 'company_currency_id', 'payment_currency_id')
    def _get_payment_amounts(self):
        for line in self:
            company_currency = line.company_currency_id
            payment_currency = line.payment_currency_id
            date = line.wizard_id.date or fields.Date.today()
            residual = company_currency.with_context(date=date).compute(
                line.amount_residual_company, payment_currency
            )
            total = company_currency.with_context(date=date).compute(
                line.amount_total_company, payment_currency
            )
            line.update({
                'amount_residual_in_payment_currency': residual,
                'amount_total_in_payment_currency': total,
            })

    wizard_id = fields.Many2one('payment.imputation.wizard')
    amount = fields.Monetary('Total A imputar', currency_field='payment_currency_id')
    payment_currency_id = fields.Many2one(related='wizard_id.currency_id')
    amount_residual_in_payment_currency = fields.Monetary(
        compute='_get_payment_amounts',
        currency_field='payment_currency_id'
    )
    amount_total_in_payment_currency = fields.Monetary(
        compute='_get_payment_amounts',
        currency_field='payment_currency_id'
    )

    @api.onchange('concile')
    def onchange_concile(self):
        self.amount = self.amount_residual_in_payment_currency if self.concile else self.amount

    @api.onchange('amount')
    def onchange_amount(self):
        self.concile = self.amount == self.amount_residual_in_payment_currency


class PaymentImputationCreditLineWizard(models.TransientModel):

    _name = 'payment.imputation.credit.line.wizard'
    _inherit = 'payment.imputation.line.wizard.abstract'


class PaymentImputationDebitLineWizard(models.TransientModel):

    _name = 'payment.imputation.debit.line.wizard'
    _inherit = 'payment.imputation.line.wizard.abstract'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
