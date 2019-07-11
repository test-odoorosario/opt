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
ROUND_PRECISION = 2


class PaymentImputationWizard(models.TransientModel):
    _name = 'payment.imputation.wizard'

    @api.depends('debit_imputation_line_ids', 'advance_amount', 'credit_imputation_line_ids')
    def _get_total_payment(self):
        self.total = sum(self.debit_imputation_line_ids.mapped('amount')) - \
                     sum(self.credit_imputation_line_ids.mapped('amount')) \
                     + self.advance_amount

    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id
    )
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], 'Tipo')
    advance_amount = fields.Monetary('Importe a cuenta')
    journal_id = fields.Many2one(
        'account.journal',
        domain=[('type', 'in', ('bank', 'cash'))],
        default=lambda l: l.env.user.company_id.default_payment_journal_id.id,
        required=True
    )
    debit_imputation_line_ids = fields.One2many(
        'payment.imputation.debit.line.wizard',
        'wizard_id',
        'Débitos',
    )
    credit_imputation_line_ids = fields.One2many(
        'payment.imputation.credit.line.wizard',
        'wizard_id',
        'Créditos',
    )

    total = fields.Monetary('Total', compute=_get_total_payment)
    date = fields.Date('Fecha')

    @api.onchange('payment_type')
    def onchange_type(self):
        partner_type = 'customer' if self.payment_type == 'inbound' else 'supplier'
        return {'domain': {'partner_id': [(partner_type, '=', True)]}}

    @api.onchange('partner_id')
    def onchange_partner_id(self):

        lines = self._get_move_lines() if self.partner_id else None

        debit_lines = [(0, 0, {
            'invoice_id': line.invoice_id.id,
            'move_line_id': line.id
        }) for line in lines.get('debit_lines')] if lines and lines.get('debit_lines') else None

        credit_lines = [(0, 0, {
            'invoice_id': line.invoice_id.id,
            'move_line_id': line.id
        }) for line in lines.get('credit_lines')] if lines and lines.get('credit_lines') else None

        self.update({
            'debit_imputation_line_ids': debit_lines,
            'credit_imputation_line_ids': credit_lines
        })

    def _get_move_lines(self):
        account_type = 'receivable' if self.payment_type == 'inbound' else 'payable'
        search_domain = [
            ('account_id.user_type_id.type', '=', account_type),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0.0)
        ]
        lines = self.env['account.move.line'].search(search_domain)

        return {
            'debit_lines':  lines.filtered(lambda x: x.debit > 0 if account_type == 'receivable' else x.credit > 0),
            'credit_lines': lines.filtered(lambda x: x.credit > 0 if account_type == 'receivable' else x.debit > 0)
        }

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.env.user.company_id.currency_id
            for l in self.debit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()
            for l in self.credit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()

    def create_payment(self):
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

    def reconcile_credits(self):
        """
        Imputa los créditos seleccionados.
        """

        # Borramos las imputaciones que no se van a realizar
        self.debit_imputation_line_ids.filtered(lambda x: not x.amount).unlink()
        self.credit_imputation_line_ids.filtered(lambda x: not x.amount).unlink()

        lines_to_concile = self.env['account.move.line']

        for imputation in self.credit_imputation_line_ids:

            company_currency = self.env.user.company_id.currency_id

            for line in self.debit_imputation_line_ids.filtered(lambda x: x.move_line_id.account_id):

                line_amount = line.amount

                # Si se imputo el restante, ajustamos el valor para ajustar las imprecisiones de usar 2 decimales
                if round(line_amount - imputation.amount, ROUND_PRECISION) == 0:
                    self.debit_imputation_line_ids -= line
                    (line.move_line_id + imputation.move_line_id).reconcile()
                    break

                # En el caso que no sean iguales, uno de los dos debe ser mayor que el otro, agarramos el minimo
                minimun_amount = min(line_amount, imputation.amount)

                line.amount -= minimun_amount
                imputation.amount -= minimun_amount
                imputation_amount = company_currency.with_context(date=self.date or fields.Date.today()).compute(
                    minimun_amount, self.currency_id, round=False
                )

                debit_move = imputation.move_line_id if imputation.move_line_id.debit > 0 else line.move_line_id
                credit_move = imputation.move_line_id if imputation.move_line_id.credit > 0 else line.move_line_id

                lines_to_concile |= line.move_line_id

                # Si no se imputo el total de la factura, creamos una conciliacion parcial
                self.env['account.partial.reconcile'].with_context(skip_full_reconcile_check=True).create({
                    'debit_move_id': debit_move.id,
                    'credit_move_id': credit_move.id,
                    'amount': imputation_amount,
                    'amount_currency': minimun_amount if self.currency_id != company_currency else 0.0,
                    'currency_id': self.currency_id.id if self.currency_id != company_currency else False
                })

                # Si lo imputado es menor que lo restante a imputar, pasamos a la otra imputación,
                # si no, sacamos la factura.
                if imputation.amount > 0:
                    self.debit_imputation_line_ids -= line
                else:
                    break

        lines_to_concile.filtered(lambda l: not l.reconciled).reconcile()
        self.credit_imputation_line_ids.unlink()

    def _validate_payment_imputation(self):
        """ Valida los importes registrados a imputar """
        if self.advance_amount < 0:
            raise ValidationError("El importe a cuenta no puede ser menor a 0.")
        if self.total <= 0:
            raise ValidationError("El importe a pagar debe ser positivo.")

        self._validate_imputation_amounts()

    def _validate_imputation_amounts(self):
        """ Valida que los créditos a imputar no sean mayor que los débitos, por cada cuenta contable a imputar. """
        debit_imputations = self.debit_imputation_line_ids.filtered(lambda x: x.amount)
        credit_imputations = self.credit_imputation_line_ids.filtered(lambda x: x.amount)

        debit_accounts = debit_imputations.mapped('move_line_id').mapped('account_id')
        credit_accounts = credit_imputations.mapped('move_line_id').mapped('account_id')

        if credit_accounts | debit_accounts != debit_accounts:
            raise ValidationError(
                "No se pueden imputar créditos de movimientos que tengan "
                "cuentas contables que no se encuentre en los débitos."
            )

        for account in debit_accounts:
            debits = debit_imputations.filtered(lambda x: x.move_line_id.account_id == account)
            credits = credit_imputations.filtered(lambda x: x.move_line_id.account_id == account)
            if sum(debits.mapped('amount')) < sum(credits.mapped('amount')):
                raise ValidationError(
                    "Los créditos a imputar superan a los débitos para la cuenta contable {}".format(account.name)
                )

    def _get_imputation_vals_for_payment(self):
        payment_imputations = []
        for imputation in self.debit_imputation_line_ids.filtered(lambda x: x.amount):
            payment_imputations.append((0, 0, {
                'invoice_id': imputation.invoice_id.id,
                'move_line_id': imputation.move_line_id.id,
                'concile': imputation.concile,
                'amount': imputation.amount,
            }))

        return payment_imputations

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
