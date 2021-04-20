/*jshint esversion: 6 */

(function ($) {
    "use strict";
    $(document).ready(function () {
        console.log($("#forgot-pass-link").html());
        let elem = $('.login-box form');
        if (elem.length) {
            elem.append($("#forgot-pass-link").html());
        }
    });
}) (jQuery || django.jQuery);