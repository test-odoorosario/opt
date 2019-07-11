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

    'name': 'l10n_ar_retentions_sicore',

    'version': '1.0',

    'category': '',

    'summary': 'l10n_ar_retentions_sicore',

    'author': 'BLUEORANGE GROUP S.R.L',

    'website': 'blueorange.com.ar',

    'depends': [

        'l10n_ar_retentions',

    ],

    'data': [

        'views/retention_sicore_view.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Generacion de archivo para la presentacion de retenciones en aplicativo SICORE
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
