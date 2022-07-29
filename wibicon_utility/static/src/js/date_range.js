odoo.define("wibicon_utility.date_range", function (require) {
  "use strict";
  let core = require("web.core");
  let time = require("web.time");
  const { DatePicker, DateTimePicker } = require("web.DatePickerOwl");
  var pyUtils = require("web.py_utils");

  const Domain = require("web.Domain");

  const ControlPanel = require("web.ControlPanel");

  let ListController = require("web.ListController");
  let field_utils = require("web.field_utils");
  let _t = core._t;
  let qweb = core.qweb;

  // var datepicker = require('web.datepicker');

  function renderDateRangeButton() {
    if (this.$buttons) {
      let self = this;
      this.isRefresh = false;
      this.customDomain;
      this.filter_group_id = null;
      this.$buttons.on("change", ".select_date_range_fields", function (ev) {
        self.date_field_selected =
          self.date_fields[
            $("select[name='date_range'] option:selected").index() - 1
          ];

        if (self.$buttons.find("input#date_range_start") !== "") {
          self.$buttons.find("input#date_range_start").val("");
        }
        if (self.$buttons.find("input#date_range_end") !== "") {
          self.$buttons.find("input#date_range_end").val("");
        }
        return self.update({
          domain: self.initialState.getDomain(),
          context: self.renderer.state.context,
        });
      });

      this.dateRangePickerOptions = {
        timePicker: self.date_field_selected?.type === "date" ? true : false,
        timePicker24Hour:
          _t.database.parameters.time_format.search("%H") !== -1,
        autoUpdateInput: false,
        timePickerIncrement: 5,
        autoApply: true,
        // showDropdowns: true,
        // parentEl:'div.o_rangedatepicker_container',
        locale: {
          format:
            self.date_field_selected?.type === "datetime"
              ? time.getLangDatetimeFormat()
              : time.getLangDateFormat(),
        },
      };

      this.$buttons
        .find('input[name="daterange"]')
        .daterangepicker(
          self.dateRangePickerOptions,
          (start, end, label) => {}
        );

      this.$buttons.on(
        "click",
        "a.btn-refresh-date",
        this._refreshInput.bind(this)
      );
    }
  }

  let includeDict = {
    update: function (params, options) {
      let self = this;
      let customfacetremoved = false;
      const facets = this.controlPanelProps.searchModel.get("facets");

      console.log("update", this);

      if (facets.length) {
        for (const facet in facets) {
          if (facets[facet].title === self.descriptionFilter) {
            self.filter_group_id = facets[facet].groupId;
            customfacetremoved = true;
            break;
          } else self._clearInput();
        }
      } else {
        self._clearInput();
      }

      return this._super.apply(this, arguments);
    },
    jsLibs: [
      "/web/static/lib/daterangepicker/daterangepicker.js",
      "/web/static/src/js/libs/daterangepicker.js",
    ],
    cssLibs: ["/web/static/lib/daterangepicker/daterangepicker.css"],

    events: _.extend({}, ListController.prototype.events, {
      "apply.daterangepicker": "_applyDateChanges",
    }),

    // events: {
    //   // "show.datetimepicker": "_onDateTimePickerShow",
    //   // "click a.btn-refresh-date": "_refreshInput",
    //   "apply.daterangepicker": "_applyDateChanges",
    //   // "hide.datetimepicker": "_onDateTimePickerHide",
    //   // "change input#date_range_start": "_changeDateStart",
    // },

    _refreshInput: function () {
      // ev.preventDefault();
      let self = this;
      self.$buttons.find("input#date_range_start").val("");
      self.$buttons.find("input#date_range_end").val("");
      self.customDomain = [];
      self.controlPanelProps.searchModel.dispatch("search");
      this.isRefresh = true;
    },

    _applyDateChanges: function (ev, picker) {
      let self = this;

      this.formatType = "date";
      let displayStartDate = field_utils.format[this.formatType](
        picker.startDate,
        {},
        { timezone: false }
      );
      let displayEndDate = field_utils.format[this.formatType](
        picker.endDate,
        {},
        { timezone: false }
      );

      if (
        this.date_field_selected === null ||
        this.date_field_selected === undefined
      ) {
        return self.do_notify("invalid field", _t("Please Choose Date Field"));
      } else {
        let { field, label } = this.date_field_selected;

        this.val_start = this.$buttons
          .find("input#date_range_start")
          .val(displayStartDate);
        this.val_end = this.$buttons
          .find("input#date_range_end")
          .val(displayEndDate);

        if (this.val_start && this.val_end) this.customDomain = [];
        this.customDomain = [];

        if (this.date_field_selected && this.val_start) {
          self.customDomain.push([
            field,
            ">=",
            field_utils.parse["date"](displayStartDate, null, {
              timezone: false,
            }).format("YYYY-MM-DD"),
          ]);
        }

        if (this.date_field_selected && this.val_end) {
          self.customDomain.push([
            field,
            "<=",
            field_utils.parse["date"](displayEndDate, null, {
              timezone: false,
            }).format("YYYY-MM-DD"),
          ]);
        }

        this.descriptionFilter = `${label} is between  ${displayStartDate} and ${displayEndDate}`;

        this.dateRangeFilters = [
          {
            description: this.descriptionFilter,
            domain: Domain.prototype.arrayToString(this.customDomain),
            type: "filter",
          },
        ];

        if (this.filter_group_id) {
          this.controlPanelProps.searchModel.dispatch(
            "deactivateGroup",
            this.filter_group_id
          );
        }

        this.customeFilterIds = self.controlPanelProps.searchModel.dispatch(
          "createNewFilters",
          this.dateRangeFilters
        );

        return this.customeFilterIds;
      }
    },

    _clearInput: function () {
      this.$buttons.find("input#date_range_start").val("");
      this.$buttons.find("input#date_range_end").val("");
    },

    _onDateRangePickerHide: function () {
      this._isOpen = false;
      // if (this._onScroll) {
      //   window.removeEventListener("scroll", this._onScroll, true);
      // }
    },

    willStart: function () {
      let self = this;
      this.date_fields = [];
      this.start_date = null;
      this.end_date = null;
      this.date_field_selected = null;

      _.each(this.initialState.fields, function (value, key, list) {
        if (
          (value.store && value.type === "datetime") ||
          value.type === "date"
        ) {
          self.date_fields.push({
            field: key,
            label: value.string,
            type: value.type,
          });
        }
      });

      return Promise.all([this._super.apply(this, arguments)]);
    },

    renderButtons: function () {
      this._super.apply(this, arguments);
      this.$searchWidget = $(
        qweb.render("DateRangeListView.buttons", {
          widget: this,
        })
      );
      this.$searchWidget.appendTo(this.$buttons);
      renderDateRangeButton.apply(this, arguments);
    },
  };

  ListController.include(includeDict);
});
