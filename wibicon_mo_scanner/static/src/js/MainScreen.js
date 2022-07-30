odoo.define("wibicon_mo_scanner.MainScreen", function (require) {
  "use strict";

  // import mqtt from 'mqtt'
  const { Component, useState } = owl;
  const Registries = require("wibicon_mo_scanner.Registries");
  const { useListener } = require("web.custom_hooks");
  const { CrashManager } = require("web.CrashManager");

  const { useRef, useDispatch, useStore } = owl.hooks;


  class MainScreen extends Component {
    // template = "WibiconIotBoxScreen";

    constructor() {
      super(...arguments);

    }


    mounted() {
      let self = this;

      $(".btn-sign-out").on("click", (e) => {
        self.props.state.isEmployee = false;
      });

      this._loadTable();
    }

    _loadTable() {
      let data = this.props.state.work_order_ids;

      $("#tbl-mo").DataTable({
        columns: [
          { data: "no" },
          { data: "mo_id" },
          { data: "workcenter_id" },
          { data: "quantity" },
          { data: "machine_id" },
          { data: "shift" },
          { data: "employee_id" },
          { data: "date_start" },
          { data: "date_finished" },
          { data: "operation_hours" },
        ],

        data: [],
      });
    }
    destroy() {
      super.destroy(...arguments);
    }
    catchError(error) {
      console.error(error);
    }
  }

  MainScreen.template = "ScannerMainScreen";

  Registries.Component.add(MainScreen);

  return MainScreen;
});
