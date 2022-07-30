odoo.define("wibicon_mo_scanner.WorkOrderScreen", function (require) {
  "use strict";

  const { Component, useState } = owl;
  const Registries = require("wibicon_mo_scanner.Registries");
  const { useListener } = require("web.custom_hooks");
  const { CrashManager } = require("web.CrashManager");
  const Autocomplete = require("wibicon_mo_scanner.Autocomplete");
  const framework = require("web.framework");

  // const Stepper = require('bs-stepper');

  const { useRef, useDispatch, useStore } = owl.hooks;
  const { loadCSS } = require("web.ajax");

  class WorkOrderScreen extends Component {
    constructor() {
      super(...arguments);
    }

    static components = {
      Autocomplete,
    };

    async willStart() {
      loadCSS("/wibicon_mo_scanner/static/src/scss/work_order.scss");
    }

    _btnBack() {
      Object.assign(this.props.state, {
        isEmployee: false,
        isMo: false,
        mrp: {},
        employee: {},
      });
    }

    _reset() {
      Object.assign(this.props.state, {
        prepareVals: {
          workcenter_id: {
            id: null,
            name: null,
          },
          machine_id: {
            id: null,
            name: null,
          },
          shift: null,
          note: null,
          finalset: {
            id: null,
            name: null,
          },
        },
      });
    }

    onOptionChosenFinalSet(ev) {
      Object.assign(this.props.state, {
        prepareVals: {
          workcenter_id: {
            id: this.props.state.prepareVals.workcenter_id.id,
            name: this.props.state.prepareVals.workcenter_id.name,
          },
          machine_id: {
            id: this.props.state.prepareVals.machine_id.id,
            name: this.props.state.prepareVals.machine_id.name,
          },
          shift: this.props.state.prepareVals.shift,
          note: this.props.state.prepareVals.note,
          finalset: {
            id: ev.detail.prepareVals?.id,
            name: ev.detail.prepareVals?.text,
          },
        },
      });
    }

    onOptionChosenWorkCenter(ev) {
      Object.assign(this.props.state, {
        prepareVals: {
          workcenter_id: {
            id: ev.detail.prepareVals?.id,
            name: ev.detail.prepareVals?.text,
          },
          machine_id: {
            id: this.props.state.prepareVals.machine_id.id,
            name: this.props.state.prepareVals.machine_id.name,
          },
          shift: this.props.state.prepareVals.shift,
          note: this.props.state.prepareVals.note,
          finalset: {
            id: this.props.state.prepareVals.finalset.id,
            name: this.props.state.prepareVals.finalset.name,
          },
        },
      });
    }

    onOptionChosenShift(ev) {
      Object.assign(this.props.state, {
        prepareVals: {
          workcenter_id: {
            id: this.props.state.prepareVals.workcenter_id.id,
            name: this.props.state.prepareVals.workcenter_id.name,
          },
          machine_id: {
            id: this.props.state.prepareVals.machine_id.id,
            name: this.props.state.prepareVals.machine_id.name,
          },
          shift: ev.detail.prepareVals,
          note: this.props.state.prepareVals.note,
          finalset: {
            id: this.props.state.prepareVals.finalset.id,
            name: this.props.state.prepareVals.finalset.name,
          },
        },
      });
    }

    onOptionChosenMachine(ev) {
      Object.assign(this.props.state, {
        prepareVals: {
          workcenter_id: {
            id: this.props.state.prepareVals.workcenter_id.id,
            name: this.props.state.prepareVals.workcenter_id.name,
          },
          machine_id: {
            id: ev.detail.prepareVals?.id,
            name: ev.detail.prepareVals?.text,
          },
          shift: this.props.state.prepareVals.shift,
          note: this.props.state.prepareVals.note,
          finalset: {
            id: this.props.state.prepareVals.finalset.id,
            name: this.props.state.prepareVals.finalset.name,
          },
        },
      });
    }

    async startWo(ev) {
      ev.preventDefault();
      framework.blockUI();
      let self = this;
      let final_set_id = this.props.state.prepareVals.finalset.id
      let workname  = this.props.state.prepareVals.workcenter_id.name;
      let machine   = this.props.state.prepareVals.machine_id.name;
      let shift     = this.props.state.prepareVals.shift;
      let workcenter = await self.env.services.rpc({
        route: "/api/mrp/workcenter",
        params: {
          workname,
        },
      });

      if (workcenter.data.id) {
        framework.unblockUI();

        if (self.operation.length > 0) {
          self.props.state.mrp.workcenter_on_progress =
            self.operation[self.idx].id;

          let request = await self.env.services.rpc({
            model: "mrp.workorder",
            method: "button_start",
            args: [[self.props.state.mrp.workcenter_on_progress]],
          });

          if (request) {
            if (workcenter.data.id == 15) {
              let finalset = self.props.state.prepareVals.finalset.name;
              let final_set_id = await self.env.services.rpc({
                route: "/api/mrp/finalset",
                params: {
                  finalset,
                  operation_id: self.props.state.mrp.workcenter_on_progress,
                },
              });

              if (!final_set_id.data.id) {
                alertify.error("Final Set Not found");
              }
            }

            let mrp_machine = await self.env.services.rpc({
              route: "/api/mrp/machine",
              params: {
                machine,

                operation_id: self.props.state.mrp.workcenter_on_progress,
              },
            });

            if (mrp_machine.data.id) {
              
              let updated_value = await self.env.services.rpc({
                route: "/api/mrp/employee",
                params: {
                  employee_id: self.props.state.employee.id,
                  operation_id: self.props.state.mrp.workcenter_on_progress,
                  shift,
                  final_set_id:self.props.state.prepareVals.finalset.id,
                },
              });

              if (updated_value.success) {
                let get_current_wo = await self.env.services.rpc({
                  route: "/api/mrp/wo-json",
                  params: {
                    production_id: self.props.state.mrp.id,
                  },
                });

                if (get_current_wo.success) {
                  framework.unblockUI();

                  Object.assign(self.props.state, {
                    mrp: get_current_wo.data,
                  });

                  let data = self.props.state.mrp.workorder_ids.filter((x) => {
                    return x.state === "progress" || x.state === "done";
                  });
                  self.table.destroy();
                  self.table = $("#tbl-wo").DataTable({
                    columns: self.columns,
                    data: data,
                  });

                  self._reset();
                }
                framework.unblockUI();

              }
              framework.unblockUI();

            } else {
              framework.unblockUI();

              alertify.error("Machine Not found");
            }
          }
        }
      } else {
        framework.unblockUI();

        alertify.error("WorkCenter Not found");
      }
    }

    async finishWo(ev) {
      let self = this;
      framework.blockUI();
      ev.preventDefault();
      let workname = this.props.state.prepareVals.workcenter_id.name;
      let machine = this.props.state.prepareVals.machine_id.name;

      let shift = this.props.state.prepareVals.shift;
      let workcenter = await self.env.services.rpc({
        route: "/api/mrp/workcenter",
        params: {
          workname,
        },
      });

      let note = document.getElementById(
        `o_message_${String(this.operation[this.idx].workcenter_id.id)}`
      ).value;

      if (shift) {
        framework.unblockUI();

        if (self.operation.length > 0) {
          self.props.state.mrp.workcenter_on_progress =
            self.operation[self.idx].id;
          let request = await self.env.services.rpc({
            model: "mrp.workorder",
            method: "button_finish",
            args: [[self.props.state.mrp.workcenter_on_progress]],
          });

          if (request) {
            let updated_value = await self.env.services.rpc({
              route: "/api/mrp/employee",
              params: {
                employee_id: self.props.state.employee.id,
                operation_id: self.props.state.mrp.workcenter_on_progress,
                shift,
                note,
                final_set_id:self.props.state.prepareVals.finalset.id,
              },
            });

            if (updated_value.success) {
              let get_current_wo = await self.env.services.rpc({
                route: "/api/mrp/wo-json",
                params: {
                  production_id: self.props.state.mrp.id,
                },
              });

              if (get_current_wo.success) {
                framework.unblockUI();

                Object.assign(self.props.state, {
                  mrp: get_current_wo.data,
                });

                let data = self.props.state.mrp.workorder_ids.filter((x) => {
                  return x.state === "progress" || x.state === "done";
                });
                self.table.destroy();
                self.table = $("#tbl-wo").DataTable({
                  columns: self.columns,
                  data: data,
                });

                self.finish += 1;
                if (self.finish !== self.props.state.mrp.workorder_ids.length) {
                  self.idx += 1;
                  self.stepper.nextStep();
                } else {
                  framework.unblockUI();

                  self.props.state.isFinished = true;
                  alertify.success("Work Orders has been Finished");
                  window.location.reload();
                }

                self._reset();
              }
              framework.unblockUI();

            }

            framework.unblockUI();

          }
          framework.unblockUI();

        }
      } else {
        alertify.error("Shift should not empty");
        framework.unblockUI();
      }
    }

    async _onChangeWorkcenter() {
      let self = this;
      let workcenter_id = self.o_input_wc.attr("data-id");

      if (workcenter_id) {
        let machine_ids = await self.env.services.rpc({
          route: "/api/mrp/machineids",
          params: {
            workcenter_id,
          },
        });

        self.props.state.machine_ids = machine_ids.data.machine_ids;
      }
    }

    mounted() {
      let self = this;
      this._loadStepper();
      this._loadTable();
      this.idx = 0;
      this.operation = self.props.state.mrp.workorder_ids.filter((x) => {
        return (
          x.state === "ready" || x.state === "progress" || x.state === "pending"
        );
      });

      if (this.props.state.isFinished) {
        alertify.success("Work Orders finished !!!");
      }

      setTimeout(function () {
        // self.o_input_wc.focus();
      }, 500);

      document.body.style.background = "#FFF !important";
    }

    _loadTable() {
      let data = this.props.state.mrp.workorder_ids.filter((x) => {
        return x.state === "progress" || x.state === "done";
      });

      this.columns = [
        {
          data: "no",
        },
        // {
        //     data: "production_id.name"
        // },
        {
          data: "workcenter_id.name",
        },
        {
          data: "mesin_id.name",
        },
        {
          data: "shift",
        },
        {
          data: "employee_id.name",
        },
        {
          data: "date_start",
        },
        {
          data: "date_finished",
        },
        {
          data: "duration",
        },
        {
          data: "note",
        },
      ];

      this.table = $("#tbl-wo").DataTable({
        columns: this.columns,

        data: data,
      });
    }

    _loadStepper() {
      let self = this;
      this.finish = 0;
      this.progress = 0;

      this.props.state.mrp.workorder_ids
        .sort((a, b) => a.no_urut - b.no_urut)
        // this.props.state.mrp.workorder_ids.sort((a, b) => a.id - b.id)
        .map((result) => {
          if (result.state === "done") {
            self.finish += 1;
          } else if (result.state === "progress") {
            self.progress = +1;
          }
          return result;
        });

      const onchangeStep = (stepperForm, activeStepContent) => {
        // this.stepper.resetStepper();
        let workcenter =
          self.props.state.mrp.workorder_ids[self.finish - 1].workcenter_id
            .name;
        alertify.success(workcenter + "Finished");
        return true;
      };

      var stepperDiv = document.querySelector(".stepper");
      this.stepper = new MStepper(stepperDiv, {
        firstActive: self.finish,
        // Allow navigation by clicking on the next and previous steps on linear steppers.
        linearStepsNavigation: true,
        stepTitleNavigation: false,
        autoFocusInput: true,
        validationFunction: onchangeStep,
      });

      // this.stepper.nextStep(this._onNextStep);
    }

    destroy() {
      super.destroy(...arguments);
    }
    catchError(error) {
      console.error(error);
    }
  }

  WorkOrderScreen.template = "WorkOrderScreen";

  Registries.Component.add(WorkOrderScreen);

  return WorkOrderScreen;
});
