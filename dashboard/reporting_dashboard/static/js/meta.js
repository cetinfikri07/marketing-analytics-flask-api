$(document).ready(function () {
    const token = localStorage.getItem('token');
    const firstName = localStorage.getItem('first_name');
    const lastName = localStorage.getItem('last_name');
    if (!token) {
        // Redirect the user to the login page
        window.location.href = 'http://localhost:5000/login';
        return;
    };

    $('.text-dark').text(firstName + ' ' + lastName);

    const accountSelect = $('#account_id');
    const levelSelect = $('#level');
    const actionsSelect = $('#actions');
    const timeSeriesSelect = $('#timeSeriesSelect');
    const countrySelect = $('#countrySelect');
    const ageGenderSelect = $('#ageGenderSelect');

    const today = new Date('2023-04-06');
    const oneWeekAgo = new Date();
    oneWeekAgo.setTime(today.getTime() - (7 * 24 * 60 * 60 * 1000));

    var dateStop = today.toISOString().substring(0, 10);
    var dateStart = oneWeekAgo.toISOString().substring(0, 10);

    //load daterange picker
    $(function () {
        $('input[name="daterange"]').daterangepicker({
            opens: 'left',
            startDate: oneWeekAgo,
            endDate: today,
            showDropdowns: false,
            locale: {
                format: 'YYYY-MM-DD'
            }
        },
            async function (start, end) {
                $('section.loading').show();
                var startISO = start.toISOString().substring(0, 10);
                var endISO = end.toISOString().substring(0, 10);
                $('input[name="daterange"]').val(startISO + ' - ' + endISO);

                //get insights
                getOnLoadDataResponse = await getonLoadData();
                getOnLoadDataJson = await getOnLoadDataResponse.json();

                if (getOnLoadDataJson == 0) {

                    $('section.loading').hide();
                    alert('No data available in given dates');

                } else {
                    //get first object and write to document
                    firstObj = getOnLoadDataJson[0];
                    console.log(firstObj);
                    var accountCurrency = firstObj.account_currency
                    currencyIconElement = currencyIcon(accountCurrency);

                    //set currency icon
                    $('#currencyIcon').empty();
                    $('#currencyIcon').append(currencyIconElement);

                    $('#cpcCurrencyAccount').empty();
                    $('#cpcCurrencyAccount').append(currencyIconElement);

                    $('#cpaCurrencyIcon').empty();
                    $('#cpaCurrencyIcon').append(currencyIconElement);

                    $('#impressions').text(firstObj.impressions_sum);
                    $('#spendings').text(firstObj.total_spend_sum);
                    $('#clicks').text(firstObj.clicks_sum);
                    $('#conversions').text(firstObj[actionsSelect.val() + '_sum']);
                    $('#cpc').text(firstObj.cpc);
                    $('#cpa').text(firstObj['cpa_' + actionsSelect.val()]);
                    $('#cr').text('%' + firstObj['cr_' + actionsSelect.val()]);
                    $('#ctr').text('%' + firstObj.ctr);

                    drawLineChart(firstObj, timeSeriesSelect.val());

                    // draw map chart
                    getCountryResponse = await getCountryData();
                    getCountryJson = await getCountryResponse.json();
                    firstObj = getCountryJson[0].series;

                    drawRegionsMap(firstObj, countrySelect.val());

                    // draw age gender distribution
                    getAgeGenderResponse = await getAgeGenderData();
                    getAgeGenderDataJson = await getAgeGenderResponse.json();

                    firstObj = getAgeGenderDataJson[0].pivot_table;

                    drawMultSeries(firstObj, ageGenderSelect.val());

                    $('section.loading').hide();
                }
            }
        )
    });

    function currencyIcon(currency) {
        if (currency == 'TRY') {
            var iconElement = `<i class="fa-solid fa-turkish-lira-sign"></i>`
        } else if (currency == 'USD') {
            var iconElement = `<i class="fa-solid fa-dollar-sign"></i>`
        } else if (currency == 'EUR') {
            var iconElement = `<i class="fa-solid fa-euro-sign"></i>`
        } else {
            var iconElement = `<i class="fa-solid fa-money-bill"></i>`
        }

        return iconElement
    }

    function drawLineChart(data, series_field = 'total_spend') {
        var dataTable = new google.visualization.DataTable();
        var words = series_field.split('_');
        var capitalizedWords = words.map(word => word.charAt(0).toUpperCase() + word.slice(1));
        var fieldText = capitalizedWords.join(' ');

        dataTable.addColumn('datetime', 'Date');
        dataTable.addColumn('number', fieldText);
        dataTable.addRows(data.series.map(function (item) {
            return [new Date(item.date), item[series_field]];
        }));

        var options = {
            title: fieldText + ' by date',
            hAxis: {
                title: 'Date'
            },
            vAxis: {
                title: fieldText
            }
        };

        if ($('#line_chart').is(":hidden")) {
            $('#line_chart').show();
        };

        var chart = new google.visualization.LineChart(document.getElementById('line_chart'));
        chart.draw(dataTable, options);
    };

    function drawRegionsMap(data, label) {
        var result = data.reduce(function (accumulator, currentValue) {
            if (typeof accumulator[currentValue.country] === 'undefined') {
                accumulator[currentValue.country] = 0;
            }
            accumulator[currentValue.country] += currentValue[countrySelect.val()];
            return accumulator;
        }, {});

        result = Object.entries(result).map(([key, value]) => [key, value]);

        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', 'Country');
        dataTable.addColumn('number', label);
        dataTable.addRows(result);

        var options = {};

        var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

        chart.draw(dataTable, options);

    };


    function drawMultSeries(pivot, field) {
        if (pivot.length != 1) {
            var data = google.visualization.arrayToDataTable(pivot);

            var words = field.split('_');
            var capitalizedWords = words.map(word => word.charAt(0).toUpperCase() + word.slice(1));
            var fieldText = capitalizedWords.join(' ');

            var options = {
                title: fieldText + ' by age and gender',
                chartArea: { width: '60%' },
                hAxis: {
                    title: fieldText,
                    minValue: 0.001
                },
                vAxis: {
                    title: 'Age'
                }
            };

            var chart = new google.visualization.BarChart(document.getElementById('age_gender_div'));
            chart.draw(data, options);
        } else {
            var data = [
                ['total_spend', 'male', 'female'],
                ['18-24', 0, 0],
                ['25-34', 0, 0],
                ['45-54', 0, 0],
                ['55-64', 0, 0]
            ]


            data = google.visualization.arrayToDataTable(data);

            var chart = new google.visualization.BarChart(document.getElementById('age_gender_div'));
            chart.draw(data, options);
        };

    };

    function getAccounts() {
        var result = fetch("http://127.0.0.1:5555/meta/user-levels",
            {
                method: "POST",
                headers: {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "levelType": "account"
                })
            }
        );

        return result
    };

    function getonLoadData() {
        dateStart = $('input[name="daterange"]').val().split(' - ')[0];
        dateStop = $('input[name="daterange"]').val().split(' - ')[1];

        var params = {
            "date_start": dateStart,
            "date_stop": dateStop,
            "account_id": accountSelect.val(),
            "fields": ["impressions", "clicks", "total_spend", actionsSelect.val()],
            "series": [timeSeriesSelect.val()],
            "actions": [actionsSelect.val()],
            "kpis": ["cpc", "ctr", "cpa", "cr"],
            "level": levelSelect.val()
        };

        var result = fetch('http://127.0.0.1:5555/meta/report', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)

        });

        return result

    };

    function getCountryData() {
        dateStart = $('input[name="daterange"]').val().split(' - ')[0];
        dateStop = $('input[name="daterange"]').val().split(' - ')[1];

        var params = {
            "date_start": dateStart,
            "date_stop": dateStop,
            "account_id": accountSelect.val(),
            "series": [countrySelect.val()],
            "breakdowns": ['country'],
            "level": levelSelect.val()
        };

        var result = fetch('http://127.0.0.1:5555/meta/report', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)

        });

        return result

    };

    function getAgeGenderData() {
        dateStart = $('input[name="daterange"]').val().split(' - ')[0];
        dateStop = $('input[name="daterange"]').val().split(' - ')[1];

        var params = {
            "date_start": dateStart,
            "date_stop": dateStop,
            "account_id": accountSelect.val(),
            "series": [ageGenderSelect.val()],
            "breakdowns": ['age', 'gender'],
            "pivot": true,
            "level": levelSelect.val()
        };

        var result = fetch('http://127.0.0.1:5555/meta/report', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)

        });

        return result

    };


    async function onLoadInsights() {
        try {
            $('section.loading').show();

            await google.charts.load('current', { 'packages': ['corechart', 'line', 'geochart'] });

            //get accounts
            getAccountResponse = await getAccounts();
            getAccountJson = await getAccountResponse.json();

            getAccountJson.forEach(element => {
                var option = $('<option>');
                let levelId = Object.values(element)[0];
                let levelName = Object.values(element)[1];
                option.val(levelId);
                option.text(levelName);

                $('#account_id').append(option);
            });

            //get insights
            getOnLoadDataResponse = await getonLoadData();
            getOnLoadDataJson = await getOnLoadDataResponse.json();

            //get first object and write to document
            firstObj = getOnLoadDataJson[0];
            var accountCurrency = firstObj.account_currency
            currencyIconElement = currencyIcon(accountCurrency);

            //set currency icon 
            $('#spendingsCurrencyIcon').append(currencyIconElement);
            $('#cpcCurrencyAccount').append(currencyIconElement);
            $('#cpaCurrencyIcon').append(currencyIconElement);

            $('#impressions').text(firstObj.impressions_sum);
            $('#spendings').text(firstObj.total_spend_sum);
            $('#clicks').text(firstObj.clicks_sum);
            $('#conversions').text(firstObj[actionsSelect.val() + '_sum']);
            $('#cpc').text(firstObj.cpc);
            $('#cpa').text(firstObj['cpa_' + actionsSelect.val()]);
            $('#cr').text('%' + firstObj['cr_' + actionsSelect.val()]);
            $('#ctr').text('%' + firstObj.ctr);

            drawLineChart(firstObj, timeSeriesSelect.val());

            // draw map chart
            getCountryResponse = await getCountryData();
            getCountryJson = await getCountryResponse.json();
            firstObj = getCountryJson[0].series;

            drawRegionsMap(firstObj, countrySelect.val());

            // draw age gender distribution
            getAgeGenderResponse = await getAgeGenderData();
            getAgeGenderDataJson = await getAgeGenderResponse.json();

            firstObj = getAgeGenderDataJson[0].pivot_table;

            drawMultSeries(firstObj, ageGenderSelect.val());

            $('section.loading').hide();
        } catch (error) {
            $('section.loading').hide();
            const newRow = `
            <div class="row">
                <div class="col-6">
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        <span>To see your metrics, please register for an ad account.</span> 
                        <button type="button" class="btn btn-light" onclick="window.location.href='/settings'">Register</button>
                    </div>
                </div>
            </div>
            `
            $('.container-fluid.p-0').prepend(newRow);
        };
    };

    accountSelect.change(async function () {
        $('section.loading').show();

        //get insights
        getOnLoadDataResponse = await getonLoadData();
        getOnLoadDataJson = await getOnLoadDataResponse.json();

        //get first object and write to document
        firstObj = getOnLoadDataJson[0];
        var accountCurrency = firstObj.account_currency
        currencyIconElement = currencyIcon(accountCurrency);

        //set currency icon
        $('#spendingsCurrencyIcon').empty();
        $('#spendingsCurrencyIcon').append(currencyIconElement);

        $('#cpcCurrencyAccount').empty();
        $('#cpcCurrencyAccount').append(currencyIconElement);

        $('#cpaCurrencyIcon').empty();
        $('#cpaCurrencyIcon').append(currencyIconElement);

        $('#impressions').text(firstObj.impressions_sum);
        $('#spendings').text(firstObj.total_spend_sum);
        $('#clicks').text(firstObj.clicks_sum);
        $('#conversions').text(firstObj[actionsSelect.val() + '_sum']);
        $('#cpc').text(firstObj.cpc);
        $('#cpa').text(firstObj['cpa_' + actionsSelect.val()]);
        $('#cr').text('%' + firstObj['cr_' + actionsSelect.val()]);
        $('#ctr').text('%' + firstObj.ctr);

        // draw time series chart
        drawLineChart(firstObj, timeSeriesSelect.val());

        // get country data
        getCountryResponse = await getCountryData();
        getCountryJson = await getCountryResponse.json();
        firstObj = getCountryJson[0].series;

        //draw map chart
        drawRegionsMap(firstObj, countrySelect.val());

        // draw age gender distribution
        getAgeGenderResponse = await getAgeGenderData();
        getAgeGenderDataJson = await getAgeGenderResponse.json();

        firstObj = getAgeGenderDataJson[0].pivot_table;

        drawMultSeries(firstObj, ageGenderSelect.val());

        $('section.loading').hide();
    });

    levelSelect.change(async function () {
        $('section.loading').show();
        $('#select-level-row').remove();

        //get insights
        getOnLoadDataResponse = await getonLoadData();
        getOnLoadDataJson = await getOnLoadDataResponse.json();

        var level = levelSelect.val();
        if (level != 'account') {
            const newRow = `
            <div class="row" id= 'select-level-row'>
                <div class="col-6">
                    <div class="row">
                    <div class="col-3">
                        <h1 class="h4 mb-3">Select ${level}: </h1>
                    </div>
                    <div class="col-3">
                        <select class="form-select mb-3" id="select-level">
                        </select>
                    </div>
                </div>
            </div>
            `
            $('.container-fluid.p-0').prepend(newRow);
            levelName = level + '_name'
            levelId = level + '_id'
            getOnLoadDataJson.forEach(element => {
                var optStr = `<option>${element[levelName]}</option>`
                var opt = $(optStr);
                opt.val(element[levelId]);

                $('#select-level').append(opt);

            });
        };

        firstObj = getOnLoadDataJson[0];
        var accountCurrency = firstObj.account_currency
        currencyIconElement = currencyIcon(accountCurrency);

        //set currency icon
        $('#spendingsCurrencyIcon').empty();
        $('#spendingsCurrencyIcon').append(currencyIconElement);

        $('#cpcCurrencyAccount').empty();
        $('#cpcCurrencyAccount').append(currencyIconElement);

        $('#cpaCurrencyIcon').empty();
        $('#cpaCurrencyIcon').append(currencyIconElement);

        $('#impressions').text(firstObj.impressions_sum);
        $('#spendings').text(firstObj.total_spend_sum);
        $('#clicks').text(firstObj.clicks_sum);
        $('#conversions').text(firstObj[actionsSelect.val() + '_sum']);
        $('#cpc').text(firstObj.cpc);
        $('#cpa').text(firstObj['cpa_' + actionsSelect.val()]);
        $('#cr').text('%' + firstObj['cr_' + actionsSelect.val()]);
        $('#ctr').text('%' + firstObj.ctr);
        drawLineChart(firstObj, timeSeriesSelect.val());

        // draw map chart
        getCountryResponse = await getCountryData();
        getCountryJson = await getCountryResponse.json();
        firstObj = getCountryJson[0].series;

        drawRegionsMap(firstObj, countrySelect.val());

        // draw age gender distribution
        getAgeGenderResponse = await getAgeGenderData();
        getAgeGenderDataJson = await getAgeGenderResponse.json();

        firstObj = getAgeGenderDataJson[0].pivot_table;

        drawMultSeries(firstObj, ageGenderSelect.val());

        $('section.loading').hide();

    });

    $('body').on('change', '#select-level', async function (e) {
        $('section.loading').show();
        var level = levelSelect.val();
        var key = level + '_id';
        var id = e.target.value;

        //get insights
        getOnLoadDataResponse = await getonLoadData();
        getOnLoadDataJson = await getOnLoadDataResponse.json();

        var foundOnLoadDataObject = getOnLoadDataJson.find(item => item[key] === id);

        var accountCurrency = foundOnLoadDataObject.account_currency
        currencyIconElement = currencyIcon(accountCurrency);

        //set currency icon
        $('#spendingsCurrencyIcon').empty();
        $('#spendingsCurrencyIcon').append(currencyIconElement);

        $('#cpcCurrencyAccount').empty();
        $('#cpcCurrencyAccount').append(currencyIconElement);

        $('#cpaCurrencyIcon').empty();
        $('#cpaCurrencyIcon').append(currencyIconElement);

        $('#impressions').text(foundOnLoadDataObject.impressions_sum);
        $('#spendings').text(foundOnLoadDataObject.total_spend_sum);
        $('#clicks').text(foundOnLoadDataObject.clicks_sum);
        $('#conversions').text(foundOnLoadDataObject[actionsSelect.val() + '_sum']);
        $('#cpc').text(foundOnLoadDataObject.cpc);
        $('#cpa').text(foundOnLoadDataObject['cpa_' + actionsSelect.val()]);
        $('#cr').text('%' + foundOnLoadDataObject['cr_' + actionsSelect.val()]);
        $('#ctr').text('%' + foundOnLoadDataObject.ctr);

        drawLineChart(foundOnLoadDataObject, timeSeriesSelect.val());

        // get counry data
        getCountryResponse = await getCountryData();
        getCountryJson = await getCountryResponse.json();
        var foundCountryObject = getCountryJson.find(item => item[key] === id).series;

        drawRegionsMap(foundCountryObject, countrySelect.val());

        // draw age gender distribution
        getAgeGenderResponse = await getAgeGenderData();
        getAgeGenderDataJson = await getAgeGenderResponse.json();
        var foundAgeGenderObject = getAgeGenderDataJson.find(item => item[key] === id).pivot_table;

        drawMultSeries(foundAgeGenderObject, ageGenderSelect.val());


        $('section.loading').hide();
    });

    actionsSelect.change(async function () {
        $('section.loading').show();

        //get insights
        getOnLoadDataResponse = await getonLoadData();
        getOnLoadDataJson = await getOnLoadDataResponse.json();

        //get first object and write to document
        firstObj = getOnLoadDataJson[0];
        var accountCurrency = firstObj.account_currency
        currencyIconElement = currencyIcon(accountCurrency);

        //set currency icon
        $('#spendingsCurrencyIcon').empty();
        $('#spendingsCurrencyIcon').append(currencyIconElement);

        $('#cpcCurrencyAccount').empty();
        $('#cpcCurrencyAccount').append(currencyIconElement);

        $('#cpaCurrencyIcon').empty();
        $('#cpaCurrencyIcon').append(currencyIconElement);



        $('#impressions').text(firstObj.impressions_sum);
        $('#spendings').text(firstObj.total_spend_sum);
        $('#clicks').text(firstObj.clicks_sum);
        $('#conversions').text(firstObj[actionsSelect.val() + '_sum']);
        $('#cpc').text(firstObj.cpc);
        $('#cpa').text(firstObj['cpa_' + actionsSelect.val()]);
        $('#cr').text('%' + firstObj['cr_' + actionsSelect.val()]);
        $('#ctr').text('%' + firstObj.ctr);


        $('section.loading').hide();

    });

    timeSeriesSelect.change(async function () {
        $('section.loading').show();
        var level = levelSelect.val();

        //get insights
        getOnLoadDataResponse = await getonLoadData();
        getOnLoadDataJson = await getOnLoadDataResponse.json();

        if ($('#select-level').length) {
            let key = level + '_id';
            let id = $('#select-level').val();

            var foundTimesSeriesObject = getOnLoadDataJson.find(item => item[key] === id);
            drawLineChart(foundTimesSeriesObject, timeSeriesSelect.val());

        } else {
            var firstObj = getOnLoadDataJson[0];
            drawLineChart(firstObj, timeSeriesSelect.val());
        };

        $('section.loading').hide();

    });

    countrySelect.change(async function () {
        $('section.loading').show();
        var level = levelSelect.val();

        getCountryResponse = await getCountryData();
        getCountryJson = await getCountryResponse.json();

        if ($('#select-level').length) {
            let key = level + '_id';
            let id = $('#select-level').val();

            var foundCountryObject = getCountryJson.find(item => item[key] === id).series;
            drawRegionsMap(foundCountryObject, countrySelect.val());

        } else {
            var firstObj = getCountryJson[0].series;
            drawRegionsMap(firstObj, countrySelect.val());
        };


        $('section.loading').hide();

    });

    ageGenderSelect.change(async function () {
        $('section.loading').show();
        var level = levelSelect.val();
        getAgeGenderDataResponse = await getAgeGenderData();
        getAgeGenderDataJson = await getAgeGenderDataResponse.json();

        if ($('#select-level').length) {
            let key = level + '_id';
            let id = $('#select-level').val();

            var foundAgeGenderObject = getAgeGenderDataJson.find(item => item[key] === id).pivot_table;
            drawMultSeries(foundAgeGenderObject, ageGenderSelect.val());

        } else {
            var firstObj = getAgeGenderDataJson[0].pivot_table;
            drawMultSeries(firstObj, ageGenderSelect.val());
        };

        $('section.loading').hide();

    });


    $('#logout').click(function () {
        localStorage.removeItem('token');
        window.location.href = 'http://localhost:5000/login';
    });

    onLoadInsights();
});