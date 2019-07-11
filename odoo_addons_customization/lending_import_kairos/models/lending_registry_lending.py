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

from openerp import models, api


class LendingRegistryLending(models.Model):
    _inherit = 'lending.registry.lending'

    @api.onchange('medicine_id')
    def onchange_medicine_id(self):
        self.code = self.medicine_id.code
        med = self.medicine_id
        self.description = "{} - {}".format(med.description_drug, med.description_presentation) if med else ''

    @api.onchange('lending_id')
    def onchange_lending_id(self):
        """ Al momento de cargar la prestacion se carga la descripcion y se rellena el campo texto de codigo"""
        if self.lending_id:
            self.description = "{}".format(self.lending_id.name)
            rate = self.search_rate()
            if rate:
                rate_line = self.search_rate_line(rate)
                self.code = "{}".format(rate_line.lender_code if rate_line.lender_code else self.lending_id.code)

    def search_rate(self):
        """ Se busca el tarifario activo por fecha y prestador"""
        rate = self.env['lending.rate'].search([
            ('date', '<=', self.date),
            ('end_date', '=', False),
            ('lender_id', '=', self.lot_id.lender_id.id)
        ], limit=1, order='date desc')
        return rate if rate else False

    def search_rate_line(self, rate):
        """ Busco la linea del tarifario que tiene el codigo de la prestacion"""
        if rate:
            rate_line = rate.mapped('line_ids').filtered(
                lambda x: x.lender_code == self.lending_id.code and not x.code_range and not x.no_agreed) or \
                        rate.mapped('line_ids').filtered(
                lambda x: x.lending_id.code == self.lending_id.code and not x.code_range and not x.no_agreed) or \
                        rate.mapped('line_ids').filtered(
                            lambda x: x.lending_id.code <= self.lending_id.code <= x.code_range and not x.no_agreed)
            return rate_line if len(rate_line) == 1 else False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
