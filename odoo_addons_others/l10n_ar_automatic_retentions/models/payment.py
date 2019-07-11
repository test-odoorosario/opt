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


from dateutil.relativedelta import relativedelta

from openerp import api
from openerp import fields, models
from ..models import retention_retention


def get_accumulated_payments(model, partner, date):
    """
    Busca los pagos para ese partner del periodo (principio y fin de mes de la fecha)
    :param model: models.Model()
    :param partner: res.partner del cual se buscaran los pagos
    :param date: Fecha de la cual se considerará el periodo
    """
    payments = model.env['account.payment'].search([
        ('payment_type', '=', 'outbound'),
        ('partner_id', '=', partner.id),
        ('state', 'not in', ['draft', 'sent']),
        ('payment_date', '>=', fields.Date.to_string(date.replace(day=1))),
        ('payment_date', '<', fields.Date.to_string(date.replace(day=1) + relativedelta(months=1)))
    ])

    return payments


class AccountAbstractPayment(models.AbstractModel):

    _inherit = 'account.abstract.payment'

    @api.onchange('partner_id')
    def onchange_partner_imputation(self):
        super(AccountAbstractPayment, self).onchange_partner_imputation()
        """ Para los casos que se paga una o mas facturas, pero se preseleccionan """
        if self.payment_type == 'outbound' and self.env.context.get('active_model') == 'account.invoice':
            self.create_retentions()

    def get_amount_to_tax(self):
        """
        Busca el importe a retener en base a las imputaciones realizadas
        :return: Importe a retener
        """
        self.ensure_one()
        amount = self.advance_amount
        for imputation in self.payment_imputation_ids:
            invoice = imputation.invoice_id

            if invoice:
                if invoice.amount_to_tax or invoice.amount_exempt:
                    amount += imputation.amount /\
                              (invoice.amount_total_signed / (invoice.amount_to_tax + invoice.amount_exempt))
            else:
                # Si no tiene factura solo me interesa el total imputado
                amount += imputation.amount

        return amount

    def create_retentions(self):
        """
        Crea las retenciones para el pago en base a lo que se va a pagar y la configuracion de la empresa
        """
        for payment in self:
            base = payment.get_amount_to_tax()
            for retention in self.env.user.company_id.retention_ids:
                retention = retention.retention_id
                # Hacemos el calculo para cada retencion
                functions = retention_retention.RETENTIONS_CALCULATION_FUNCTIONS
                ret_value = getattr(
                    retention, functions.get(retention.type))(
                    payment.partner_id, base, payment
                )
                # Creamos la retencion en caso que el importe calculado sea mayor que 0
                if ret_value:
                    payment._create_retention(ret_value[0], ret_value[1], retention)

    def _create_retention(self, base, amount, retention):
        """ Crea una linea de retencion en el pago """
        self.ensure_one()
        if amount > 0:
            vals = {
                'base': base,
                'amount': round(amount, 2),
                'retention_id': retention.id,
                'name': retention.name,
                'jurisdiction': retention.jurisdiction
            }

            if retention.type == 'profit':
                activity = retention.get_profit_retention_rule(self.partner_id).activity_id
                vals['activity_id'] = activity.id

            self.retention_ids = [(0, 0, vals)]

        return self.retention_ids


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    def get_accumulated_amount(self):
        """
        Busca el acumulado de los pagos, considerando los netos gravados de las facturas que se pagaron
        """
        accumulated = 0
        for payment in self:
            payment_move_lines = payment.env['account.move.line'].search([('payment_id', '=', payment.id)])
            # El account.partial.reconcile une las invoices con el pago y tiene el importe de cuanto se imputo
            for payment_move_line in payment_move_lines.filtered(lambda x: x.debit > 0):
                accumulated += payment_move_line.debit
                for credit_reconcile in payment_move_line.matched_credit_ids:
                    invoice = credit_reconcile.credit_move_id.invoice_id
                    if invoice:
                        # Sacamos la diferencia entre los impuestos y la factura,
                        # ya que solo se retiene sobre el neto gravado
                        invoice_tax = invoice.amount_total_signed / invoice.amount_to_tax \
                            if invoice.amount_to_tax else None
                        # En ese caso le restamos al importe pagado la parte de impuestos, si no, no se retiene
                        accumulated -= credit_reconcile.amount - (credit_reconcile.amount / invoice_tax) if invoice_tax\
                            else credit_reconcile.amount
                    else:
                        accumulated -= credit_reconcile.amount

        return accumulated

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
