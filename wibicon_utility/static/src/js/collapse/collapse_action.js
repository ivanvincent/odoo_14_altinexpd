odoo.define('wibicon_utility.CollapseAction', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');

    var CollapseAction = AbstractAction.extend({
        init: function (parent) {
            this._super.apply(this, arguments);
        },
    });
    core.action_registry.add("list_collapse_action", CollapseAction);
    // console.log('gantt action loaded');
});