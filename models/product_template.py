from odoo import api, models, fields
from odoo.exceptions import ValidationError
from datetime import date

class ProductTemplate(models.Model):
    _inherit = "product.template"

    sol_ref = fields.Integer(string="Correlativo Interno", required=True, default=0)
    marca_id = fields.Many2one(comodel_name='sol.marca', string="Marca", required=False)
    sol_serie = fields.Char(string="Serie")
    sol_nota = fields.Char(string="Nota")
    sol_observacion = fields.Char(string="Observacion")



    @api.onchange('marca_id')
    def onchange_marca_id(self):
        self.asigna_correlativo()

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        self.asigna_correlativo()

    def asigna_correlativo(self):
        if self.marca_id.sol_corr and self.categ_id.sol_corr:
            siguiente = self.env['product.template'].search([('marca_id', '=', self.marca_id.id),
                                                             ('categ_id', '=', self.categ_id.id)],
                                                                 order='sol_ref desc')

            sig_corr = 1
            if siguiente:
                sig_corr = siguiente[0].sol_ref + 1

            self.sol_ref = sig_corr
            self.default_code = self.categ_id.sol_corr + "-" + self.marca_id.sol_corr + "-" + str(sig_corr).rjust(4, '0')

        else:
            self.default_code = "Sin Asignar"
