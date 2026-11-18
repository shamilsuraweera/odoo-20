import os

from odoo import api, fields, models
from odoo.modules import get_module_path

# Modules living in a directory with one of these names count as custom.
CUSTOM_ADDONS_DIRS = ('custom_addons',)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    module_source = fields.Selection(
        [('official', 'Odoo Modules'), ('custom', 'Custom Modules')],
        string='Source', compute='_compute_module_source', store=True)

    @api.depends('name')
    def _compute_module_source(self):
        for module in self:
            path = get_module_path(module.name, display_warning=False)
            parent = os.path.basename(os.path.dirname(path)) if path else ''
            module.module_source = 'custom' if parent in CUSTOM_ADDONS_DIRS else 'official'
