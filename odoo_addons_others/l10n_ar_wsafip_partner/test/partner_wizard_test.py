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

from mock import mock
from openerp import SUPERUSER_ID
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError
import config


class PartnerWizardTest(TransactionCase):

    exp_time = None
    global_token = None
    global_sign = None

    def setUp(self):
        super(PartnerWizardTest, self).setUp()
        self.wsaa = self.env['wsaa.configuration'].create({
            'type': 'homologation',
            'name': 'wsaa',
            'private_key': config.private_key,
            'certificate': config.certificate,
        })

        if not PartnerWizardTest.exp_time:
            self.token = self.env['wsaa.token'].create({
                'name': 'ws_sr_padron_a5',
                'wsaa_configuration_id': self.wsaa.id,
            })
            self.token.action_renew()
            PartnerWizardTest.exp_time = self.token.expiration_time
            PartnerWizardTest.global_token = self.token.token
            PartnerWizardTest.global_sign = self.token.sign

        else:
            self.token = self.env['wsaa.token'].create({
                    'name': 'ws_sr_padron_a5',
                    'wsaa_configuration_id': self.wsaa.id,
                    'expiration_time': PartnerWizardTest.exp_time,
                    'token': PartnerWizardTest.global_token,
                    'sign': PartnerWizardTest.global_sign
                })

        self.user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
        self.user.partner_id.tz = 'America/Argentina/Buenos_Aires'
        self.ws_padron = self.env['wssrpadrona4.configuration'].create({
            'name': 'Test Wssrpadrona5',
            'type': 'homologation',
            'wsaa_configuration_id': self.wsaa.id,
            'wsaa_token_id': self.token.id,
        })
        self.wizard = self.env['partner.data.get.wizard'].create({
            'vat': 11221233211,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'TEST PARTNER',
            'country_id': self.env.ref('base.ar').id,
            'vat': 20357563276
        })

    def test_get_data_without_configuration(self):
        self.ws_padron.unlink()
        with self.assertRaises(ValidationError):
            self.wizard.get_data()

    def test_get_data(self):
        self.wizard.vat = 30709653543
        data = self.wizard.get_data()

        assert data.persona
        assert data.persona.domicilio

    def test_cannot_get_valid_data(self):
        """ Testeamos que se devuelve un error cuando el cuit es inexistente """
        self.wizard.vat = 20221122

        with self.assertRaises(Exception):
            self.wizard.get_data()

    def test_cannot_get_valid_data_vat_alphanumeric(self):
        """ Testeamos que se devuelve un error cuando cuit alfanumerico """
        self.wizard.vat = '20312-123'

        with self.assertRaises(Exception):
            self.wizard.get_data()

    def test_load_vals(self):

        self.wizard.vat = 30709653543
        # Creamos mocks para simular el comportamiento de AFIP
        data = mock.Mock()
        persona = mock.Mock()
        domicilio = [mock.Mock()]

        persona.vat = '30709653543'
        persona.razonSocial = 'Test'
        data.persona = persona

        domicilio[0].localidad = 'loc'
        domicilio[0].codPostal = '1666'
        domicilio[0].direccion = 'Street'
        domicilio[0].idProvincia = 1
        persona.domicilio = domicilio

        vals = self.wizard.load_vals(data)
        assert vals == {
            'name': data.persona.razonSocial,
            'partner_document_type_id': self.env.ref('l10n_ar_afip_tables.partner_document_type_80').id,
            'vat': data.persona.vat,
            'country_id': self.env.ref('base.ar').id,
            'state_id': self.env.ref('base.state_ar_b').id,
            'zip': data.persona.domicilio[0].codPostal,
            'city': data.persona.domicilio[0].localidad,
            'street': data.persona.domicilio[0].direccion,
        }

    def test_create_partner(self):
        """ Testeamos que se crea el partner que posee ese cuit """
        self.wizard.vat = 30709653543
        self.wizard.get_and_write_data()
        partner = self.env['res.partner'].search([('vat', '=', '30709653543')])

        assert partner.street
        assert partner.country_id == self.env.ref('base.ar')
        assert partner.vat == '30709653543'
        assert partner.partner_document_type_id == self.env.ref('l10n_ar_afip_tables.partner_document_type_80')
        assert partner.city
        assert partner.zip
        assert partner.street
        assert partner.state_id

    def test_obtain_afip_data_and_overwrite(self):
        """ Obtener datos de AFIP va a sobreescribir un partner existente """
        self.partner.vat = 30709653543

        self.wizard.vat = 30709653543
        self.wizard.write_partner = True
        self.wizard.get_and_write_data()

        assert self.partner.street
        assert self.partner.country_id == self.env.ref('base.ar')
        assert self.partner.vat == '30709653543'
        assert self.partner.partner_document_type_id == self.env.ref('l10n_ar_afip_tables.partner_document_type_80')
        assert self.partner.city
        assert self.partner.zip
        assert self.partner.street
        assert self.partner.state_id

    def test_obtain_afip_data_with_partner_will_overwrite(self):
        "Obtener datos de AFIP va a sobreescribir el partner seleccionado"
        assert self.partner.name == "TEST PARTNER"

        self.wizard.vat = 20359891033
        self.wizard.write_partner = True
        self.wizard.partner_id = self.partner
        self.wizard.get_and_write_data()

        assert self.partner.name == "BIANCHINI JUAN GABRIEL"
        assert self.partner.vat == "20359891033"

    def test_cannot_overwrite_partner(self):
        "No se puede sobreescribir un partner sin tildar 'sobreescribir'"
        self.wizard.vat = 20357563276

        with self.assertRaises(Exception):
            self.wizard.get_and_write_data()

    def test_onchange_partner(self):
        "Testeamos que funciona el onchange"
        assert self.wizard.vat == '11221233211'

        self.wizard.partner_id = self.partner
        self.wizard.onchange_partner()

        assert self.wizard.vat == '20357563276'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

