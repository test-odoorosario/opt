# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tests import common
from odoo.addons.l10n_ar_afip_webservices_wsaa.tests import config
from openerp.exceptions import ValidationError


class TestWsfex(common.TransactionCase):

    def setUp(self):
        super(TestWsfex, self).setUp()
        self.wsaa = self.env['wsaa.configuration'].create({
            'type': 'homologation',
            'name': 'wsaa',
            'private_key': config.private_key,
            'certificate': config.certificate

        })
        self.wsaa_token = self.env['wsaa.token'].create({
            'name': 'wsfex',
            'wsaa_configuration_id': self.wsaa.id,
        })
        self.wsfex = self.env['wsfe.configuration'].create({
            'name': 'Test Wsfex',
            'type': 'homologation',
            'wsaa_configuration_id': self.wsaa.id,
            'wsaa_token_id': self.wsaa_token.id,
        })

    def test_unique_ticket(self):
        with self.assertRaises(ValidationError):
            self.env['wsfe.configuration'].create({
                'name': 'Test Wsfex2',
                'type': 'homologation',
                'wsaa_configuration_id': self.wsaa.id,
                'wsaa_token_id': self.wsaa_token.id,
            })

    def test_onchange_wsaa_configuration(self):
        new_wsfex = self.env['wsfe.configuration'].new(self.wsfex.read()[0])
        assert new_wsfex.wsaa_token_id
        new_wsfex.onchange_wsaa_configuration()
        assert not new_wsfex.wsaa_token_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
