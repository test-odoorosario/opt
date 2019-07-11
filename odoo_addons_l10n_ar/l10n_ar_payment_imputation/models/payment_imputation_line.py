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


class AbstractAccountPaymentImputationLine(models.AbstractModel):
    _name = 'abstract.payment.imputation.line'

    def _compute_amounts(self):
        for line in self:
            line.update({
                'amount_residual': abs(line.move_line_id.amount_residual_currency)
                if line.move_line_id.amount_currency else abs(line.move_line_id.amount_residual),
                'amount_total': abs(line.move_line_id.amount_currency)
                if line.move_line_id.amount_currency else abs(line.move_line_id.debit - line.move_line_id.credit),
                'amount_residual_company': abs(line.move_line_id.amount_residual),
                'amount_total_company': abs(line.move_line_id.debit - line.move_line_id.credit)
            })

    def _compute_currency_id(self):
        for line in self:
            line.currency_id = line.move_line_id.currency_id or line.move_line_id.company_currency_id

    def _compute_name(self):
        for line in self:
            invoice = line.move_line_id.invoice_id
            line.name = invoice.name_get()[0][1] if invoice else line.move_line_id.name

    name = fields.Char('Documento', compute='_compute_name')
    move_line_id = fields.Many2one('account.move.line', 'Documento')
    invoice_id = fields.Many2one('account.invoice', 'Factura')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id')
    company_currency_id = fields.Many2one(related='move_line_id.company_currency_id')
    amount_residual = fields.Monetary('Restante moneda comprobante', compute='_compute_amounts')
    amount_total = fields.Monetary('Total moneda comprobante', compute='_compute_amounts')
    amount_residual_company = fields.Monetary('Restante moneda empresa', compute='_compute_amounts')
    amount_total_company = fields.Monetary('Total moneda empresa', compute='_compute_amounts')
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        related='move_line_id.company_id',
        store=True,
        readonly=True,
        related_sudo=False
    )
    concile = fields.Boolean('Conciliacion completa')


class PaymentImputationLine(models.Model):
    _name = 'payment.imputation.line'
    _inherit = 'abstract.payment.imputation.line'

    @api.depends('payment_id.payment_date', 'company_currency_id', 'payment_currency_id')
    def _get_payment_amounts(self):
        for line in self:
            company_currency = line.company_currency_id
            payment_currency = line.payment_currency_id
            if payment_currency:
                date = line.payment_id.payment_date or fields.Date.today()
                residual = company_currency.with_context(date=date).compute(
                    line.amount_residual_company, payment_currency
                )
                total = company_currency.with_context(date=date).compute(
                    line.amount_total_company, payment_currency
                )
            else:
                residual = line.amount_residual_company
                total = line.amount_total_company

            line.update({
                'amount_residual_in_payment_currency': residual,
                'amount_total_in_payment_currency': total,
            })

    payment_id = fields.Many2one('account.payment', 'Pago', ondelete='cascade')
    amount = fields.Monetary('Total A imputar', currency_field='payment_currency_id')
    payment_currency_id = fields.Many2one(related='payment_id.currency_id', readonly=True)
    payment_state = fields.Selection(related='payment_id.state')
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

    def validate(self, invoice_move_line):
        """
        Valida que no haya problemas a la necesitar generar una imputacion a una invoice
        :param invoice_move_line: account.move.line de la invoice
        """
        self.ensure_one()
        # Caso que se modifique el asiento y deje inconsistencia
        if len(invoice_move_line) != 1:
            raise ValidationError("El asiento de la factura que se quiere imputar no tiene cuentas deudoras "
                                  "o tiene mas de una asociada, por favor, modificar el asiento primero")
        if self.amount_residual_in_payment_currency < self.amount or self.amount < 0:
            raise ValidationError("No se pueden imputar importes negativos o mayores que lo que reste pagar")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
