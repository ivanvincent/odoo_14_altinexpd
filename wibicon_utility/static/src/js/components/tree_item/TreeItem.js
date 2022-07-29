odoo.define(
  "wibicon_utility/static/src/js/components/tree_item/TreeItem.js",
  function (require) {
    "use strict";
    const { Component } = owl;
    const patchMixin = require("web.patchMixin");

    const { useState } = owl.hooks;

    class TreeItem extends Component {
      /**
       * @override
       */
      constructor(...args) {
        super(...args);
        this.state = useState({
          childrenVisible: false,
        });
      }

      toggleChildren() {
        if (
          this.props.item.child_id.length > 0 &&
          this.props.item.children == undefined
        ) {
          this.trigger("tree_item_clicked", { data: this.props.item });
        }
        Object.assign(this.state, {
          childrenVisible: !this.state.childrenVisible,
        });
      }
    }

    Object.assign(TreeItem, {
      components: { TreeItem },
      props: {
        item: {},
        countField: "",
      },
      template: "wibicon_utility.TreeItem",
    });

    return patchMixin(TreeItem);
  }
);
