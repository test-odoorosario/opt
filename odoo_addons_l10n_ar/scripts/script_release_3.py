import odoo

DB_NAME = 'DB_NAME'
ODOO_CONF = '/etc/odoo/odoo.conf'
UID = odoo.SUPERUSER_ID

odoo.tools.config.parse_config(['--config=%s' % ODOO_CONF])
with odoo.api.Environment.manage():
    registry = odoo.modules.registry.RegistryManager.get(DB_NAME)
    with registry.cursor() as cr:
        ctx = odoo.api.Environment(cr, UID, {})['res.users'].context_get()
        env = odoo.api.Environment(cr, UID, ctx)
        payment_proxy = env['account.payment']

        for imputation in payment_proxy.search([]).mapped('payment_imputation_ids'):
            imputation.move_line_id = imputation.invoice_id.move_id.line_ids.filtered(
                lambda x: x.account_id == imputation.invoice_id.account_id
            )[0] if imputation.invoice_id.move_id else None
