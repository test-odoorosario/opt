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

    'name': 'Account payment report with credits',

    'version': '1.0',

    'category': '',

    'summary': '',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'blueorange.com.ar',

    'depends': [

        'others',
        'l10n_ar_account_payment_report',

    ],

    'data': [

        'views/account_payment_view.xml',
        'report/report_account_payment.xml',
        'security/ir.model.access.csv'

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Account payment report with credits
======================================
* Reporte de pagos con imputaciones de creditos y debitos
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
