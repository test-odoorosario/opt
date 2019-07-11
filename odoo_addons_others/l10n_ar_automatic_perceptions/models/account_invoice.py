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
import perception_calculator


def _format_perception_message(message):
    return """         
    <div class="alert alert-info" role="alert" style="margin-bottom: -5px;">
       <string> Error! </strong> {}
    </div>
    """.format(message)


class AccountInvoice(models.Model):  # Se encarga de cargar las percepciones en la factura automaticamente

    _inherit = 'account.invoice'

    perception_message = fields.Char('Alerta percepcion', default='')

    def get_automatic_perceptions(self):
        self.ensure_one()
        calculator = perception_calculator.PerceptionCalculator(
            self.partner_id,
            self._get_untaxed_product_amounts(),
            self.jurisdiction_id
        )
        return calculator.get_perceptions_values()

    @api.onchange('invoice_line_ids', 'jurisdiction_id')
    def onchange_invoice_line_perception(self):
        if self.type in ['out_invoice', 'out_refund']:
            message = ''
            perception_values = []

            if self.partner_id:
                try:
                    perception_values = self.get_automatic_perceptions()
                except Exception as e:
                    message = _format_perception_message(e[0])

            self.perception_message = message

            # El new nos sirve mucho porque lo cachea y nosotros no lo necesitamos en la base hasta el guardado, es un
            # comportamiento similar al de los impuestos.
            perception_proxy = self.env['account.invoice.perception']
            for perception_value in perception_values:
                perception_proxy |= perception_proxy.new(perception_value)

            self.perception_ids = perception_proxy

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.jurisdiction_id = self.partner_id.state_id
        self.onchange_invoice_line_perception()
        return super(AccountInvoice, self).onchange_partner_id()

    def _get_untaxed_product_amounts(self):
        """ Solo aplica percepcion en los casos de productos percibiles y que tengan neto gravado"""
        self.ensure_one()
        group_vat = self.env.ref('l10n_ar.tax_group_vat', False)
        lines = self.invoice_line_ids.filtered(
            lambda x:
            x.product_id.perception_taxable and
            x.mapped('invoice_line_tax_ids').filtered(lambda y: y.tax_group_id == group_vat and not y.is_exempt)
        )
        amount = sum(line.price_subtotal for line in lines)
        return round(amount, 2)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
