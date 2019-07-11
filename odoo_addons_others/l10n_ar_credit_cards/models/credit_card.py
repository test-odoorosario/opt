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


class CreditCard(models.Model):

    _name = 'credit.card'

    name = fields.Char(
        'Nombre',
        required=True
    )
    account_id = fields.Many2one(
        'account.account',
        'Cuenta',
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        default=lambda self: self.env['res.company']._company_default_get('credit.card'),
    )

    _sql_constraints = [('unique_name', 'unique(name, company_id)', 'Ya existe una tarjeta con ese nombre')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
