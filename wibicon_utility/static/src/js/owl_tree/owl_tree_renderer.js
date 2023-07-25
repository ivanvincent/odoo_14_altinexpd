odoo.define("wibicon_utility.OWLTreeRenderer", function (require) {
  "use strict";

  const AbstractRendererOwl = require("web.AbstractRendererOwl");
  const patchMixin = require("web.patchMixin");
  const QWeb = require("web.QWeb");
  const session = require("web.session");

  const { useRef, useState } = owl.hooks;

  class OWLTreeRenderer extends AbstractRendererOwl {
    constructor(parent, props) {
      super(...arguments);
      this.qweb = new QWeb(this.env.isDebug(), { _s: session.origin });
      this.gridContainerRef = useRef("gridContainer");

      this.state = useState({
        localItems: props.items || [],
        countField: "",
      });
      if (this.props.arch.attrs.count_field) {
        Object.assign(this.state, {
          countField: this.props.arch.attrs.count_field,
        });
      }

      console.log(this);
      console.log("init renderer");
    }

    async _actionConfirm(args) {
      return await session.rpc("/web/dataset/call_button", {
        model: "purchase.order",
        method: "button_confirm",
        args: args || [],
        kwargs: {},
      });
    }

    async _actionCreatePr(args) {
      return await session.rpc("/web/dataset/call_button", {
        model: "request.requisition",
        method: "create_purchase_request",
        args: args || [],
        kwargs: {},
      });
    }

    async _actionCreatePicking(args) {
      return await session.rpc("/web/dataset/call_button", {
        model: "request.requisition",
        method: "create_picking_issue",
        args: args || [],
        kwargs: {},
      });
    }
    async _actionAppproveRR(args) {
      return await session.rpc("/web/dataset/call_button", {
        model: "request.requisition",
        method: "button_approved",
        args: args || [],
        kwargs: {},
      });
    }

    async _actionReject(args) {
      return await session.rpc("/web/dataset/call_button", {
        model: "purchase.order",
        method: "button_reject",
        args: args || [],
        kwargs: {},
      });
    }

    // _renderButtonAction(){

    // }

    // _renderFields(){

    // }

    _renderDataGrid() {
      let self = this;
      let selection_mode = this.props.arch.attrs.selection
        ? this.props.arch.attrs.selection
        : "none";
      this.dx = $(this.gridContainerRef.el).dxDataGrid({
        dataSource: this.props.items,
        showBorders: true,
        showRowLines: true,
        repaintChangesOnly: true,
        // searchPanel: {
        //   visible: true,
        //   width: 240,
        //   placeholder: 'Search...',
        // },
        selection: {
          mode: selection_mode,
        },
        remoteOperations: true,
        editing: {
          // allowDeleting: true,
          texts: {
            confirmDeleteMessage: "",
          },
        },
        // rowAlternationEnabled: true,
        hoverStateEnabled: true,
        onRowClick: function (e) {
          console.log("on row click", e);
          if (e.rowType === "data" && e.handled !== true) {
            var key = e.component.getKeyByRowIndex(e.rowIndex);
            var expanded = e.component.isRowExpanded(key);
            if (expanded) {
              e.component.collapseRow(key);
            } else {
              e.component.expandRow(key);
            }
          }
        },
        columns: [
          {
            caption: "Action",
            width: 280,
            cellTemplate: function (cellElement, cellInfo) {
              cellElement.append(
                $("<div>").dxButton({
                  text: "Approve",
                  type: "success",
                  icon: "check",
                  // stylingMode: "outlined",

                  onClick(e) {
                    e.event.stopPropagation();
                    console.log(e);
                    self._actionConfirm([cellInfo.data.id]).then((result) => {
                      if (!result) {
                        DevExpress.ui.notify("Order Confirmed", "success");
                        DevExpress.ui.dxDataGrid
                          .getInstance(self.dx)
                          .deleteRow(cellInfo.rowIndex);
                        DevExpress.ui.dxDataGrid
                          .getInstance(self.dx)
                          .deselectAll();
                        // DevExpress.ui.dxDataGrid.getInstance(dx).refresh(true);
                        // console.log(DevExpress.ui.dxDataGrid.getInstance(dx));
                      }
                    });
                  },
                })
              );
              cellElement.append(
                $(`<div style="margin-left:10px" >`).dxButton({
                  text: "Reject",
                  type: "danger",
                  icon: "clear",

                  // stylingMode: "outlined",
                  onClick(e) {
                    e.event.stopPropagation();
                    self._actionReject([cellInfo.data.id]).then((result) => {
                      if (!result) {
                        DevExpress.ui.notify("Order Rejected");
                        DevExpress.ui.dxDataGrid
                          .getInstance(self.dx)
                          .deleteRow(cellInfo.rowIndex);
                        DevExpress.ui.dxDataGrid
                          .getInstance(self.dx)
                          .deselectAll();
                        // DevExpress.ui.dxDataGrid.getInstance(dx).refresh(true);
                        // console.log(DevExpress.ui.dxDataGrid.getInstance(dx));
                      }
                    });
                  },
                })
              );
            },
          },
          // {
          //   type: "buttons",
          //   width: 110,
          //   buttons: [
          //     {
          //       hint: "tes",
          //       icon: "fa fa-envelope-o",
          //     },
          //     {
          //       text: "Approve",
          //       hint: "Approve",
          //       icon: "check",
          //       // visible(e) {
          //       //   return !e.row.isEditing;
          //       // },
          //       // disabled(e) {
          //       //   return isChief(e.row.data.Position);
          //       // },
          //       onClick(e) {
          //         const clonedItem = $.extend({}, e.row.data, {
          //           ID: (maxID += 1),
          //         });

          //         employees.splice(e.row.rowIndex, 0, clonedItem);
          //         e.component.refresh(true);
          //         e.event.preventDefault();
          //       },
          //     },
          //     {
          //       hint: "Reject",
          //       icon: "clear",
          //       // visible(e) {
          //       //   return !e.row.isEditing;
          //       // },
          //       // disabled(e) {
          //       //   return isChief(e.row.data.Position);
          //       // },
          //       onClick(e) {
          //         const clonedItem = $.extend({}, e.row.data, {
          //           ID: (maxID += 1),
          //         });

          //         employees.splice(e.row.rowIndex, 0, clonedItem);
          //         e.component.refresh(true);
          //         e.event.preventDefault();
          //       },
          //     },
          //   ],
          // },
          // {
          //   dataField: "no",
          //   dataType: "number",
          // },
          {
            caption: "Date",
            dataField: "date_order",
            dataType: "date",
            width: 110,
            alignment: "center",
          },
          {
            caption: "Purchase Order",
            dataField: "name",
            alignment: "center",
          },
          {
            caption: "Vendor",
            alignment: "center",
            calculateCellValue(data) {
              return [data.partner_id].join("");
              // return [data.partner_id[1]].join("");
            },
          },
          {
            caption: "Tax",
            dataField: "amount_tax",
            dataType: "number",
            format: {
              type: "currency",
              currency: "IDR",
            },
          },
          {
            caption: "Total",
            dataField: "amount_total",
            dataType: "number",
            format: {
              type: "currency",
              currency: "IDR",
            },
          },
        ],
        masterDetail: {
          enabled: true,
          template: (container, option) => {
            console.log(option.data);

            $("<div>")
              .dxDataGrid({
                columnAutoWidth: true,
                showBorders: true,
                columns: [
                  {
                    dataField: "no",
                    dataType: "number",
                  },
                  "product",
                  {
                    dataField: "qty_onhand",
                    caption: "Stock",
                    dataType: "number",
                  },
                  {
                    dataField: "hasil_konversi",
                    caption: "Quantity PR",
                    dataType: "number",
                  },
                  { dataField: "product_uom", caption: "Uom" },
                  {
                    dataField: "conversion",
                    caption: "Konversi",
                    dataType: "number",
                  },
                  {
                    dataField: "qty_pr",
                    caption: "Quantity PO",
                    dataType: "number",
                  },
                  {
                    dataField: "status_po",
                    caption: "Satuan PO",
                  },
                  {
                    dataField: "price_unit",
                    caption: "Price Unit",
                    dataType: "number",
                    format: {
                      type: "currency",
                      currency: "IDR",
                    },
                  },
                  {
                    dataField: "discount",
                    caption: "Discount",
                    dataType: "number",
                  },
                  {
                    dataField: "taxes_id",
                    caption: "Tax",
                    // dataType: "number",
                    // format: {
                    //   type: "currency",
                    //   currency: "IDR",
                    // },
                  },
                  {
                    dataField: "price_subtotal",
                    caption: "Sub total",
                    dataType: "number",
                    format: {
                      type: "currency",
                      currency: "IDR",
                    },
                  },
                ],
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.ArrayStore({
                    key: "id",
                    data: option.data.order_line,
                  }),
                }),
              })
              .appendTo(container);
          },
        },
      });
    }

    _renderProductAttribute() {
      let self = this;
      let selection_mode = this.props.arch.attrs.selection
        ? this.props.arch.attrs.selection
        : "none";
      this.dx = $(this.gridContainerRef.el).dxDataGrid({
        dataSource: this.props.items,
        showBorders: true,
        columnAutoWidth: true,
        showRowLines: true,
        repaintChangesOnly: true,
        selection: {
          mode: selection_mode,
        },
        remoteOperations: true,
        editing: {
          texts: {
            confirmDeleteMessage: "",
          },
        },
        hoverStateEnabled: true,
        onRowClick: function (e) {
          if (e.rowType === "data" && e.handled !== true) {
            var key = e.component.getKeyByRowIndex(e.rowIndex);
            var expanded = e.component.isRowExpanded(key);
            if (expanded) {
              e.component.collapseRow(key);
            } else {
              e.component.expandRow(key);
            }
          }
        },
        columns: [
          {
            caption: "Attribute",
            dataField: "name",
            // dataType: "date",
            width: 400,
            alignment: "center",
          },
        ],
        masterDetail: {
          enabled: false,
          template: (container, option) => {
            console.log(option.data);
            $("<div>")
              .dxTabPanel({
                items: [
                  {
                    title: "Value",
                    template: () => {
                      return $("<div>").dxDataGrid({
                        columnAutoWidth: true,
                        showBorders: true,
                        columns: [
                          {
                            type: "buttons",
                            buttons: [
                              {
                                onClick: async (e) => {
                                  e.event.stopPropagation();
                                },
                                template: function (e) {
                                  return $("<div>").append(
                                    $("<div>").dxButton({
                                      text: "Create",
                                      // type: "success",
                                      // icon: "check",
                                    })
                                  );
                                },
                              },
                            ],
                          },
                          {
                            dataField: "no",
                            dataType: "number",
                          },
                          {
                            dataField: "name",
                            caption: "Value",
                          },
                        ],
                        dataSource: new DevExpress.data.DataSource({
                          store: new DevExpress.data.ArrayStore({
                            key: "id",
                            data: option.data.value_ids,
                          }),
                        }),
                      });
                    },
                  },
                  {
                    title: "Product",
                    template: () => {
                      return $("<div>").dxDataGrid({
                        columnAutoWidth: true,
                        showBorders: true,
                        columns: [
                          {
                            dataField: "no",
                            dataType: "number",
                          },
                          {
                            dataField: "name",
                            caption: "Value",
                          },
                        ],
                        dataSource: new DevExpress.data.DataSource({
                          store: new DevExpress.data.ArrayStore({
                            key: "id",
                            data: option.data.product_tmpl_ids,
                          }),
                        }),
                      });
                    },
                  },
                ],
              })
              .appendTo(container);
          },
        },
      });
    }

    _renderDataGridRR() {
      let self = this;
      let selection_mode = this.props.arch.attrs.selection
        ? this.props.arch.attrs.selection
        : "none";
      this.dx = $(this.gridContainerRef.el).dxDataGrid({
        dataSource: this.props.items,
        showBorders: true,
        columnAutoWidth: true,
        showRowLines: true,
        repaintChangesOnly: true,
        selection: {
          mode: selection_mode,
        },
        remoteOperations: true,
        editing: {
          texts: {
            confirmDeleteMessage: "",
          },
        },
        hoverStateEnabled: true,
        onRowClick: function (e) {
          if (e.rowType === "data" && e.handled !== true) {
            var key = e.component.getKeyByRowIndex(e.rowIndex);
            var expanded = e.component.isRowExpanded(key);
            if (expanded) {
              e.component.collapseRow(key);
            } else {
              e.component.expandRow(key);
            }
          }
        },
        columns: [
          {
            type: "buttons",
            buttons: [
              {
                visible: (e) => {
                  return (
                    e.row.data.internal_transfer_count == 0 &&
                    e.row.data.state == "approved"
                  );
                },
                onClick: async (e) => {
                  e.event.stopPropagation();
                  let picking = await self._actionCreatePicking([
                    e.row.data.id,
                  ]);
                  self.trigger("do_action", { action: picking });
                },
                template: function (e) {
                  return $("<div>").append(
                    $("<div>").dxButton({
                      text: "Validate",
                      type: "success",
                      icon: "check",
                    })
                  );
                },
              },
              {
                visible: function (e) {
                  return e.row.data.state == "waiting";
                },
                onClick: (e) => {
                  e.event.stopPropagation();
                  self._actionAppproveRR([e.row.data.id]).then((resultd) => {});

                  self.env.services
                    .rpc({
                      route: "/api/request-requisition",
                      params: {
                        domain: self.props.domain,
                      },
                    })
                    .then((results) => {
                      self.props.items = results;
                      self.patched();
                      DevExpress.ui.dxDataGrid
                        .getInstance(self.dx)
                        .getDataSource()
                        .reload();
                    });
                },
                template: function (e) {
                  return $("<div>").append(
                    $("<div>").dxButton({
                      text: "Approve",
                      type: "success",
                      icon: "check",
                    })
                  );
                },
              },
              {
                visible: function (e) {
                  return (
                    e.row.data.internal_transfer_count == 0 &&
                    e.row.data.request_id == false &&
                    e.row.data.state == "approved"
                  );
                },
                onClick: async (e) => {
                  e.event.stopPropagation();
                  let pr = await self._actionCreatePr([e.row.data.id]);
                  console.log(pr);
                },
                template: function (e) {
                  return $("<div>").append(
                    $("<div>").dxButton({
                      text: "Create PR",
                      type: "success",
                      icon: "check",
                    })
                  );
                },
              },
            ],
          },
          {
            caption: "Request Date",
            dataField: "request_date",
            dataType: "date",
            width: 110,
            alignment: "center",
          },
          {
            caption: "Request By",
            dataField: "requested_by",
            alignment: "center",
          },
          {
            caption: "Request Number",
            dataField: "name",
            alignment: "center",
          },
          {
            caption: "From",
            alignment: "center",
            dataField: "request_by_warehouse",
          },
          {
            caption: "Warehouse",
            alignment: "center",
            dataField: "warehouse_id",
          },
          {
            caption: "Status",
            alignment: "center",
            dataField: "state",
          },
          {
            caption: "Purchase Request",
            alignment: "center",
            dataField: "request_id",
          },
        ],
        masterDetail: {
          enabled: true,
          template: (container, option) => {
            console.log(option.data);

            $("<div>")
              .dxDataGrid({
                columnAutoWidth: true,
                showBorders: true,
                columns: [
                  {
                    dataField: "no",
                    dataType: "number",
                  },
                  "product",
                  {
                    dataField: "spesification",
                    caption: "Spesification",
                  },
                  {
                    dataField: "name",
                    caption: "Description",
                  },
                  {
                    dataField: "quantity",
                    caption: "Quantity",
                    dataType: "number",
                  },
                  {
                    dataField: "qty_onhand",
                    caption: "On Hand",
                    dataType: "number",
                  },
                  { dataField: "uom_id", caption: "Uom" },
                ],
                dataSource: new DevExpress.data.DataSource({
                  store: new DevExpress.data.ArrayStore({
                    key: "id",
                    data: option.data.order_ids,
                  }),
                }),
              })
              .appendTo(container);
          },
        },
      });
    }

    mounted() {
      if (this.props.model === "purchase.order") {
        this._renderDataGrid();
      } else if (this.props.model === "request.requisition") {
        this._renderDataGridRR();
      } else if (this.props.model === "product.attribute") {
        this._renderProductAttribute();
      }
    }

    patched() {
      if (this.props.model === "purchase.order") {
        this._renderDataGrid();
      } else if (this.props.model === "request.requisition") {
        this._renderDataGridRR();
      } else if (this.props.model === "product.attribute") {
        this._renderProductAttribute();
      }
      super.patched(...arguments);
    }

    willUpdateProps(nextProps) {
      Object.assign(this.state, {
        localItems: nextProps.items,
      });
    }
  }

  // const components = {
  //   TreeItem: require("wibicon_utility/static/src/js/components/tree_item/TreeItem.js"),
  // };
  Object.assign(OWLTreeRenderer, {
    // components,
    defaultProps: {
      items: [],
      domain: [],
    },
    props: {
      arch: {
        type: Object,
        optional: true,
      },
      items: {
        type: Array,
      },
      isEmbedded: {
        type: Boolean,
        optional: true,
      },
      noContentHelp: {
        type: String,
        optional: true,
      },
      model: {
        type: String,
        optional: true,
      },
      domain: { type: Array, optional: true },

      // shouldUpdateRecord: Boolean,
    },
    // template: "wibicon_utility.OWLTreeRenderer",
  });

  OWLTreeRenderer.template = "wibicon_utility.OWLTreeRenderer";
  return patchMixin(OWLTreeRenderer);
});
