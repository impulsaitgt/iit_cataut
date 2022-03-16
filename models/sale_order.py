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
                        vals = {
                            'sol_supervisores': rango.user_id,
                            'sol_autorizado': False,
                            'sol_requiere_autorizacion': True,
                            'sol_precio_autorizado': linea.price_unit
                        }
                        linea_act = self.env['sale.order.line'].search([('id', '=', linea.id)])
                        linea_act.write(vals)
                        autorizado = False
                    else:
                        vals = {
                            'sol_supervisores': None,
                            'sol_autorizado': True,
                            'sol_requiere_autorizacion': False,
                            'sol_precio_autorizado': linea.price_unit
                        }
                        linea_act = self.env['sale.order.line'].search([('id', '=', linea.id)])
                        linea_act.write(vals)

        if autorizado:
            res = super(SaleOrder, self).action_confirm()
        else:
            res = self.action_muestra_autorizaciones()
        return res


    def action_muestra_autorizaciones(self):
        action = self.env.ref('iit_solares.action_autorizacion_pendiente').read()[0]
        action['domain'] = [('sol.autorizacion.pendiente.wizard.sale_id', '=', self.id)]
        return action

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sol_autorizado = fields.Boolean(string='Autorizado', default=True)
    sol_requiere_autorizacion = fields.Boolean(string='Requiere Autorizacion', default=False)
    sol_supervisores = fields.Many2many(string="Superviso(es)", comodel_name="res.users")
    sol_autorizo = fields.Many2one(string="Usuario(s)", comodel_name="res.users")
    sol_fecha_autorizado = fields.Date(string="Fecha de autorizacion")
    sol_precio_autorizado = fields.Float(string="Precio", default=1000000)

    sol_etiqueta_autorizacion = fields.Char(string="Autorizado", compute="_etiquetas_")
    sol_etiqueta_requiere_autorizacion = fields.Char(string="Requiere Autorizacion", compute="_etiquetas_")

    def _etiquetas_(self):
        for linea in self:
            if linea.sol_autorizado:
                linea.sol_etiqueta_autorizacion = "Autorizado"
            else:
                linea.sol_etiqueta_autorizacion = "No Autorizado"

            if linea.sol_requiere_autorizacion:
                linea.sol_etiqueta_requiere_autorizacion = "Requiere Autornizacion"
            else:
                linea.sol_etiqueta_requiere_autorizacion = "Autorizacion Automatica"

