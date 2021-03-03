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
function insertAlertAfter(elem, divID, alertText) {
  $($("#bootstrapAlert").html()).insertAfter(elem).attr('id', divID).append(alertText);
}

function insertAlertBefore(elem, divID, alertText) {
  $($("#bootstrapAlert").html()).insertBefore(elem).attr('id', divID).append(alertText);
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
  return details.name + ":" + details.port ;
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
        url: `/api/dbcopy/databases/${hostDetails.name}/${hostDetails.port}`,
        dataType: "json",
        data: {
            matches: matchesDBs,
        },
        success: function (data) {
          const hostString = hostDetailsToString(hostDetails);
          data.forEach(function (dbName) {
            presentDBs.push(hostString + "/" + dbName);
          });
        },
        error: function (_request, _textStatus, _error) {
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
    url: `/api/dbcopy/tables/${hostDetails.name}/${hostDetails.port}/${databaseName}`,
    dataType: "json",
    data: {
        matches: matchesTables,
    },
    success: function (data) {
        thenFunc($.makeArray(data));
    },
    error: function (_request, _textStatus, _error) {
        thenFunc([]);
    }
  });
}

function checkDBNames(dbNames, hostDetails, thenFunc) {
  if (dbNames.length && dbNames.length > 1) {
    thenFunc(dbNames);
  }
  else {
    $.ajax({
      url: `/api/dbcopy/databases/${hostDetails.name}/${hostDetails.port}`,
      dataType: "json",
      data: {
          search: dbNames[0],
      },
      success: function (data) {
        thenFunc($.makeArray(data));
      },
      error: function (_request, _textStatus, _error) {
        thenFunc([]);
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
      url: `/api/dbcopy/tables/${hostDetails.name}/${hostDetails.port}/${databaseName}`,
      dataType: "json",
      success: function (data) {
        thenFunc($.makeArray(data));
      },
      error: function (_request, _textStatus, _error) {
        thenFunc([]);
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

function updateTableAlert(tableOnly) {
  if (DBNames.length == 1) {
    const inclTables = getSplitNames("#id_src_incl_tables");
    const skipTables = getSplitNames("#id_src_skip_tables");

    checkTableNames(inclTables, SrcHostDetails, DBNames[0], function (foundTableNames) {
      TableNames = arrayDiff(foundTableNames, skipTables);
      rebuildAlerts(tableOnly);
    });
  }
  else {
    TableNames = [];
    rebuildAlerts(tableOnly);
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
      insertAlertAfter("#div_id_email_list", "db-alert", alertText);
    }
  });
}

function buildTableConflictsAlert(hostDetails, databaseName, tableNames) {
  fetchPresentTableNames(hostDetails, databaseName, tableNames, function (foundTableNames) {
    let alertMsg = "<strong>Alert!</strong> The following table(s) are already present in the selected database:";
    const alertText = buildAlertText(alertMsg, foundTableNames);
    if (alertText.length) {
      insertAlertBefore($("#submit-id-submit").parent().parent(), "table-alert", alertText);
    }
  });
}

function rebuildAlerts(tableOnly) {
  if (SrcHostDetails.name && TgtHostsDetails.length && DBNames.length) {
    $("#submit-id-submit").prop("disabled", "true");
    $("#table-alert").remove();
    if (TableNames.length && TgtHostsDetails.length == 1) {
      buildTableConflictsAlert(TgtHostsDetails[0], DBNames[0], TableNames);
    }
    if (!tableOnly) {
      $("#db-alert").remove();
      buildDBConflictsAlert(TgtHostsDetails, DBNames);
    }
    $("#submit-id-submit").removeAttr("disabled");
  }
  else {
    $("#db-alert").remove();
    $("#table-alert").remove();
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
  $("#div_id_dry_run").parent().prop("hidden", "true");
});

// Initialize Hosts Details
$(function () {
  const srcHostElem = $("#id_src_host");
  const tgtHostElem = $("#id_tgt_host");
  if (srcHostElem.length && tgtHostElem.length) {
    SrcHostDetails = hostStringToDetails(srcHostElem.val());
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
                        return  item; //hostDetailsToString(item);
                    }));
                }
            });
        },
        minLength: 1,
        select: function (event, ui) {

            let seletedItem = hostDetailsToString(ui.item);
            $.map(SrcHostResults, function (item) {
                let curr_item = hostDetailsToString(item);
                if (seletedItem === curr_item) {
                    //Compare list of hosts from the endpoint stored in SrcHostResults
                    //variables with the host selected by the user
                    // Store the server details into the SrcHostDetails variable
                    SrcHostDetails = item;
                    if(item.active){
                      $('#id_src_host').val(seletedItem);
                    }
                    
                }
            })
            return false;
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            SrcHostDetails = hostStringToDetails($(this).val());
            updateAlerts();
        }
    }).data( "ui-autocomplete" )._renderItem = function( ul, item ) {
      let active = 'badge-danger';
      let desc = 'Not Active';
      if(item.active){
        active = 'badge-success';
        desc = 'Active'
      }
      return $( "<li>" )
      .append( '<span class="badge badge-pill '+  active + '">'+ desc+'</span> <span>' + item.name +'</span>')
      .appendTo( ul );
   };
    
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
                    return  item; //hostDetailsToString(item);
                  }));
                }
            });
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            let seletedItem = hostDetailsToString(ui.item); 
            if(ui.item.active){
              this.value = insertItem(this.value, seletedItem );
            }
            return false;
        },
        change: function (event, ui) {
            $(this).removeClass("is-invalid");
            TgtHostsDetails = getHostsDetails(this);
            updateAlerts();
        }
    }).data( "ui-autocomplete" )._renderItem = function( ul, item ) {
      let active = 'badge-danger';
      let desc = 'Not Active';
      if(item.active){
        active = 'badge-success';
        desc = 'Active'
      }
      return $( "<li>" )
      .append( '<span class="badge badge-pill '+  active + '">'+ desc+'</span> <span>' + item.name +'</span>')
      .appendTo( ul );
   };
});
// Autocomplete for the list of databases to copy
$(function () {
    $("#id_src_incl_db").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: `/api/dbcopy/databases/${SrcHostDetails.name}/${SrcHostDetails.port}`,
                dataType: "json",
                data: {
                    search: extractLast(request.term)
                },
                success: function (data) {
                    response(data);
                },
                error: function (_request, _textStatus, _error) {
                  response([]);
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
                url: `/api/dbcopy/databases/${SrcHostDetails.name}/${SrcHostDetails.port}`,
                dataType: "json",
                data: {
                    search: extractLast(request.term)
                },
                success: function (data) {
                    response(data);
                },
                error: function (_request, _textStatus, _error) {
                  response([]);
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
                    url: `/api/dbcopy/tables/${SrcHostDetails.name}/${SrcHostDetails.port}/${srcDBs[0]}`,
                    dataType: "json",
                    data: {
                        // Get the first database from the id_src_incl_db field
                        search: extractLast(request.term)
                    },
                    success: function (data) {
                        response(data);
                    },
                    error: function (_request, _textStatus, _error) {
                      response([]);
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
            updateTableAlert(true);
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
                    url: `/api/dbcopy/tables/${SrcHostDetails.name}/${SrcHostDetails.port}/${srcDBs[0]}`,
                    dataType: "json",
                    data: {
                        // Get the first database from the id_src_incl_db field
                        search: extractLast(request.term)
                    },
                    success: function (data) {
                        response(data);
                    },
                    error: function (_request, _textStatus, _error) {
                      response([]);
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
            updateTableAlert(true);
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

//set host target
function targetHosts(){
  let selectVal = $("#id_tgt_group_host option:selected").val();
  if(selectVal !== ''){
    $('#id_tgt_host').val(selectVal);
  }
}