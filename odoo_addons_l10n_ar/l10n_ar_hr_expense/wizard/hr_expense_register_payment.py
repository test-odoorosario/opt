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

from openerp import api, models, fields
from werkzeug import url_encode
from openerp.exceptions import ValidationError


class HrExpenseRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.register.payment.wizard"

    payment_type_line_ids = fields.Many2many(
        'account.payment.type.line',
        'hr_expense_register_payment_line_rel',
        'payment_id',
        'line_id',
        'Lineas de pagos'
    )

    def get_payment_vals(self):
        """ Se redefine la funcion para tomar los metodos de pago"""
        res = super(HrExpenseRegisterPaymentWizard, self).get_payment_vals()
        res['payment_type_line_ids'] = [(4, payment) for payment in self.payment_type_line_ids.ids]
        return res

    @api.multi
    def expense_post_payment(self):
        """ El metodo es el standard para generar y postear pagos desde gastos, 
        nos aseguramos que no se utilice en otro lado que no es contemplado """
        raise ValidationError("Funcion de validacion de pago estandar deshabilitada")
        return super(HrExpenseRegisterPaymentWizard, self).expense_post_payment()

    @api.multi
    def expense_post_l10n_ar_payment(self):
        """ Se redefine la funcion de posteo de pagos desde gasto para realiace la funcion de la localizacion"""
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)

        # Creo el pago y lo posteo
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.onchange_payment_type()
        payment.post_l10n_ar()

        # Loggeo de pago en el chat
        body = ("Se ha realizado un pago de %s %s con referencia a <a href='/mail/view?%s'>%s</a> relacionada con su "
                "gasto %s" % ("{0:.2f}".format(payment.amount), payment.currency_id.symbol, url_encode({
                    'model': 'account.payment', 'res_id': payment.id
                }), payment.name, expense_sheet.name))
        expense_sheet.message_post(body=body)

        # Conciliacion del pago con el gasto
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable':
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
