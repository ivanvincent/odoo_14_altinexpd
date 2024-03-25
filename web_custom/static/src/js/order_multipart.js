odoo.define("web_custom.order_multipart", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
  
    publicWidget.registry.OrderMultipart = publicWidget.Widget.extend({
      selector: ".o_order_multipart_main",
      events: {
        submit: "_onSubmit",
        // 'click .o_button_subcribe': "_onSubmit",
        // submit: "_onSubmit",
        // "change input.uploadProfileInput": "_onChangeImageProfile",
        // "change input#o_input_img_identity": "_onChangeImageIdPhoto",
        // "change input#o_input_img_payment": "_onChangeImageProofOfPayments",
        // "change select#slct": "_onChangeJobTitle",
        // "change input#o_term_checkbox": "_onChangeCheckBoxAgreement",
      },
  
      init: function (parent, options) {
        this._super.apply(this, arguments);      
        console.log("testt");
      },
      _onSubmit: async function (ev) {
        // ev.stopPropagation();
        console.log('=========_onSubmit=====');
        ev.preventDefault();
        let self = this;
        // if (self.imgProfile === undefined){
        //   $(".o_img_profile_wrapper").append(
        //     '<div class="snackbar show" role="alert"><i class="fa fa-check-circle text-danger"></i> Profile image must be required!</div>'
        //   );
        // }else{
        
        let holder_specifications = $("select[name='holder_specifications']").val();
        let holder_positions = $("select[name='holder_positions']").val();
        let holder_materials = $("select[name='holder_materials']").val();
        let dust_cup_configurations = $("select[name='dust_cup_configurations']").val();
        let keyway_configurations = $("select[name='keyway_configurations']").val();
        let keyway_positions = $("select[name='keyway_positions']").val();
        let head_flat_extensions = $("select[name='head_flat_extensions']").val();
        let holder_heat_treatments = $("select[name='holder_heat_treatments']").val();
        let holder_surface_treatments = $("select[name='holder_surface_treatments']").val();
        let tip_shapes = $("select[name='tip_shapes']").val();
        let tip_positions = $("select[name='tip_positions']").val();
        let tip_materials = $("select[name='tip_materials']").val();
        let tip_heat_treatments = $("select[name='tip_heat_treatments']").val();
        let tip_surface_treatments = $("select[name='tip_surface_treatments']").val();
        let holder_caps = $("select[name='holder_caps']").val();
        let holder_cap_bores = $("select[name='holder_cap_bores']").val();
        let holder_cap_surface_treatments = $("select[name='holder_cap_surface_treatments']").val();
        let custom_adjustments = $("select[name='custom_adjustments']").val();
        let fat_options = $("select[name='fat_options']").val();
        let hobbs = $("select[name='hobbs']").val();
        let drawings = $("select[name='drawings']").val();
        //   let lastName = $("input.o_input_lastname").val();
        //   let email = $("input.o_input_email").val();
        //   let idNumber = $("input.o_input_id_number").val();
        //   let phoneNumber = $("input.o_input_phone").val();
        //   let gender = $("input[name='gender']:checked").val();
        //   let address = $("input.o_input_address").val();
        //   let job = $("#slct :selected").val();
        //   job =
        //     $("#slct :selected").val() !== "Others"
        //       ? $("#slct :selected").val()
        //       : $("#input#other_jobs").val();
        //   let imgProfile = self.imgProfile;
        //   let idPhoto = self.idPhoto;
        //   let proofOfPayments = self.proofOfPayments;
          try {
            var btn = $(".o_button_order_multipart")
            btn.html("<i class='fa fa-spinner fa-spin '></i> Processing Order Multipart");
            btn.prop("disabled", true);
            let response = await self._rpc({
              route: "/confirm-multipart",
              params: {
                data: {
                  holder_specifications,
                  holder_positions,
                  holder_materials,
                  dust_cup_configurations,
                  keyway_configurations,
                  keyway_positions,
                  head_flat_extensions,
                  holder_heat_treatments,
                  holder_surface_treatments,
                  tip_shapes,
                  tip_positions,
                  tip_materials,
                  tip_heat_treatments,
                  tip_surface_treatments,
                  holder_caps,
                  holder_cap_bores,
                  holder_cap_surface_treatments,
                  custom_adjustments,
                  fat_options,
                  hobbs,
                  drawings,
                },
              },
            });
            console.log(response);
    
          } catch (error) {
                console.error(error);
                // window.location.href = "/page/error";
          }

        // }
  
        // this._rpc
      },
  
      // _onChangeCheckBoxAgreement : function (params) {
      //   if ($("#o_term_checkbox:checked").length > 0){
      //     window.open("http://thinkresearchinstitute.com/pdf/approval.pdf","_blank", "width=700,height=700");
      //   }
      // }
  
    });
  });
  