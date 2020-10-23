// Variable containing the selected host server details
var SrcHostDetails;

// Split a string according to a delimiter
function split(val) {
    return val.replace(/\s*/, "").replace(/,$/, "").split(",");
}

// Get the last item from a list
function extractLast(term) {
    return split(term).pop();
}

// Insert alert after
function insertAlertAfter(elem, alertText) {
  $($("#bootstrapAlert").html()).insertAfter(elem).append(alertText);
}

// Remove alert after element
function removeAlertAfter(elem) {
  $(elem).nextAll(".alert").remove();
}

// Clean and split the string in elem and return an array
function getSplitNames(elem) {
  const namesArr = split($(elem).val());
  return namesArr.filter(function (item) {
    return item != "";
  });
}

// Return the set difference: a1 / a2
function arrayDiff(a1, a2) {
  return a1.filter(function (x) {
    return !a2.includes(x);
  });
}

function hostStringToDetails(string) {
  details = string.split(':');
  return {'name': details[0], 'port': details[1]};
}

function hostDetailsToString(details) {
  return details.name + ":" + details.port;
}

function getHostsDetails(elem) {
  let serverNames = getSplitNames(elem);
  return $.map(serverNames, function (val, i) {
    return hostStringToDetails(val);
  });
}

// Fetch Databases per server
function fetchPresentDBNames(hostsDetails, DBNames) {
  let presentDBs = [];
  let asyncCalls = [];
  $(hostsDetails).each(function () {
    const hostDetails = this;
    asyncCalls.push(
      $.ajax({
        url: "/api/dbcopy/databases",
        dataType: "json",
        data: {
            host: hostDetails.name,
            port: hostDetails.port,
            matches: DBNames
        },
        success: function (data) {
          data.forEach(function (dbname) {
            presentDBs.push(hostDetailsToString(hostDetails) + "/" + dbname);
          });
        }
    }));
  });
  return [presentDBs, asyncCalls];
}

function buildWipeAlert(hostsDetails, DBNames) {
  $("#submit-id-submit").prop("disabled", "true");
  let [toWipeDBs, asyncCalls] = fetchPresentDBNames(hostsDetails, DBNames);
  $.when.apply($, asyncCalls).then(function () {
    if (toWipeDBs.length > 0) {
      let alertText = "<strong>Alert!</strong> The following database(s) will be erased before the copy:";
      alertText += "<ul>"
      toWipeDBs.forEach(function (value) {
        alertText += "<li>" + value + "</li>";
      });
      alertText += "</ul>"
      insertAlertAfter("#div_id_wipe_target", alertText);
    }
    $("#submit-id-submit").removeAttr("disabled");
  });
}

function checkPresentDBs() {
  const hostsDetails = getHostsDetails("#id_tgt_host");
  const targetDBNames = getSplitNames("#id_tgt_db_name");
  const skipDBNames = getSplitNames("#id_src_skip_db");
  const sourceDBNames = getSplitNames("#id_src_incl_db");
  const sourceDBNamesFiltered = arrayDiff(sourceDBNames, skipDBNames);
  if (targetDBNames.length) {
    buildWipeAlert(hostsDetails, targetDBNames);
  }
  else if (sourceDBNamesFiltered.length) {
    buildWipeAlert(hostsDetails, sourceDBNamesFiltered);
  }
}

function insertItem(string, value) {
  // Code to allow multiple items to be selected in the autocomplete
  let terms = split(string);
  terms.pop();
  terms.push(value);
  terms.push("");
  return terms.join(",");
}

function checkWipeTarget() {
  const sourceDBNames = getSplitNames("#id_src_incl_db");
  const targetDBNames = getSplitNames("#id_tgt_db_name");
  if (!(sourceDBNames.length || targetDBNames.length)) {
    $("#id_wipe_target").prop("disabled", "true");
  }
  else {
    $("#id_wipe_target").removeAttr("disabled");
  }
}

// Initialize SrcHostDetails
$(function () {
  const srcHostElem = $("#id_src_host");
  if (srcHostElem.length) {
    const srcHostElemArray = getSplitNames($("#id_src_host"));
    if (srcHostElemArray.length) {
      SrcHostDetails = hostStringToDetails(srcHostElemArray[0]);
    }
  }
});

// Initialize WipeTarget
$(function () {
  if ($("#id_wipe_target").length) {
    checkWipeTarget();
  }
});

// Enable/Disable WipeTarget when target names changes
$(function () {
  $("#id_tgt_db_name").change(function () {
    checkWipeTarget();
  });
});

// Autocomplete for the source host field
$(function () {
    var SrcHostResults;
    $("#id_src_host").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/api/dbcopy/src_host",
                dataType: "json",
                data: {
                    name: request.term
                },
                success: function (data) {
                    SrcHostResults = data.results
                    response($.map(data.results, function (item) {
                        return hostDetailsToString(item);
                    }));
                }
            });
        },
        minLength: 1,
        select: function (event, ui) {
            $.map(SrcHostResults, function (item) {
                let curr_item = hostDetailsToString(item);
                if (ui.item.value === curr_item) {
                    //Compare list of hosts from the endpoint stored in SrcHostResults variables with the host selected by the user
                    // Store the server details into the SrcHostDetails variable
                    SrcHostDetails = item;
                }
            })
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            SrcHostDetails = hostStringToDetails($(this).val());
        }
    });
});
// Autocomplete for the target host field (allows mutiple values)
$(function () {
    $("#id_tgt_host").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/api/dbcopy/tgt_host",
                dataType: "json",
                data: {
                    name: extractLast(request.term)
                },
                success: function (data) {
                    response($.map(data.results, function (item) {
                        return hostDetailsToString(item);
                    }));
                }
            });
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            this.value = insertItem(this.value, ui.item.value);
            return false;
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
        }
    });
});
// Autocomplete for the list of databases to copy
$(function () {
    $("#id_src_incl_db").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/api/dbcopy/databases",
                dataType: "json",
                data: {
                    host: SrcHostDetails.name,
                    port: SrcHostDetails.port,
                    search: extractLast(request.term)
                },
                success: function (data) {
                    response(data);
                }
            });
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            this.value = insertItem(this.value, ui.item.value);
            return false;
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            checkWipeTarget();
        }
    });
});
// Autocomplete for the list of databases to skip
$(function () {
    $("#id_src_skip_db").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/api/dbcopy/databases",
                dataType: "json",
                data: {
                    host: SrcHostDetails.name,
                    port: SrcHostDetails.port,
                    search: extractLast(request.term)
                },
                success: function (data) {
                    response(data);
                }
            });
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            this.value = insertItem(this.value, ui.item.value);
            return false;
        },
        change: function () {
            $(this).removeClass("is-invalid");
        }
    });
});
// Autocomplete for the list of tables to copy
$(function () {
    $("#id_src_incl_tables").autocomplete({
        source: function (request, response) {
            const srcDBs = getSplitNames("#id_src_incl_db");
            if (srcDBs.length) {
                $.ajax({
                    url: "/api/dbcopy/tables",
                    dataType: "json",
                    data: {
                        host: SrcHostDetails.name,
                        port: SrcHostDetails.port,
                        // Get the first database from the id_src_incl_db field
                        database: srcDBs[0],
                        filter: extractLast(request.term)
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            }
            else {
                response([]);
            }
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            this.value = insertItem(this.value, ui.item.value);
            return false;
        }
    });
});
// Autocomplete for the list of tables to skip
$(function () {
    $("#id_src_skip_tables").autocomplete({
        source: function (request, response) {
            const srcDBs = getSplitNames("#id_src_incl_db");
            if (srcDBs.length) {
                $.ajax({
                    url: "/api/dbcopy/tables",
                    dataType: "json",
                    data: {
                        host: SrcHostDetails.name,
                        port: SrcHostDetails.port,
                        // Get the first database from the id_src_incl_db field
                        database: srcDBs[0],
                        filter: extractLast(request.term)
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            }
            else {
                response([]);
            }
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            this.value = insertItem(this.value, ui.item.value);
            return false;
        }
    });
});

// Alert if wiping target
$(function () {
  $("#id_wipe_target").click(function () {
    if (this.checked) {
      checkPresentDBs();
    }
    else {
      removeAlertAfter("#div_id_wipe_target");
    }
  });
});

// Remove error feedback
$(function () {
  $("#id_tgt_db_name").change(function () {
    $(this).removeClass("is-invalid");
  });
});

