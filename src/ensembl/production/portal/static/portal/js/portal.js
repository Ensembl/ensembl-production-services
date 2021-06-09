/*jshint esversion: 6 */
/**
 *
 * Set of dedicated JS related to JazzMin integration into ENsembl portal.
 *
 * */
(function ($) {
    "use strict";

    $(document).ready(function () {
        let elem = $('.login-box form');
        if (elem.length) {
            elem.append($("#forgot-pass-link").html());
        }
        // DBCopy trick to select pane when pagination is used on transfer-logs
        $('#requestjob_form .nav-tabs a[href="#transferlogs-tab"]').on('shown.bs.tab', function(e) {
            $('#transferlogs-tab .paginator a.page-link').each(function (index) {
                $(this).attr('href', $(this).attr('href') + "#transferlogs-tab");
            });
        });
    });

}) (jQuery || django.jQuery);
