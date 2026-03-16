fetch("plot.json")
    .then(response => response.json())
    .then(plotData => {
        Plotly.newPlot("plot", plotData.data, plotData.layout);
    });

fetch("stats.json")
    .then(response => response.json())
    .then(stats => {
        const s = stats[0];

        document.getElementById("go-hours").textContent = s.go_hours;
        document.getElementById("nogo-hours").textContent = s.nogo_hours;
        document.getElementById("go-streak").textContent = s.go_streak;
        document.getElementById("max-wave-height").textContent = s.max_wave_height;
    });