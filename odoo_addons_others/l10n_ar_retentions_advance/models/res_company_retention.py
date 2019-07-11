# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class ResCompanyRetention(models.Model):
    _name = 'res.company.retention'
    _description = 'Retencion de empresa'

    @api.constrains('company_id', 'retention_id')
    def _check_repeat(self):
        rules = self.search([('company_id', '=', self.company_id.id), ('retention_id', '=', self.retention_id.id),
                             ('id', '!=', self.id)])
        if rules:
            raise Warning("Existe mas de una regla con retencion {}.".format(
                self.retention_id.name if self.retention_id else "vacia"))

    retention_id = fields.Many2one(
        comodel_name='retention.retention',
        string='Retencion',
        domain="[('type_tax_use','=','purchase')]",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('res.company.retention'),
    )

    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string="Provincia",
        related='retention_id.state_id',
        readonly=True,
    )

    type = fields.Selection(
        selection=[
            ('vat', 'IVA'),
            ('gross_income', 'Ingresos Brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro')
        ],
        string="Tipo",
        related='retention_id.type',
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
