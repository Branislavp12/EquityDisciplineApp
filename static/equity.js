// Slovensky komentár: klientský skript pre vykresľovanie grafu a spracovanie obchodov
let chart;
let equityHistory = [];
let pending = null; // dočasný obchod

function initChart(data) {
    equityHistory = data;
    const ctx = document.getElementById('equityChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((_, i) => i),
            datasets: [{
                label: 'Equity',
                data: data,
                borderColor: 'blue',
                fill: false
            }]
        }
    });
}

document.getElementById('tradeForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const risk = parseFloat(document.getElementById('risk').value);
    const reward = parseFloat(document.getElementById('reward').value);
    const lastEq = equityHistory[equityHistory.length - 1];
    // vykreslíme vetvy
    chart.data.labels.push(chart.data.labels.length);
    chart.data.datasets.push({
        label: 'Win',
        data: [...equityHistory, lastEq + reward],
        borderColor: 'green',
        fill: false,
        borderDash: [5,5]
    });
    chart.data.datasets.push({
        label: 'Loss',
        data: [...equityHistory, lastEq - risk],
        borderColor: 'red',
        fill: false,
        borderDash: [5,5]
    });
    chart.update();
    pending = { risk, reward };
    document.getElementById('resultButtons').style.display = 'block';
});

document.getElementById('winBtn').addEventListener('click', function () {
    finalizeTrade(1);
});

document.getElementById('lossBtn').addEventListener('click', function () {
    finalizeTrade(-1);
});

function finalizeTrade(result) {
    if (!pending) return;
    const form = new URLSearchParams();
    form.append('risk', pending.risk);
    form.append('reward', pending.reward);
    form.append('result', result);
    fetch('/trade', {
        method: 'POST',
        body: form,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).then(r => r.json()).then(data => {
        equityHistory = data.equity;
        chart.data.labels = equityHistory.map((_, i) => i);
        chart.data.datasets = [{
            label: 'Equity',
            data: equityHistory,
            borderColor: 'blue',
            fill: false
        }];
        chart.update();
        pending = null;
        document.getElementById('resultButtons').style.display = 'none';
        document.getElementById('tradeForm').reset();
    });
}
