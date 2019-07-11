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

    'name': 'Lending',

    'version': '1.0',

    'category': '',

    'summary': 'Lending',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar/',

    'depends': [

        'mail',
        'bo_customization',
        'web_readonly_bypass',

    ],

    'data': [

        'security/groups.xml',
        'views/menu.xml',
        'views/lending_view.xml',
        'views/lending_lender_view.xml',
        'views/lending_lot_view.xml',
        'views/lending_rate_view.xml',
        'views/lending_rate_line_view.xml',
        'views/lending_lot_type_view.xml',
        'views/lending_invoice_view.xml',
        'views/lending_plan_agreement_view.xml',
        'views/lending_registry_lending_view.xml',
        'views/lending_affiliate_view.xml',
        'views/lending_customer_view.xml',
        'views/lending_nomenclator_view.xml',
        'views/lending_expense_type_view.xml',
        'views/lending_debit_motive_view.xml',
        'views/lending_category_view.xml',
        'views/lending_coinsurance_view.xml',
        'data/lending_debit_motive_data.xml',
        'security/ir.model.access.csv',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Lending
======================================
* Modulo de prestaciones
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
