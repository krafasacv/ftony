odoo.define('pos_product_min_price.models', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	//models.load_fields('product.product', ['product_min_price']);
	models.load_fields('product.pricelist.item', ['product_min_price']);
});