#!/usr/bin/env bash
GITKEY=$1
sudo pip install --upgrade l10n_ar_api
sudo pip install --upgrade git+https://blueorangegroup:${GITKEY}@bitbucket.org/blueorangegroup/blueorange.git
sudo pip install --upgrade generic-erp
sudo git -C /opt/odoo_addons_l10n_ar/ reset --hard
sudo git -C /opt/odoo_addons_l10n_ar/ pull https://blueorangegroup:${GITKEY}@bitbucket.org/blueorangegroup/odoo_l10n_ar.git
sudo git -C /opt/odoo_addons_others/ reset --hard
sudo git -C /opt/odoo_addons_others/ pull https://blueorangegroup:${GITKEY}@bitbucket.org/blueorangegroup/odoo_addons_others.git
sudo git -C /opt/odoo_addons_extra/ reset --hard
sudo git -C /opt/odoo_addons_extra/ pull https://blueorangegroup:${GITKEY}@bitbucket.org/blueorangegroup/odoo_addons_extra.git
sudo git -C /opt/odoo_addons_customization/ reset --hard
sudo git -C /opt/odoo_addons_customization/ pull https://blueorangegroup:${GITKEY}@bitbucket.org/blueorangegroup/odoo_customization_audisalud.git
sudo /etc/init.d/odoo restart
sudo /opt/odoo/./odoo-bin -c /etc/odoo/odoo.conf --no-xmlrpc -u base_vat_ar,bo_customization,others -d AUDISALUD --stop-after-init
sudo /opt/odoo/./odoo-bin -c /etc/odoo/odoo.conf --no-xmlrpc -u base_vat_ar,bo_customization,others -d TEST --stop-after-init