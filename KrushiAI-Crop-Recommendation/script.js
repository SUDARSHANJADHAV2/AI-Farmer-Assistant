document.getElementById('recommendation-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        const predictionResult = document.getElementById('prediction-result');
        const cropInfo = document.getElementById('crop-info');

        if (result.error) {
            predictionResult.innerHTML = `<p style=\"color: red;\">${result.error}</p>`;
            cropInfo.innerHTML = '';
        } else {
            predictionResult.innerHTML = `🌱 ${result.prediction}`;
            let html = `<p>${result.info}</p>`;
            if (Array.isArray(result.top_3)) {
                const items = result.top_3.map((r, idx) => `<li><strong>${idx+1}. ${r.label}</strong> — ${(r.probability*100).toFixed(1)}%<br/><small>${r.info}</small></li>`).join('');
                html += `<h3>Top recommendations</h3><ol>${items}</ol>`;
            }
            cropInfo.innerHTML = html;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const predictionResult = document.getElementById('prediction-result');
        predictionResult.innerHTML = `<p style=\"color: red;\">An error occurred while getting the recommendation.</p>`;
    });
});
