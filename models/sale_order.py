from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def action_confirm(self):
        autorizado = True
        mensaje = ''
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
                        mensaje = mensaje + 'Producto = ' + linea.product_id.name + ' (supervisores'
                        for usuario in rango.user_id:
                            mensaje = mensaje + ' - ' + usuario.name
                        mensaje = mensaje + ')\n'
                        linea.sol_supervisores = rango.user_id
                        linea.sol_autorizado = False
                        linea.sol_requiere_autorizacion = True
                        autorizado = False
                    else:
                        linea.sol_requiere_autorizacion = False
                        linea.sol_autorizado = True

        if autorizado:
            res = super(SaleOrder, self).action_confirm()
        else:
            raise ValidationError("Existen productos no autorizados, comuniquese con los supervisores, \n" + mensaje)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sol_autorizado = fields.Boolean(string='Autorizado', default=True)
    sol_requiere_autorizacion = fields.Boolean(string='Requiere Autorizacion', default=False)
    sol_supervisores = fields.Many2many(string="Superviso(es)", comodel_name="res.users")
    sol_autorizo = fields.Many2one(string="Usuario(s)", comodel_name="res.users")
    sol_fecha_autorizado = fields.Date(string="Fecha de autorizacion")
    sol_precio_autorizado = fields.Float(string="Precio autorizado", default=1000000)

