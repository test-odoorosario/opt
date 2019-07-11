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

from openerp import models, fields


class LendingInvoice(models.Model):
    _inherit = 'lending.invoice'

    difference = fields.Float(
        compute="get_difference"
    )

    difference_msg = fields.Html(
        compute="get_difference"
    )

    def get_difference(self):
        for r in self:
            r.difference = abs((r.amount_untaxed + r.amount_taxed) - r.amount_total_lots)
            r.difference_msg = "<b>Atención:</b> Existe una diferencia de $ {} entre el total de la factura y el de " \
                               "los lotes".format('{:,.2f}'.format(r.difference)) if r.difference else ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
