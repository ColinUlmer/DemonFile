//DELETE THESE TWO LINES - JUST ADMIN TESTING
document.getElementById("phone-input").value = "1";
document.getElementById("passcode-input").value = "39716";

function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

function hideWarnings() {
  document.getElementById("warning-doublephone").style.display = "none";
  document.getElementById("warning-nophone").style.display = "none";
  document.getElementById("warning-invalidcode").style.display = "none";
  document.getElementById("warning-nocode").style.display = "none";
}

function send_verification() {
  hideWarnings();
  var phone_input = document.getElementById("phone-input").value;
  $.post("/verify",
  {
    phone: phone_input,
  },
  function(data, response){
    if (data.status == "300") {
      document.getElementById("warning-doublephone").style.display = "inline";
    } else if (data.status == "301") {
      document.getElementById("warning-nophone").style.display = "inline";
      }
    else {
      var loading_icon = document.getElementById("verifying-icon");
      loading_icon.style.display = "inline";
      var send_btn = document.getElementById("send_code_btn");
      send_btn.disabled = true;
      wait(500);
      send_btn.innerHTML = "Re-send Code";
      send_btn.disabled = false;
      }
  });
}

function disableLogin() {
  var loading_icon = document.getElementById("verifying-icon");
  loading_icon.style.display = "none";
  var open_btn = document.getElementById("open-file-system-btn");
  var send_btn = document.getElementById("send_code_btn");
  open_btn.disabled=true;
  send_btn.disabled = true;
  $("#phone-input").prop('disabled', true);
  $("#passcode-input").prop('disabled', true);
}

function updateFileWindow(data) {
   if (data.length == 0) {
     document.getElementById("file-window-body").innerHTML = '<h5>No files yet, Drop files here to upload</h5>';
  } else {
    file_table = "";
    for (i=0; i < data.length; i++) {
      file_table += '<tr><td colspan="2">' + data[i]['filename'] +'</td><td>' + data[i]['type'] +'</td><td>' + data[i]['size'] +'</td></tr>';
    }
    document.getElementById("file-window-body").innerHTML = file_table;
  }
}

function reloadFiles() {
  var phone_input = document.getElementById("phone-input").value;
  var code_input = document.getElementById("passcode-input").value;
  $.post("/data/update-files",
  {
    phone: phone_input,
    code : code_input,
  },
  function(data, response){
    if(data.status == "200") {
      updateFileWindow(data.data);
    };
  });
}

function showFileWindow(){
  hideWarnings();

  var phone_input = document.getElementById("phone-input").value;
  var code_input = document.getElementById("passcode-input").value;

    $.post("/login",
    {
      phone: phone_input,
      code : code_input,
    },
    function(data, response){
      if (data.status == "303") {
        document.getElementById("warning-nocode").style.display = "inline";
      } else if (data.status == "304") {
        document.getElementById("warning-invalidcode").style.display = "inline";
      } else {
        disableLogin();
        updateFileWindow(data.data);
        var file_table = document.getElementById("file-options");
        file_table.style.display = "inline";
        document.getElementById("file-table-line").scrollIntoView();
        var newDropZone = new Dropzone("div#file-window", {
                                          url: "/upload",
                                          method: "POST",
                                          paramName: "user-file",
                                          createImageThumbnails: false,
                                          clickable: false,
                                          previewsContainer: "#dropzone-preview",
                                          uploadMultiple: true,
                                          headers: {'phone': document.getElementById("phone-input").value }
                                          });

      newDropZone.options.filedrop = {
                                      init: function () {
                                        this.on("complete", function (file) {
                                          if (this.getUploadingFiles().length === 0 && this.getQueuedFiles().length === 0) {
                                            reloadFiles();
                                          }
                                        });
                                      }
                                    };
      }

    });


}
