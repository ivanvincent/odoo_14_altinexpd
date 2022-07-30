odoo.define("wibicon_mo_scanner.Autocomplete", function (require) {
  "use strict";

  const { Component, useState, hooks } = owl;
  const Registries = require("wibicon_mo_scanner.Registries");
  const core = require("web.core");
  const { useExternalListener } = hooks;

  let _t = core._t;
  let _lt = core._lt;

  class Autocomplete extends Component {
    constructor(...args) {
      super(...args);
      useExternalListener(window, "click", this.hideOptions);
    }

    static props = {
      field: String,
      model: String,
      id: Number,
      placeHolder: { type: String, optional: true },
      inputClass: { type: String, optional: true },
      dropdownClass: { type: String, optional: true },
      data: {
        type: Array,
        optional: true,
      },
      value: { name: "", optional: true },
    };

    state = useState({
      showOptions: false,
      chosenOption: "",
      searchTerm: "",
    });

    hideOptions(event) {
      if (!this.el.contains(event.target)) {
        Object.assign(this.state, { showOptions: false });
      }
    }

    reset() {
      this.trigger("input", "");
      this.trigger("chosen", { prepareVals: null });
      Object.assign(this.state, {
        chosenOption: "",
        searchTerm: "",
        showOptions: false,
      });
    }

    handleShowOptions(evt) {
      Object.assign(this.state, {
        searchTerm: evt.target.value,
        showOptions: true,
      });
    }

    searchResults() {
      return this.props.data.filter((item) => {
        if (this.props.field == "shift")
          return item
            .toLowerCase()
            .includes(this.state.searchTerm.toLowerCase());
        return item.text
          .toLowerCase()
          .includes(this.state.searchTerm.toLowerCase());
      });
    }

    async handleClick(item) {
      this.trigger("input", item.text);
      this.trigger("chosen", { prepareVals: item });
      Object.assign(this.state, {
        chosenOption: item.text,
        showOptions: false,
        searchTerm: item.text,
      });
    }
  }

  Autocomplete.template = "Autocomplete";

  Registries.Component.add(Autocomplete);

  return Autocomplete;
});
