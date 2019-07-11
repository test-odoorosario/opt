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

from openerp import models


class AccountOwnCheckLine(models.Model):

    _inherit = 'account.own.check.line'

    def print_issued_check(self):
        """ Imprime el cheque propio si no está en borrador """
        self.ensure_one()
        if self.own_check_id:
            return self.env['report'].get_action(
                self.own_check_id,
                'opyme_print_issued_check.report_print_issued_check'
            )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
