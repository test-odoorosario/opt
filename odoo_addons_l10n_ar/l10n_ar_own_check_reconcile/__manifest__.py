# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

    'name': 'Own Check Reconcile',

    'version': '1.0',

    'category': '',

    'summary': 'Own Check Reconcile',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'blueorange.com.ar',

    'depends': [

        'l10n_ar_account_check',

    ],

    'data': [

        'views/own_check_reconcile.xml',
        'views/account_own_check.xml',
        'security/ir.model.access.csv',
        'data/security.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Own Check Reconcile',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
