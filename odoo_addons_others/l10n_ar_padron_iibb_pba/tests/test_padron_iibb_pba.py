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


class TestResPartner(common.TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()

    def test_update_iibb_pba_values(self):
        partner = self.env['res.partner'].create({'name': 'Test', 'vat': '123123123'})
        self.env['padron.iibb.pba'].search([]).unlink()
        self.env['padron.iibb.pba'].create({
            'aliquot': 2.00,
            'validity_date_since': '01082018',
            'validity_date_to': '31082018',
            'publication_date': '24102018',
            'taxpayer_type': 'D',
            'cuit': '123123123',
            'regime': 'R',
            'up_down_flag': 'A',
            'change_aliquot_flag': 'T',
            'group_number': 'AD',
        })
        self.env['padron.iibb.pba'].create({
            'aliquot': 4.00,
            'validity_date_since': '01082018',
            'validity_date_to': '31082018',
            'cuit': '123123123',
            'publication_date': '24102018',
            'taxpayer_type': 'D',
            'regime': 'P',
            'up_down_flag': 'A',
            'change_aliquot_flag': 'T',
            'group_number': 'AD',
        })

        self.env['wizard.padron.iibb.pba'].massive_update_iibb_pba_values()

        perception_rule = partner.perception_partner_rule_ids[0]
        retention_rule = partner.retention_partner_rule_ids[0]

        assert perception_rule.perception_id == self.env['perception.perception'].get_iibb_pba_perception()
        assert perception_rule.date_from == '2018-08-01'
        assert perception_rule.date_to == '2018-08-31'
        assert perception_rule.partner_id == partner
        assert perception_rule.percentage == 4.0

        assert retention_rule.retention_id == self.env['retention.retention'].get_iibb_pba_retention()
        assert retention_rule.date_from == '2018-08-01'
        assert retention_rule.date_to == '2018-08-31'
        assert retention_rule.partner_id == partner
        assert retention_rule.percentage == 2.0
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
