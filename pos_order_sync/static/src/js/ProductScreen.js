odoo.define('pos_order_sync.ProductScreen', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
	
    const MinPriceProductScreen = ProductScreen =>
        class extends ProductScreen {
            _onClickPay() {
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
						this.showPopup('ErrorPopup', {
				                    title: this.env._t('Product Price below minimum price'),
				                    body: this.env._t('Product '+order_line.get_full_product_name()+' have minimum selling price is '+product_min_price),
				                });	
					}
					else{
						super._onClickPay();
					}
	                
	            } else {
	                super._onClickPay();
	            }
				
	        }
        };

    Registries.Component.extend(ProductScreen, MinPriceProductScreen);

    return ProductScreen;
});
