odoo.define("wibicon_utility.TotalLabel", function (require) {
  "use strict";

  var ListRenderer = require("web.ListRenderer");

  ListRenderer.include({
    _renderFooter: function () {
      let $footer = this._super.apply(this, arguments);
      let col_agg = undefined;

      for (const col in this.columns) {
        if ("aggregate" in this.columns[col]) {
          col_agg = col;
          break;
        }
      }

      if (col_agg) {
        $footer.find(`td:eq(${col_agg - 1})`).html("Total");
      }
      return $footer;
    },
  });
});
