from odoo import models,fields,api


class AutorizacionPendiente(models.TransientModel):
    _name = 'caa.autorizacion.pendiente.wizard'
    _description = 'Muestra autorizaciones pendientes'

    estado = fields.Char(string="Estatus", default='Autorizaciones Pendientes')
    sale_id = fields.Many2one(string="Pedido de Venta", comodel_name="sale.order", readonly=True)
    detalle_autorizaciones = fields.Html(string="Detalle de Autorizaciones", readonly=True)


    @api.onchange('estado')
    def onchanche_estado(self):
        self.sale_id = self.env['sale.order'].search([('id', '=', self.env.context['active_id'])])

        detalles = "<table class='table table-bordered'>"
        detalles += "<tr><th>Producto</th><th>Supervisores</th></tr>"
        for linea in self.sale_id.order_line:
            if linea.caa_requiere_autorizacion:
                supervisores = ', '.join(linea.caa_supervisores.mapped('name'))
                detalles += f"<tr><td>{linea.product_id.name}</td><td>{supervisores}</td></tr>"
        detalles += "</table>"
        self.detalle_autorizaciones = detalles

