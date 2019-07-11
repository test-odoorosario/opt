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
from datetime import datetime
from openerp import models, fields

from ...rate_getters import rate_getter_yahoo


class CurrencyRateWizard(models.TransientModel):
    _name = 'currency.rate.wizard'

    def instantiate_rate_getter(self):
        """
        Instancia la clase correspondiente a la obtencion de tasas segun el servicio elegido
        :return: una instancia nueva de la clase
        """
        return {
            'yahoo': rate_getter_yahoo.RateGetterYahoo(),
        }.get(self.service)

    def get_rate(self):
        rate_getter = self.instantiate_rate_getter()
        print self.local_currency.name, self.currency.name
        rate = rate_getter.get_rate(self.local_currency.name, self.currency.name)
        print rate
        inverse_rate = rate_getter.get_rate(self.currency.name, self.local_currency.name)
        self.env['res.currency.rate'].create({
            'name': datetime.now(),
            'currency_id': self.currency.id,
            'rate': rate,
            'inverse_rate': inverse_rate
        })

    def _get_local_currency(self):
        return self.env.user.company_id.currency_id.id

    local_currency = fields.Many2one(
        string="Moneda local",
        comodel_name="res.currency",
        default=_get_local_currency,
        required=True,
    )

    currency = fields.Many2one(
        string="Moneda a consultar",
        comodel_name="res.currency",
        required=True,
    )

    service = fields.Selection(
        string="Servicio",
        selection=[('yahoo', 'Yahoo')],
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
