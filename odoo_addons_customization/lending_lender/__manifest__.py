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

    'name': 'Lending lender',

    'version': '1.0',

    'category': '',

    'summary': '',

    'author': 'BLUEORANGE GROUP S.R.L',

    'website': 'blueorange.com.ar',

    'depends': [

        'bo_customization',
        'bo_lending_lot_import',
        'lending_medical_audit',

    ],

    'data': [

        'security/groups.xml',
        'views/menu.xml',
        'views/lending_invoice_view.xml',
        'views/res_users_view.xml',
        'security/ir.model.access.csv',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """

Configuracion y nuevo menu para usabilidad de prestadores
""",

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
