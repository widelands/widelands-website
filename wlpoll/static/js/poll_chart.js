// Draws the results of a poll as a pie chart with Chart.js.
//
// Expects the poll as JSON in <script id="pollData"> (rendered by the
// display_poll template tag) and a <canvas id="pollChart"> inside a
// container with a fixed height.

document.addEventListener('DOMContentLoaded', function() {
    const data = document.getElementById('pollData');
    const canvas = document.getElementById('pollChart');
    if (!data || !canvas) {
        return;
    }
    const poll = JSON.parse(data.textContent);
    const labels = poll.choices.map(function(c) { return c[0]; });
    const votes = poll.choices.map(function(c) { return c[1]; });
    const total = votes.reduce(function(a, b) { return a + b; }, 0);
    const colors = [
        '#d4a017', '#3d8b3d', '#8b5a2b', '#c0392b',
        '#2e6f95', '#e07b39', '#6c4f8a', '#7f8c5a',
    ];

    function describe(count) {
        const percent = total ? (100 * count / total).toFixed(1) : '0.0';
        return count + (count === 1 ? ' vote' : ' votes') + ' (' + percent + ' %)';
    }

    // Chart.js draws nothing for a pie without votes, so say so instead.
    const noVotes = {
        id: 'noVotes',
        afterDraw: function(chart) {
            if (total) {
                return;
            }
            const area = chart.chartArea;
            const ctx = chart.ctx;
            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.font = '16px sans-serif';
            ctx.fillStyle = '#666';
            ctx.fillText('No votes yet',
                (area.left + area.right) / 2, (area.top + area.bottom) / 2);
            ctx.restore();
        },
    };

    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: votes,
                backgroundColor: labels.map(function(_, i) {
                    return colors[i % colors.length];
                }),
                borderColor: '#fff',
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: poll.name,
                    font: { size: 18, weight: 'normal' },
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        generateLabels: function(chart) {
                            const items = Chart.overrides.pie.plugins.legend.labels.generateLabels(chart);
                            items.forEach(function(item) {
                                item.text = labels[item.index] + ': ' + describe(votes[item.index]);
                            });
                            return items;
                        },
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return describe(context.parsed);
                        },
                    },
                },
            },
        },
        plugins: [noVotes],
    });
});
