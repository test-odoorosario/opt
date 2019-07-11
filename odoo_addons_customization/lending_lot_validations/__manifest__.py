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

{

    'name': 'Lending lot validations',

    'version': '1.0',

    'category': '',

    'summary': 'Lending lot validations',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar/',

    'depends': [

        'lending_import_kairos',

    ],

    'data': [

        'views/lending_lot_view.xml',
        'views/lending_rate_view.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Lending lot validations
======================================
* . Validaciones de las prestaciones de cada lote
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
