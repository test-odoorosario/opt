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


class PurchaseCreditCardConciliation(models.Model):   # Maneja las acciones al cambiar sus estados

    _name = 'purchase.credit.card.conciliation'

    @api.depends('fee_ids')
    def _get_conciliation_total(self):
        for each in self:
            each.amount = sum(fee.amount for fee in each.fee_ids)

    name = fields.Char(
        'Nombre',
        required=True
    )
    date = fields.Date(
        'Fecha de conciliación',
        required=True
    )
    date_from = fields.Date(
        'Fecha desde',
        required=True
    )
    date_to = fields.Date(
        'Fecha hasta',
        required=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Cuenta Bancaria',
        required=True,
        ondelete='restrict'
    )
    credit_card_id = fields.Many2one(
        'credit.card',
        'Tarjeta',
        required=True,
        ondelete='restrict'
    )
    amount = fields.Monetary(
        'Importe total',
        compute='_get_conciliation_total',
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda'
    )
    fee_ids = fields.Many2many(
        'purchase.credit.card.fee',
        'credit_card_fee_conciliation_rel',
        'conciliation_id',
        'fee_id',
        string='Cuotas'
    )
    state = fields.Selection(
        [('canceled', 'Cancelada'),
         ('draft', 'Borrador'),
         ('reconciled', 'Conciliada')],
        string='Estado',
        default='draft',
    )
    move_id = fields.Many2one(
        'account.move',
        'Asiento contable',
        readonly=True,
        ondelete='restrict'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    _sql_constraints = [('name_uniq', 'unique(name)', 'El nombre de la conciliacion debe ser unico')]
    _order = "date_from desc, name desc"

    @api.constrains('date_from', 'date_to')
    def constraint_dates(self):
        for conciliation in self:
            if conciliation.date_from > conciliation.date_to:
                raise ValidationError("La fecha desde debe ser menor que la fecha hasta.")

    @api.constrains('fee_ids')
    def constraint_fees(self):
        for conciliation in self:
            if len(conciliation.fee_ids.mapped('currency_id')) > 1:
                raise ValidationError("Las conciliaciones deben ser de cuotas en la misma moneda.")
            if len(conciliation.fee_ids.mapped('credit_card_id')) > 1:
                raise ValidationError("Las conciliaciones deben ser de cuotas de la misma tarjeta.")

    @api.multi
    def post(self):
        for conciliation in self:
            if not conciliation.fee_ids:
                raise ValidationError("No se puede validar una conciliación sin cuotas.")

            conciliation.write({
                # Ya validamos en el constraint que la moneda es unica
                'currency_id': conciliation.fee_ids.mapped('currency_id').id,
                'state': 'reconciled'
            })
            conciliation.move_id = conciliation.create_move()
            conciliation.fee_ids.reconcile()

    @api.multi
    def cancel(self):
        for conciliation in self:
            move = conciliation.move_id
            conciliation.move_id = None
            move.button_cancel()
            move.unlink()
            conciliation.fee_ids.cancel_reconcile()
            conciliation.state = 'canceled'

    @api.multi
    def cancel_to_draft(self):
        self.write({'state': 'draft'})


class PurchaseCreditCardConciliationMove(models.Model):  # Crea el asiento de conciliación

    _inherit = 'purchase.credit.card.conciliation'

    def create_move(self):
        self.ensure_one()

        vals = {
            'date': self.date,
            'ref': 'Conciliacion de tarjetas: ' + self.name,
            'journal_id': self.journal_id.id,
        }
        move = self.env['account.move'].create(vals)

        # Hacemos el computo multimoneda
        company = self.env.user.company_id
        debit, credit, amount_currency, currency_id = self.env['account.move.line'].with_context(date=self.date).\
            compute_amount_fields(self.amount, self.currency_id, company.currency_id)

        # Creamos las lineas de los asientos
        self._create_move_lines(move, amount_currency, debit=debit)
        self._create_move_lines(move, -amount_currency, credit=debit)
        move.post()
        return move

    def _create_move_lines(self, move, amount_currency, debit=0.0, credit=0.0):
        """
        Crea una move line de la boleta de deposito y las asocia al move
        :param move: account.move - Asiento a relacionar las move_lines creadas
        :param debit: Importe en el haber de la move line
        :param credit: Importe en el haber de la move line
        :return: account.move.line creada
        """

        account_id = self.journal_id.default_debit_account_id.id if debit else\
            self.fee_ids.mapped('credit_card_id').account_id.id
        company_currency = self.env.user.company_id.currency_id

        move_line_vals = {
            'move_id': move.id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency,
            'name': move.ref,
            'account_id': account_id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != company_currency and self.currency_id.id or False,
            'ref': move.ref
        }
        return self.env['account.move.line'].with_context(check_move_validity=False).create(move_line_vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
