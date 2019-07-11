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

import locale
from yahoo_finance import Currency


class RateGetterYahoo():

    def get_rate(self, source_code, dest_code):
        previous_locale = locale.getlocale()
        locale.setlocale(locale.LC_ALL, 'C')
        currency = Currency(source_code + dest_code)
        locale.setlocale(locale.LC_ALL, previous_locale)
        return currency.get_rate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
