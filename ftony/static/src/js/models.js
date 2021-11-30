odoo.define('ftony.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    models.load_fields("product.product", ["standard_price"]);
    models.load_fields("res.company", ['regimen_fiscal','street_name','city']);
    console.log(Object.values(company));
    
    var core = require('web.core');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var _t = core._t;
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

});
