import odoo

DB_NAME = "AUDISALUD"
ODOO_CONF = "/etc/odoo/odoo.conf"
UID = odoo.SUPERUSER_ID


odoo.tools.config.parse_config(['--config=%s' % ODOO_CONF])
with odoo.api.Environment.manage():
    registry = odoo.modules.registry.RegistryManager.get(DB_NAME)
    with registry.cursor() as cr:
        cr.execute("""INSERT INTO lending_kairos_value_line (kairos_id, date, value)
        SELECT id, date, value FROM lending_kairos_line""")
