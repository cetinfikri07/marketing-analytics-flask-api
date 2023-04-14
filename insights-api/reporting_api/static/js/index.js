// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart','line']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(() => {
    const url = "https://eyula-reporting-api-dot-eyula-etl.ew.r.appspot.com/reporting-api/meta/get-report"
    fetch(url,{
        method:"POST",
        headers: {
            'Content-type' : 'application/json',
            'Authorization': 'Basic YWRtaW4xQGV4YW1wbGUuY29tOmFkbW9u',
            'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMTMiLCJleHAiOjE2NzkwMzk3Nzd9.ak4FPiBbLBkCWcnmDIYzaWqi0jmRMcvZWL8CsHYF1Yc',
    
        },
        body: JSON.stringify({
            "date_start": "2023-02-01",
            "date_stop": "2023-03-15",
            "account_id": "525510428828068",
            "fields":["impressions","clicks","total_spend"],
            "series":["total_spend"],
            "actions":["video_view"],
            "kpis":["cpc","ctr","cpa","cr"],
            "level": "ad"
        }),
    })
    .then(response => response.json())
    .then(res => {
        res = res.find(data => data.ad_id === '23851706892930348');
        console.log(res);    
        drawChart(res);
    }).catch(error => {
        console.log(error)
    });
});

function drawChart(data){
    var dataTable = new google.visualization.DataTable();

    dataTable.addColumn('date','Date');
    dataTable.addColumn('number','Total Spend');

    dataTable.addRows(data.series.map(function(item) {
        return [new Date(item.date), item.total_spend];
    }));

    var options = {
        title: 'Total Spend by date',
        hAxis: {
            title: 'Date'
        },
        
        vAxis: {
            title: 'Total Spend'
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(dataTable, options);
};






