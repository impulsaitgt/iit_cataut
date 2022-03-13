from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def action_confirm(self):
        autorizado = True
        for linea in self.order_line:
            if not (linea.sol_autorizado and (linea.sol_precio_autorizado == linea.price_unit)):
                descuento = linea.product_id.lst_price - linea.price_unit
                if descuento > 0:
                    rango = self.env['sol.rango.autorizacion'].search([('company_id', '=', self.env.company.id),
                                                                       ('category_id', '=', linea.product_id.categ_id.id),
                                                                       ('monto_inicial_autorizado', '<=', descuento),
                                                                       ('monto_final_autorizado', '>=', descuento)],
                                                                       order='monto_inicial_autorizado')
                    if rango:
                        linea.sol_supervisores = rango.user_id
                        linea.sol_autorizado = False
                        autorizado = False

        if autorizado:
            res = super(SaleOrder, self).action_confirm()
        else:
            raise ValidationError("Existe productos no autorizados, comuniquese con los supervisores " )
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sol_autorizado = fields.Boolean(string='Autorizado', default=False)
    sol_supervisores = fields.Many2many(string="Superviso(es)", comodel_name="res.users")
    sol_autorizo = fields.Many2one(string="Usuario(s)", comodel_name="res.users")
    sol_fecha_autorizado = fields.Date(string="Fecha de autorizacion")
    sol_precio_autorizado = fields.Float(string="Precio autorizado", default=1000000)

