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


class PurchaseCreditCardFee(models.Model):

    _name = 'purchase.credit.card.fee'
    _order = 'due_date asc'

    name = fields.Char(
        'Descripción'
    )
    credit_card_line_id = fields.Many2one(
        'purchase.credit.card.line',
        'Linea de pago con tarjeta'
    )
    partner_id = fields.Many2one(
        related='credit_card_line_id.partner_id'
    )
    credit_card_id = fields.Many2one(
        related='credit_card_line_id.credit_card_id',
        store=True
    )
    payment_id = fields.Many2one(
        related='credit_card_line_id.payment_id'
    )
    currency_id = fields.Many2one(
        related='credit_card_line_id.currency_id'
    )
    total_fees = fields.Integer(
        'Total de cuotas'
    )
    fee = fields.Integer(
        'Cuota'
    )
    amount = fields.Monetary(
        'Importe'
    )
    due_date = fields.Date(
        'Fecha de vencimiento'
    )
    fees_text = fields.Char(
        'Cuota',
        compute='_compute_fees_text'
    )
    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        default=lambda self: self.env['res.company']._company_default_get('purchase.credit.card.fee'),
    )

    def _compute_fees_text(self):
        for fee in self:
            fee.fees_text = '{} / {}'.format(fee.fee, fee.total_fees)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
