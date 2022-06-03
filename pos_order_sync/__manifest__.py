# -*- coding: utf-8 -*-

{
  "name"                 :  "POS Order Sync",
  "summary"              :  """Module POS Order Sync""",
  "category"             :  "Point of Sale",
  "version"              :  "1.1",
  "author"               :  "IT Admin.",
  "license"              :  "Other proprietary",
  "website"              :  "www.itadmin.com.mx",
  "description"          :  """Odoo POS Order Sync
Synchronize POS sessions
Syc session
Send POS quotations
Share POS session
Synchronize multiple POS session""",
  "depends"              :  ['point_of_sale', 'pos_product_min_price'],
  "data"                 :  [
                             'reports/order_sync_paperformate.xml',
                             'views/pos_order_sync_view.xml',
                             'views/template.xml',
                             'views/order_quote_sequence.xml',
                             'views/pos_config_view.xml',
                             #'views/product_pricelist.xml',
                             'reports/report_file.xml',
                             'reports/quote_report.xml',
                             'security/ir.model.access.csv',
                            ],
  "qweb"                 :  ['static/src/xml/pos_order_sync.xml'],
  "images"               :  [],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}