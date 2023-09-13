odoo.define("web_custom.order_die", function (require) {
    "use strict";
  
    var publicWidget = require("web.public.widget");
  
    publicWidget.registry.OrderDie = publicWidget.Widget.extend({
      selector: ".o_order_die_main",
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
        let basics = $("select[name='basics']").val();
        let materials = $("select[name='materials']").val();
        let bores = $("select[name='bores']").val();
        let single_or_multi = $("select[name='single_or_multi']").val();
        let die_screws = $("select[name='die_screws']").val();
        let optional_tapered_bores = $("select[name='optional_tapered_bores']").val();
        let heat_treatments = $("select[name='heat_treatments']").val();
        let surface_treatments = $("select[name='surface_treatments']").val();
        let custom_adjustments = $("select[name='custom_adjustments']").val();
        let fat_options = $("select[name='fat_options']").val();
        let die_setting_aligners = $("select[name='die_setting_aligners']").val();
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
            var btn = $(".o_button_order_die")
            btn.html("<i class='fa fa-spinner fa-spin '></i> Processing Order Die");
            btn.prop("disabled", true);
            let response = await self._rpc({
              route: "/confirm-die",
              params: {
                data: {
                    basics,
                    materials,
                    bores,
                    single_or_multi,
                    die_screws,
                    optional_tapered_bores,
                    heat_treatments,
                    surface_treatments,
                    custom_adjustments,
                    fat_options,
                    die_setting_aligners,
                },
              },
            });
            console.log(response);
    
          } catch (error) {
                console.error(error);
                window.location.href = "/page/success";
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
  