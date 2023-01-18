odoo.define('wibicon_attendance.tree_generate_button', function (require){
    "use strict";
    
    var core = require('web.core');
    var ListView = require('web.ListView');
    var QWeb = core.qweb;
    var Model = require('web.Model')
    
    ListView.include({       
    
            render_buttons: function($node) {
                    var self = this;
                    this._super($node);
                        this.$buttons.find('.o_generate_absen').click(this.proxy('tree_generate_action'));
            },
    
            tree_generate_action: function () {           

                console.log("ini button")
                var model = new Model('checkinout')
                model.call('action_generate_absensi', [[]]);

            } 
    
    });
    
    });
    