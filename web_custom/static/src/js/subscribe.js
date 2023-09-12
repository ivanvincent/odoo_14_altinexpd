odoo.define("web_custom.subscribe", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var core = require('web.core');
  var session = require('web.session');

  publicWidget.registry.ElearningSubscribe = publicWidget.Widget.extend({
    selector: ".o_subscribe_s_main",
    events: {
      submit: "_onSubmit",
      // 'click .o_button_subcribe': "_onSubmit",
      // submit: "_onSubmit",
      "change input.uploadProfileInput": "_onChangeImageProfile",
      "change input#o_input_img_identity": "_onChangeImageIdPhoto",
      "change input#o_input_img_payment": "_onChangeImageProofOfPayments",
      "change select#slct": "_onChangeJobTitle",
      // "change input#o_term_checkbox": "_onChangeCheckBoxAgreement",
    },

    init: function (parent, options) {
      this._super.apply(this, arguments);      
      console.log("testt");
    },

    _onChangeJobTitle: function (ev) {
      console.log("tusttt");
      let job = $("select#slwebct :selected").val();
      // console.log("on change job title", job);
      if (job === "Others") {
        $("input#other_jobs").removeClass("d-none");
      } else {
        $("input#other_jobs").addClass("d-none");
      }
    },

    _onChangeImageProfile: function (ev) {
      console.log('_onChangeImageProfile');
      let self = this;
      let triggerInput = this;
      this.imgProfile = null;
      let currentImg = $(".o_img_holder").find(".o_default_img").attr("src");

      let holder = $(".o_img_holder");
      let wrapper = $(".o_img_profile_wrapper");
      $(wrapper).find('[role="alert"]').remove();
      let files = !!ev.target.files ? ev.target.files : [];

      if (!files.length || !window.FileReader) {
        return;
      }

      if (/^image/.test(files[0].type)) {
        var reader = new FileReader();
        reader.readAsDataURL(files[0]);
        reader.onloadend = function () {
          $(holder).addClass("uploadInProgress");

          self.imgProfile = this.result;
          $(holder).find(".o_default_img").attr("src", this.result);
          $(holder).append(
            '<div class="upload-loader"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div></div>'
          );

          setTimeout(() => {
            $(holder).removeClass("uploadInProgress");
            $(holder).find(".upload-loader").remove();
            if (Math.random() < 0.9) {
              $(wrapper).append(
                '<div class="snackbar show" role="alert"><i class="fa fa-check-circle text-success"></i> Profile image updated successfully</div>'
              );

              $(triggerInput).val("");

              setTimeout(() => {
                $(wrapper).find('[role="alert"]').remove();
              }, 3000);
            } else {
              $(holder).find(".pic").attr("src", currentImg);
              $(wrapper).append(
                '<div class="snackbar show" role="alert"><i class="fa fa-times-circle text-danger"></i> There is an error while uploading! Please try again later.</div>'
              );

              $(triggerInput).val("");
              setTimeout(() => {
                $(wrapper).find('[role="alert"]').remove();
              }, 3000);
            }
          }, 1500);
        };
      } else {
        $(wrapper).append(
          '<div class="alert alert-danger d-inline-block p-2 small" role="alert">Please choose the valid image.</div>'
        );

        console.log("on else");
        setTimeout(() => {
          $(wrapper).find('role="alert"').remove();
        }, 3000);
      }
    },

    _onChangeImageIdPhoto: function (ev) {
      ev.stopPropagation();
      let self = this;
      let files = !!ev.target.files ? ev.target.files : [];

      if (/^image/.test(files[0].type)) {
        var reader = new FileReader();
        reader.readAsDataURL(files[0]);
        reader.onloadend = function () {
          self.idPhoto = { data: this.result, mimeType: files[0].type };
        };
      } else {
        console.log("failde");
      }

      console.log("on change imageid photo");
      console.log(this.idPhoto);
    },

    _onChangeImageProofOfPayments: function (ev) {
      let self = this;
      let files = !!ev.target.files ? ev.target.files : [];

      if (/^image/.test(files[0].type)) {
        var reader = new FileReader();
        reader.readAsDataURL(files[0]);
        reader.onloadend = function () {
          self.proofOfPayments = { data: this.result, mimeType: files[0].type };
        };
      } else {
        console.log("failed");
      }
    },

    _onSubmit: async function (ev) {
      // ev.stopPropagation();
      ev.preventDefault();
      let self = this;
      // first_pw = $("input.first_password").val();
      // first_confirm_password = $("input.confirm_password").val();
      // console.log(first_pw);
      // console.log(first_confirm_password);
      // if (first_pw != first_confirm_password) {
      //   $(".o_img_profile_wrapper").append(
      //     '<div class="snackbar show" role="alert"><i class="fa fa-check-circle text-danger"></i> Password tidak sesuai!</div>'
      //   );
      //   return
      // }
      if (self.imgProfile === undefined){
        $(".o_img_profile_wrapper").append(
          '<div class="snackbar show" role="alert"><i class="fa fa-check-circle text-danger"></i> Profile image must be required!</div>'
        );
      }else{
        let firstName = $("input.o_input_firstname").val();
        let lastName = $("input.o_input_lastname").val();
        let email = $("input.o_input_email").val();
        let idNumber = $("input.o_input_id_number").val();
        let phoneNumber = $("input.o_input_phone").val();
        let gender = $("input[name='gender']:checked").val();
        let address = $("input.o_input_address").val();
        let job = $("#slct :selected").val();
        job =
          $("#slct :selected").val() !== "Others"
            ? $("#slct :selected").val()
            : $("#input#other_jobs").val();
        let imgProfile = self.imgProfile;
        let idPhoto = self.idPhoto;
        let proofOfPayments = self.proofOfPayments;
        try {
          var btn = $(".o_button_subcribe")
          btn.html("<i class='fa fa-spinner fa-spin '></i> Processing Subscribe");
          btn.prop("disabled", true);
          let response = await self._rpc({
            route: "/register",
            params: {
              data: {
                firstName,
                lastName,
                email,
                idNumber,
                phoneNumber,
                gender,
                job,
                imgProfile,
                idPhoto,
                proofOfPayments,
                address,
              },
            },
          });
  
          console.log(response);
  
          if (response.success) {
            window.location.href = "/page/success" + '?user=' + btoa(firstName + ' ' + lastName);
          } else {
            if (response.code == 889){
              btn.html("Subscribe");
              btn.prop("disabled", false);
              $(".o_img_profile_wrapper").append(
                '<div class="snackbar show" role="alert"><i class="fa fa-check-circle text-danger"></i>'+response.message+'</div>'
              );
            }else{
              window.location.href = "/page/error";
            }
          }
        } catch (error) {
          console.error(error);
          window.location.href = "/page/error";
        }

      }

      // this._rpc
    },

    // _onChangeCheckBoxAgreement : function (params) {
    //   if ($("#o_term_checkbox:checked").length > 0){
    //     window.open("http://thinkresearchinstitute.com/pdf/approval.pdf","_blank", "width=700,height=700");
    //   }
    // }

  });
});
