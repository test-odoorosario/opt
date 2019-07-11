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
from datetime import datetime


class OwnCheckReconcile(models.Model):
    _name = 'own.check.reconcile'
    _inherit = 'mail.thread'

    def get_lines_from_checks(self, checks):
        ids = []
        for check in checks:
            ids.append(self.env['own.check.reconcile.line'].create({
                'check_id': check.id,
            }).id)
        return ids

    def _get_lines(self):
        ids = self.get_lines_from_checks(self.env['account.own.check'].browse(self.env.context.get('active_ids')))
        self.validate_lines(ids)
        return [(6, 0, ids)]

    def validate_lines(self, ids):
        if any(c.check_id.state not in ['handed', 'collect'] for c in self.env['own.check.reconcile.line'].browse(ids)):
            raise ValidationError("Todos los cheques a conciliar deben estar entregados o cobrados")

    date = fields.Date(
        default=fields.Date.context_today,
        string="Fecha",
        required=True,
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Diario",
    )

    general_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Cuenta general",
    )

    move_id = fields.Many2one(
        comodel_name='account.move',
        string="Asiento",
        readonly=True,
    )

    line_ids = fields.One2many(
        comodel_name='own.check.reconcile.line',
        inverse_name='reconcile_id',
        string="Lineas",
        default=_get_lines,
    )

    state = fields.Selection(
        string="Estado",
        selection=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmada'),
            ('canceled', 'Cancelada'),
        ],
        required=True,
        default='draft',
        track_visibility='onchange',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    def name_get(self):
        res = []
        for r in self:
            res.append(
                (r.id, "{} - {}".format(datetime.strptime(r.date, '%Y-%m-%d').strftime('%d/%m/%Y'), r.journal_id.name)))
        return res

    @api.model
    def create(self, vals):
        """
        Redefino el create porque al confirmar en el popup se crea el objeto y pierdo la referencia a las lineas
        :param vals: valores de la creacion
        :return: objeto creado
        """
        res = super(OwnCheckReconcile, self).create(vals)
        if vals.get('line_ids') and not res.line_ids:
            line_ids = [val[1] for val in vals['line_ids']]
            res.line_ids = [(6, 0, line_ids)]
        return res

    def unlink(self):
        if 'confirmed' in self.mapped('state'):
            raise ValidationError("No se pueden eliminar conciliaciones confirmadas.")
        return super(OwnCheckReconcile, self).unlink()

    def cancel(self):
        for r in self:
            r.move_id.button_cancel()
            r.move_id.unlink()
            r.line_ids.mapped('check_id').cancel_reconcile()
        self.write({
            'state': 'canceled',
        })

    @api.onchange('general_account_id')
    def onchange_general_account(self):
        self.line_ids.update({'account_id': self.general_account_id})

    def confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError("La conciliacion a confirmar no posee lineas.")
        if any(not l.check_account_id for l in self.line_ids):
            raise ValidationError("La cuenta bancaria no tiene cuentas contables configuradas.\n"
                                  "Por favor, configurarla en el diario correspondiente o en la chequera")

        move_line_proxy = self.env['account.move.line'].with_context(check_move_validity=False)
        date = datetime.strptime(self.date, '%Y-%m-%d').strftime('%d/%m/%Y')
        move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'state': 'draft',
            'date': self.date,
            'ref': 'Conciliacion de cheques propios {}'.format(date)
        })

        for line in self.line_ids:
            check = line.check_id
            company_currency = self.env.user.company_id.currency_id
            line_currency = check.currency_id.id if check.currency_id != company_currency else False
            debit, credit, amount_currency, currency_id = move_line_proxy.with_context(
                date=self.date).compute_amount_fields(line.amount, check.currency_id, company_currency)

            # La funcion anterior te devuelve el valor en credit o debit dependiendo
            # del signo de monto por lo tanto aca dejamos que credit sea igual que debit
            # simplemente a modo que sea mas comprensible la creacion de lineas de asiento
            credit = debit

            move_line_proxy.create({
                'name': 'Conciliacion de cheque propio {}'.format(check.name),
                'account_id': line.check_account_id.id,
                'journal_id': self.journal_id.id,
                'date': self.date,
                'credit': 0,
                'debit': debit,
                'state': 'valid',
                'move_id': move.id,
                'amount_currency': amount_currency,
                'currency_id': line_currency,
            })
            move_line_proxy.create({
                'name': 'Conciliacion de cheque propio {}'.format(check.name),
                'account_id': line.account_id.id,
                'journal_id': self.journal_id.id,
                'date': self.date,
                'credit': credit,
                'debit': 0,
                'state': 'valid',
                'move_id': move.id,
                'amount_currency': -amount_currency,
                'currency_id': line_currency,
            })
            check.reconcile_check({'reconcile_id': self.id})

        move.post()
        self.write({
            'move_id': move.id,
            'state': 'confirmed',
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
