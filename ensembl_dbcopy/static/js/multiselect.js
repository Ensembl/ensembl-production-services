// Variable to collect source host endpoint data
var SrcHostResults;
// Variable containing the selected host server details
var SrcHostDetails;

// Split a string according to a delimiter
function split(val) {
    return val.split(/,\s*/);
}

// Get the last item from a list
function extractLast(term) {
    return split(term).pop();
}

// Autocomplete for the source host field
$(function () {
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
                        return item.name + ":" + item.port;
                    }));
                }
            });
        },
        minLength: 1,
        select: function (event, ui) {
            $.map(SrcHostResults, function (item) {
                var curr_item = item.name + ":" + item.port
                if (ui.item.value == curr_item) {
                    //Compare list of hosts from the endpoint stored in SrcHostResults variables with the host selected by the user
                    // Store the server details into the SrcHostDetails variable
                    SrcHostDetails = item;
                }
            })
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
                        return item.name + ":" + item.port;
                    }));
                }
            });
        },
        minLength: 1,
        focus: function () {
            return false;
        },
        select: function (event, ui) {
            // Code to allow multiple items to be selected in the autocomplete
            var terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push("");
            this.value = terms.join(",");
            return false;
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
                    user: SrcHostDetails.mysql_user,
                    database: extractLast(request.term)
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
            // Code to allow multiple items to be selected in the autocomplete
            var terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push("");
            this.value = terms.join(",");
            return false;
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
                    user: SrcHostDetails.mysql_user,
                    database: extractLast(request.term)
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
            // Code to allow multiple items to be selected in the autocomplete
            var terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push("");
            this.value = terms.join(",");
            return false;
        }
    });
});
// Autocomplete for the list of tables to copy
$(function () {
    $("#id_src_incl_tables").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/api/dbcopy/tables",
                dataType: "json",
                data: {
                    host: SrcHostDetails.name,
                    port: SrcHostDetails.port,
                    user: SrcHostDetails.mysql_user,
                    // Get the first database from the id_src_incl_db field
                    database: $("#id_src_incl_db").val().split(",")[0],
                    table: extractLast(request.term)
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
            // Code to allow multiple items to be selected in the autocomplete
            var terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push("");
            this.value = terms.join(",");
            return false;
        }
    });
});
// Autocomplete for the list of tables to skip
$(function () {
    $("#id_src_skip_tables").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/api/dbcopy/tables",
                dataType: "json",
                data: {
                    host: SrcHostDetails.name,
                    port: SrcHostDetails.port,
                    user: SrcHostDetails.mysql_user,
                    // Get the first database from the id_src_incl_db field
                    database: $("#id_src_incl_db").val().split(",")[0],
                    table: extractLast(request.term)
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
            // Code to allow multiple items to be selected in the autocomplete
            var terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push("");
            this.value = terms.join(",");
            return false;
        }
    });
});