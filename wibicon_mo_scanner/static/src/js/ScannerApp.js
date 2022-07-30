odoo.define("wibicon_mo_scanner.ScannerApp", function (require) {
  "use strict";

  // import mqtt from 'mqtt'
  const { Component, useState } = owl;
  const { whenReady } = owl.utils;
  const HeaderScreen = require("wibicon_mo_scanner.HeaderScreen");
  const EmployeeScannerScreen = require("wibicon_mo_scanner.EmployeeScannerScreen");
  const OrderScannerScreen = require("wibicon_mo_scanner.OrderScannerScreen");
  const WorkOrderScreen = require("wibicon_mo_scanner.WorkOrderScreen");
  const MainScreen = require("wibicon_mo_scanner.MainScreen");
  const Registries = require("wibicon_mo_scanner.Registries");
  const { useListener } = require("web.custom_hooks");
  const { CrashManager } = require("web.CrashManager");

  const { useRef, useDispatch, useStore } = owl.hooks;

  class ScannerApp extends Component {
    template = "ScannerHomePage";
    static components = {
      HeaderScreen,
      EmployeeScannerScreen,
      OrderScannerScreen,
      WorkOrderScreen,
      MainScreen,
    };

    constructor() {
      super(...arguments);
      this.state = useState({
        head: null,
        value: 0,
        progress_of_done: 0,
        isEmployee: false,
        isMo: false,
        barcode: null,
        showButton: false,
        isFinished: false,
        active_model: null,
        html_color: null,
        handling_id: {
          id: null,
          name: null,
        },
        process_type: {
          id: null,
          name: null,
        },
        design_id: {
          id: null,
          name: null,
        },
        opc_scouring_id: {
          id: null,
          name: null,
        },
        std_potong:null,
        note:null,
        prepareVals: {
          workcenter_id: { id: null, name: null },
          machine_id: { id: null, name: null },
          shift: null,
          note: null,
          finalset: { id: null, name: null },
        },
        workcenter_ids: [],
        machine_ids: [],
        finalset_ids: [],
        shift: ["A", "B", "C"],
        mrp: {
          id: null,
          name: null,
          state: null,
          product_id: null,
          product_qty: null,
          state: null,
          type_id: null,
          sale_id: null,
          partner_id: null,
          components_availability_state: null,
          workcenter_on_progress: null,
          workorder_ids: [],
        },
        employee: {
          id: null,
          name: null,
          shift: null,
        },
      });
    }

    async willStart() {
      // loadCSS("/wibicon_mo_scanner/static/src/scss/main.scss");
    }

    mounted() {
      let self = this;
    }
    catchError(error) {
      console.error(error);
    }
  }

  ScannerApp.template = "ScannerHomePage";

  Registries.Component.add(ScannerApp);

  return ScannerApp;
});
