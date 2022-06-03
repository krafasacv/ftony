odoo.define('pos_product_min_price.PrintBillButton', function(require) {
    'use strict';

    const PrintBillButton = require('pos_restaurant.PrintBillButton');
    const Registries = require('point_of_sale.Registries');
	
    const MinPricePrintBillButton = PrintBillButton =>
        class extends PrintBillButton {
            async onClick() {
				const order = this.env.pos.get_order();
	            if (order.get_orderlines().length > 0) {
					var pricelist = this.env.pos.default_pricelist;
					var pricelist_items = pricelist.items;
					var product_min_price = 0.0
					var order_line = _.find(order.get_orderlines(), function (line) {
						var price_exist = pricelist_items.filter(function(item) {return item['product_tmpl_id'][0] ==line.product.product_tmpl_id});
						if (price_exist.length > 0 && price_exist[0].product_min_price>0 && line.get_unit_price() < price_exist[0].product_min_price){
							product_min_price = price_exist[0].product_min_price;
							return true;
						}
					})
					
					if (order_line != undefined){
						await this.showPopup('ErrorPopup', {
				                    title: this.env._t('El precio del producto es menor que el permitido'),
				                    body: this.env._t('El precio del producto '+order_line.get_full_product_name()+' es menor del precio minimo '+product_min_price),
				                });	
					}
					else{
						await super.onClick();
					}
	                
	            } else {
	                await super.onClick();
	            }
				
	        }
        };

    Registries.Component.extend(PrintBillButton, MinPricePrintBillButton);

    return PrintBillButton;
});
