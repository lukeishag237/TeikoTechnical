// chart.js loader for Flask
// This simply loads Chart.js from CDN so you can reference /static/chart.js

const script = document.createElement("script");
script.src = "https://cdn.jsdelivr.net/npm/chart.js";
document.head.appendChild(script);
