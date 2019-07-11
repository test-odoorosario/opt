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

from openerp import models, fields, api


class BankCardCoupon(models.Model):
    _inherit = 'bank.card.coupon'

    estimated_amount = fields.Float(
        string='Monto estimado de acreditacion',
        readonly=True,
    )
    estimated_date = fields.Date(
        string='Fecha estimada de acreditacion',
        readonly=True,
    )
    date_closed = fields.Date(
        string='Fecha de cierre',
        readonly=True,
    )

    @api.multi
    def _close_coupon(self):
        view = self.env.ref('opyme_coupon_projection.close_coupon_wizard_form_view')
        return {
            'name': 'Cerrar cupones',
            'res_model': 'close.coupon.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'search_view_id': view.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
