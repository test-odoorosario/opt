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

    'name': 'l10n_ar_hr_expense',

    'version': '1.0',

    'category': '',

    'summary': '',

    'author': 'BLUEORANGE GROUP S.R.L',

    'website': 'blueorange.com.ar',

    'depends': [

        'hr_expense',
        'l10n_ar_account_payment',

    ],

    'data': [

        'wizard/hr_expense_register_payment.xml',

    ],

    'installable': True,

    'auto_install': True,

    'application': False,

    'description': """
l10n_ar_hr_expense
======================================
* Se modifica posteo de pagos en gastos
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
