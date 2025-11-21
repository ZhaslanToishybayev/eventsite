$(document).ready(function() {
    "use strict";
    let $start_datetime = $("#id_start_datetime");
    let timeStartInLocalFormat = $start_datetime.attr('value');
    let [day_start_datetime, month_start_datetime, year_start_datetime] = timeStartInLocalFormat.split(".");
    let formattedStartDate = `${year_start_datetime}-${month_start_datetime}-${day_start_datetime}`;
    $start_datetime.attr('value', formattedStartDate);

    let $end_datetime = $("#id_end_datetime");
    let timeEndInLocalFormat = $end_datetime.attr('value');
    let [day_end_datetime, month_end_datetime, year_end_datetime] = timeEndInLocalFormat.split(".");
    let formattedEndDate = `${year_end_datetime}-${month_end_datetime}-${day_end_datetime}`;
    $end_datetime.attr('value', formattedEndDate);
});