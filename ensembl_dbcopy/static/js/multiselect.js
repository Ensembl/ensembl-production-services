// Variable containing the selected host server details
var SrcHostDetails;

var TgtHostsDetails;

var DBNames = [];

var TableNames = [];

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

function insertItem(string, value) {
  // Code to allow multiple items to be selected in the autocomplete
  let terms = split(string);
  terms.pop();
  terms.push(value);
  terms.push("");
  return terms.join(",");
}

// Fetch Databases per server
function fetchPresentDBNames(hostsDetails, matchesDBs, thenFunc) {
  let presentDBs = [];
  let asyncCalls = [];
  $(hostsDetails).each(function (_i, hostDetails) {
    asyncCalls.push(
      $.ajax({
        url: "/api/dbcopy/databases",
        dataType: "json",
        data: {
            host: hostDetails.name,
            port: hostDetails.port,
            matches: matchesDBs,
        },
        success: function (data) {
          const hostString = hostDetailsToString(hostDetails);
          data.forEach(function (dbName) {
            presentDBs.push(hostString + "/" + dbName);
          });
        }
      })
    );
  });
  $.when.apply($, asyncCalls).then(function () {
    thenFunc(presentDBs);
  });
}

// Fetch Databases per server
function fetchPresentTableNames(hostDetails, databaseName, matchesTables, thenFunc) {
  $.ajax({
    url: "/api/dbcopy/tables",
    dataType: "json",
    data: {
        host: hostDetails.name,
        port: hostDetails.port,
        database: databaseName,
        matches: matchesTables,
    },
    success: function (data) {
        thenFunc($.makeArray(data));
    }
  });
}

function checkDBNames(dbNames, hostDetails, thenFunc) {
  if (dbNames.length && !dbNames[0].startsWith("%")) {
    thenFunc(dbNames);
  }
  else {
    $.ajax({
      url: "/api/dbcopy/databases",
      dataType: "json",
      data: {
          host: hostDetails.name,
          port: hostDetails.port,
          search: dbNames[0],
      },
      success: function (data) {
        thenFunc($.makeArray(data));
      }
    });
  }
}

function checkTableNames(tableNames, hostDetails, databaseName, thenFunc) {
  if (tableNames.length) {
    thenFunc(tableNames);
  }
  else {
    $.ajax({
      url: "/api/dbcopy/tables",
      dataType: "json",
      data: {
          host: hostDetails.name,
          port: hostDetails.port,
          database: databaseName
      },
      success: function (data) {
        thenFunc($.makeArray(data));
      }
    });
  }
}

function updateAlerts() {
  const tgtDBNames = getSplitNames("#id_tgt_db_name");
  const inclDBNames = getSplitNames("#id_src_incl_db");
  const skipDBNames = getSplitNames("#id_src_skip_db");

  if (SrcHostDetails.name) {
    if (tgtDBNames.length) {
      DBNames = tgtDBNames;
      updateTableAlert();
    }
    else if (!skipDBNames.length) {
      checkDBNames(inclDBNames, SrcHostDetails, function (foundDBNames) {
        DBNames = foundDBNames;
        updateTableAlert();
      });
    }
    else {
      checkDBNames(inclDBNames, SrcHostDetails, function (foundInclDBNames) {
        checkDBNames(skipDBNames, SrcHostDetails, function (foundSkipDBNames) {
          DBNames = arrayDiff(foundInclDBNames, foundSkipDBNames);
          updateTableAlert();
        });
      });
    }
  }
  else {
    rebuildAlerts();
  }
}

function updateTableAlert() {
  if (DBNames.length == 1) {
    const inclTables = getSplitNames("#id_src_incl_tables");
    const skipTables = getSplitNames("#id_src_skip_tables");

    checkTableNames(inclTables, SrcHostDetails, DBNames[0], function (foundTableNames) {
      TableNames = arrayDiff(foundTableNames, skipTables);
      rebuildAlerts();
    });
  }
  else {
    TableNames = [];
    rebuildAlerts();
  }
}

function buildAlertText(alertMsg, lines) {
  let alertText = "";
  if (lines.length > 0) {
    alertText += alertMsg;
    alertText += "<ul>"
    lines.forEach(function (value) {
      alertText += "<li>" + value + "</li>";
    });
    alertText += "</ul>"
  }
  return alertText;
}

function buildDBConflictsAlert(hostsDetails, dbNames) {
  fetchPresentDBNames(hostsDetails, dbNames, function (toWipeDBs) {
    let alertMsg = "<strong>Alert!</strong> The following database(s) are already present:";
    const alertText = buildAlertText(alertMsg, toWipeDBs);
    if (alertText.length) {
      insertAlertAfter("#div_id_email_list", alertText);
    }
  });
}

function buildTableConflictsAlert(hostDetails, databaseName, tableNames) {
  fetchPresentTableNames(hostDetails, databaseName, tableNames, function (foundTableNames) {
    let alertMsg = "<strong>Alert!</strong> The following table(s) are already present in the selected database:";
    const alertText = buildAlertText(alertMsg, foundTableNames);
    if (alertText.length) {
      insertAlertAfter("#div_id_email_list", alertText);
    }
  });
}

function rebuildAlerts() {
  removeAlertAfter("#div_id_email_list");
  removeAlertAfter("#div_id_email_list");
  if (SrcHostDetails.name && TgtHostsDetails.length && DBNames.length) {
    $("#submit-id-submit").prop("disabled", "true");
    if (TableNames.length && TgtHostsDetails.length == 1) {
      buildTableConflictsAlert(TgtHostsDetails[0], DBNames[0], TableNames);
    }
    buildDBConflictsAlert(TgtHostsDetails, DBNames);
    $("#submit-id-submit").removeAttr("disabled");
  }
}


// Commented until Wipe target feature is enabled by DBAs
//
// function checkWipeTarget() {
//   const sourceDBNames = getSplitNames("#id_src_incl_db");
//   const targetDBNames = getSplitNames("#id_tgt_db_name");
//   if (!(sourceDBNames.length || targetDBNames.length)) {
//     $("#id_wipe_target").prop("disabled", "true");
//   }
//   else {
//     $("#id_wipe_target").removeAttr("disabled");
//   }
// }
//
// // Initialize WipeTarget
// $(function () {
//   if ($("#id_wipe_target").length) {
//     checkWipeTarget();
//   }
// });
//
// // Enable/Disable WipeTarget when target names changes
// $(function () {
//   $("#id_tgt_db_name").change(function () {
//     checkWipeTarget();
//   });
// });
//
// // Alert if wiping target
// $(function () {
//   $("#id_wipe_target").click(function () {
//     if (this.checked) {
//       if (DBNames.length) {
//         const hostsDetails = getHostsDetails("#id_tgt_host");
//         buildConflictsAlert(hostsDetails, DBNames);
//       }
//     }
//     else {
//       removeAlertAfter("#div_id_email_list");
//     }
//   });
// });

// Hide Wipe target and Convert innodb checkboxes.
// Remember to delete this once these features are implemented by DBAs
$(function () {
  $("#div_id_wipe_target").parent().prop("hidden", "true");
  $("#div_id_convert_innodb").parent().prop("hidden", "true");
});

// Initialize Hosts Details
$(function () {
  const srcHostElem = $("#id_src_host");
  const tgtHostElem = $("#id_tgt_host");
  if (srcHostElem.length && tgtHostElem.length) {
    SrcHostDetails = getHostsDetails(srcHostElem);
    TgtHostsDetails = getHostsDetails(tgtHostElem);
    updateAlerts();
  }
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
                    //Compare list of hosts from the endpoint stored in SrcHostResults
                    //variables with the host selected by the user
                    // Store the server details into the SrcHostDetails variable
                    SrcHostDetails = item;
                }
            })
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            SrcHostDetails = hostStringToDetails($(this).val());
            updateAlerts();
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
            TgtHostsDetails = getHostsDetails(this);
            updateAlerts();
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
            updateAlerts();
            // Commented until Wipe target is enabled by DBAs
            // checkWipeTarget();
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
            updateAlerts();
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
                        search: extractLast(request.term)
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
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            updateAlerts();
            // // Commented until Wipe target is enabled by DBAs
            // checkWipeTarget();
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
                        search: extractLast(request.term)
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
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            updateAlerts();
            // // Commented until Wipe target is enabled by DBAs
            // checkWipeTarget();
        }
    });
});

// Remove error feedback
$(function () {
  $("#id_tgt_db_name").change(function () {
    $(this).removeClass("is-invalid");
    updateAlerts();
  });
});

