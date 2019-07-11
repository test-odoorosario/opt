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


class ResCurrency(models.Model):

    _inherit = 'res.currency'

    editable_inverse_rate = fields.Boolean(
        'Tasa inversa editable',
        help="Si se marca, se podra cargar la tasa de cambio de forma inversa"
    )
    rate = fields.Float(digits=(12, 10), compute='_compute_current_rate')

    @api.multi
    @api.depends('rate_ids.rate')
    def _compute_current_rate(self):
        date = self._context.get('date') or fields.Datetime.now()
        for currency in self:
            currency_rate = self.env['res.currency.rate'].search([
                ('name', '<=', date),
                ('company_id', '=', self.env.user.company_id.id),
                ('currency_id', '=', currency.id)
            ], limit=1, order='name desc')
            currency.rate = currency_rate.rate or 1.0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
