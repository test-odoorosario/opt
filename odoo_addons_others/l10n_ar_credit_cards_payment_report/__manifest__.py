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

    'name': 'L10n ar credit cards payment report',

    'version': '1.0',

    'category': '',

    'summary': 'L10n ar credit cards payment report',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'blueorange.com.ar',

    'depends': [

        'l10n_ar_purchase_credit_cards',
        'l10n_ar_account_payment_report',

    ],

    'data': [

        'report/account_payment_report.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
L10n ar credit cards payment report
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
