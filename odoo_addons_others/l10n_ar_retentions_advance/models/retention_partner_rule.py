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


class RetentionPartnerRule(models.Model):
    _name = 'retention.partner.rule'
    _description = 'Reglas de retenciones de terceros'

    @api.constrains('percentage', 'retention_id')
    def _check_percentage(self):
        if self.percentage and self.retention_id.type == 'profit':
            raise Warning("Para {} el porcentaje debe ser 0".format(self.retention_id.name))
        if self.percentage < 0 or self.percentage > 100:
            raise Warning("El porcentaje debe estar entre 0 y 100")

    @api.constrains('partner_id', 'retention_id', 'activity_id')
    def _check_repeat(self):
        rules = self.search([('partner_id', '=', self.partner_id.id), ('retention_id', '=', self.retention_id.id),
                             ('activity_id', '=', self.activity_id.id), ('id', '!=', self.id)])
        if rules:
            raise Warning("Existe mas de una regla con retencion {} y actividad {}.".format(self.retention_id.name,
                                                                                            self.activity_id.name if self.activity_id else "vacia"))

    activity_id = fields.Many2one(
        comodel_name='retention.activity',
        string="Actividad",
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        ondelete="cascade",
    )

    retention_id = fields.Many2one(
        comodel_name='retention.retention',
        string='Retencion',
        required=True,
        domain="[('type_tax_use','=','purchase')]",
    )

    percentage = fields.Float(
        string='Porcentaje',
        required=True,
    )

    type = fields.Selection(
        selection=[
            ('vat', 'IVA'),
            ('gross_income', 'Ingresos Brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro'),
        ],
        string="Tipo",
        related='retention_id.type',
        readonly=True,
    )

    state_id = fields.Many2one(
        'res.country.state',
        string="Provincia",
        related='retention_id.state_id',
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('retention.partner.rule'),
    )

    date_from = fields.Date(
        'Fecha desde'
    )

    date_to = fields.Date(
        'Fecha hasta'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
