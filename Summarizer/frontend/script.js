document.addEventListener("DOMContentLoaded", function() {
    const API_URL = window.location.origin || "http://127.0.0.1:5000";

    // 📄 Upload PDF
    document.getElementById("uploadBtn").addEventListener("click", async () => {
        const file = document.getElementById("fileInput").files[0];
        const status = document.getElementById("uploadStatus");
        if (!file) {
            status.textContent = "⚠️ Please select a PDF file first.";
            status.style.color = "red";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        status.textContent = "⏳ Uploading and extracting text...";
        status.style.color = "gray";

        try {
            const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
            const data = await res.json();
            if (data.text) {
                document.getElementById("extractedText").value = data.text;
                status.textContent = "✅ Text extracted successfully!";
                status.style.color = "green";
            } else throw new Error(data.error || "Extraction failed.");
        } catch (err) {
            status.textContent = `❌ ${err.message}`;
            status.style.color = "red";
        }
    });

    // 🧠 Summarize Button: Generates Summary ONLY (No Metrics Display)
    document.getElementById("summarizeBtn").addEventListener("click", async () => {
        const text = document.getElementById("extractedText").value.trim();
        const model = document.getElementById("modelSelect").value;
        const output = document.getElementById("summaryOutput");
        const loading = document.getElementById("loading");
        const metricsDiv = document.getElementById("singleModelMetrics"); 
        
        if (!text) {
            output.textContent = "⚠️ Please upload or enter text first.";
            return;
        }

        output.textContent = "";
        metricsDiv.innerHTML = "";
        loading.classList.remove("hidden");
        document.getElementById("analyzerSection").classList.add("hidden"); 
        loading.textContent = "⏳ Generating summary...";

        try {
            const res = await fetch(`${API_URL}/summarize`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text, model }),
            });

            const data = await res.json();
            loading.classList.add("hidden");
            loading.textContent = "⏳ Processing..."; 

            if (data.summary) {
                output.textContent = data.summary;
            } else {
                output.textContent = `❌ ${data.error || "Error during summarization"}`;
            }
            metricsDiv.innerHTML = "";
        } catch (err) {
            loading.classList.add("hidden");
            output.textContent = `⚠️ ${err.message}`;
            metricsDiv.innerHTML = "";
        }
    });

    // 📊 Compare All Models Button
    document.getElementById("compareAllBtn").addEventListener("click", async () => {
        const text = document.getElementById("extractedText").value.trim();
        const loading = document.getElementById("loading");
        const analyzerSection = document.getElementById("analyzerSection");
        const summaryOutput = document.getElementById("summaryOutput"); 
        
        if (!text) {
            alert("⚠️ Please upload or enter text first.");
            return;
        }
        
        loading.classList.remove("hidden");
        analyzerSection.classList.add("hidden"); 
        loading.textContent = "⏳ Running 3 models and comparative analysis...";
        
        // Clear previous single metrics
        summaryOutput.textContent = ""; 
        document.getElementById("singleModelMetrics").innerHTML = "";

        try {
            const res = await fetch(`${API_URL}/compare_models_full`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });
            
            const data = await res.json();
            loading.classList.add("hidden");
            
            if (data.results) {
                renderComparisonDashboard(data.results, summaryOutput); 
                document.getElementById("analyzerSection").classList.remove("hidden"); 
                analyzerSection.scrollIntoView({ behavior: "smooth" });
            } else {
                alert(data.error || "Comparison failed. Check console for details.");
            }
        } catch (err) {
            loading.classList.add("hidden");
            alert(`⚠️ ${err.message}`);
        }
    });


    // Utility function to display single model metrics (Only for reference)
    function displaySingleModelMetrics(metrics, targetDiv) {
        // This function is present but no longer called by the summarizeBtn.
        const entityTotal = Number(metrics.retention_data.entity_count_total) || 0; 
        const entityRetained = Number(metrics.retention_data.entity_count_retained) || 0;
        const retentionPct = entityTotal > 0 ? ((entityRetained / entityTotal) * 100).toFixed(1) : 'N/A';
        
        const modelName = document.getElementById("modelSelect").options[document.getElementById("modelSelect").selectedIndex].text;
        const readabilityRounded = metrics.readability_grade ? metrics.readability_grade.toFixed(1) : 'N/A';
        
        targetDiv.innerHTML = `
            <h4 style="margin-top: 15px;">Analysis Metrics</h4>
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="background-color: #f1f3f6;">
                        <th style="padding: 8px; border: 1px solid #ddd;">Model Name</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Accuracy (Key Fact Retention)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="font-weight: bold;">
                        <td style="padding: 8px; border: 1px solid #ddd;">${modelName}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${retentionPct}%</td>
                    </tr>
                </tbody>
            </table>
            
            <p style="margin-top: 10px; font-size: 0.9em;">
                Compression: **${(100 - metrics.information_density).toFixed(1)}%** (Readability Grade: ${readabilityRounded})
            </p>
        `;
    }


    // Function to render the comparison bar graph (used by compareAllBtn)
    let comparisonChart = null; 
    function renderComparisonDashboard(results, summaryOutputElement) { 
        const ctx = document.getElementById("comparisonChart").getContext("2d");
        
        // 1. Calculate scores and find the best model
        let bestModel = { model: '', score: -1, index: -1, summary: '' };
        let allZeroAccuracy = true; 

        const labels = results.map(r => r.model.toUpperCase());
        const retentionScores = results.map((r, index) => {
            const entityTotal = Number(r.metrics.retention_data.entity_count_total) || 0;
            const entityRetained = Number(r.metrics.retention_data.entity_count_retained) || 0;

            const score = entityTotal > 0 ? (entityRetained / entityTotal) * 100 : 0;
            
            if (score > 0) allZeroAccuracy = false; 

            if (score > bestModel.score) {
                bestModel = { model: r.model.toUpperCase(), score: score, index: index, summary: r.summary };
            }
            return score;
        });
        
        const readabilityScores = results.map(r => r.metrics ? r.metrics.readability_grade : 15);
        
        
        // **STEP 1: DISPLAY ALL SUMMARIES IN MAIN BOX (Cleaned Accuracy Line)**
        let allSummariesHtml = 'Summary Comparison:';

        results.forEach(r => {
            const isBest = r.model.toUpperCase() === bestModel.model && !allZeroAccuracy;
            
            // ✅ FIX: Only display the accuracy percentage if it's NOT allZeroAccuracy
            const accuracyLine = allZeroAccuracy 
                ? '' // Empty string if all are zero
                : ` (Accuracy: ${r.metrics.retention_data.entity_count_total > 0 ? (r.metrics.retention_data.entity_count_retained / r.metrics.retention_data.entity_count_total * 100).toFixed(1) + '%' : 'N/A'})`;

            allSummariesHtml += `
                \n\n--- ${isBest ? '🏆 BEST MODEL' : 'MODEL'} ---
                \n${r.model.toUpperCase()}${accuracyLine}
                \n${r.summary || 'Error: Could not generate summary.'}
                \n--------------------
            `;
        });
        
        summaryOutputElement.textContent = allSummariesHtml.trim();
        
        
        // 2. Apply conditional styling for the best model's bar
        const backgroundColors = retentionScores.map((score, index) => 
            index === bestModel.index && !allZeroAccuracy ? "rgba(40, 167, 69, 0.9)" : "rgba(0, 123, 255, 0.7)" 
        );


        // Destroy existing chart instance if it exists
        if (comparisonChart) {
            comparisonChart.destroy();
        }
        
        comparisonChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Key Entity Retention (%) (Accuracy)",
                        data: retentionScores,
                        backgroundColor: backgroundColors, 
                        yAxisID: 'y_retention',
                    },
                    {
                        label: "Readability (F-K Grade Level)",
                        data: readabilityScores,
                        backgroundColor: "rgba(108, 117, 125, 0.4)", 
                        yAxisID: 'y_readability',
                    }
                ],
            },
            options: {
                responsive: true,
                scales: {
                    y_retention: {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: true,
                        max: 100,
                        title: { display: true, text: 'Accuracy: Entity Retention (%)' } 
                    },
                    y_readability: {
                        type: 'linear',
                        position: 'right',
                        grid: { drawOnChartArea: false }, 
                        title: { display: true, text: 'Readability (Grade Level)' }
                    }
                },
                plugins: {
                    title: { display: true, text: 'Model Performance Comparison' },
                    legend: { position: 'top' }
                }
            }
        });

        // 3. Display Comparison Metrics Table ONLY IF ACCURACY IS > 0
        const comparisonTableDiv = document.getElementById("comparisonTable");

        if (!allZeroAccuracy) {
            // Add the Best Performer message
            let dashboardContent = `
                <h3 style="color: #1e7e34;">🏆 Best Performer: ${bestModel.model} 
                <span style="font-size: 0.8em; font-weight: normal;">(Accuracy: ${bestModel.score.toFixed(1)}%)</span>
                </h3>
                <p>This model retained the highest percentage of critical legal facts. Scroll down for the detailed comparison chart.</p>
            `;
            
            // Add the Comparison Metrics Table (HTML)
            const tableHtml = results.map(r => {
                const entityTotal = Number(r.metrics.retention_data.entity_count_total) || 0;
                const entityRetained = Number(r.metrics.retention_data.entity_count_retained) || 0;
                const score = entityTotal > 0 ? (entityRetained / entityTotal) * 100 : 0;
                
                const isBest = r.model.toUpperCase() === bestModel.model;
                const rowStyle = isBest ? 'background-color: #e6ffed; font-weight: bold;' : '';
                const accuracyText = entityTotal > 0 ? score.toFixed(1) + '%' : 'N/A';

                return `
                    <tr style="${rowStyle}">
                        <td style="padding: 8px; border: 1px solid #ddd;">${r.model.toUpperCase()}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${accuracyText}</td>
                    </tr>
                `;
            }).join('');

            dashboardContent += `
                <h4 style="margin-top: 20px;">Comparison Metrics</h4>
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr style="background-color: #f1f3f6;">
                            <th style="padding: 8px; border: 1px solid #ddd;">Model Name</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">Accuracy (Key Fact Retention)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableHtml}
                    </tbody>
                </table>
            `;
            comparisonTableDiv.innerHTML = dashboardContent;
        } else {
            // ✅ FIX: If all accuracy is 0%, clear the comparison metrics area entirely.
            comparisonTableDiv.innerHTML = '';
        }

    }

    // 💬 Chatbot
    document.getElementById("chatBtn").addEventListener("click", async () => {
        const input = document.getElementById("chatInput").value.trim();
        const responseBox = document.getElementById("chatResponse");
        if (!input) {
            responseBox.textContent = "⚠️ Please enter your question.";
            return;
        }

        responseBox.textContent = "⏳ Thinking...";
        try {
            const res = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: input }),
            });
            const data = await res.json();
            responseBox.textContent = data.response || `❌ ${data.error || "Chat failed"}`;
        } catch (err) {
            responseBox.textContent = `⚠️ ${err.message}`;
        }
    });

    // Sidebar navigation
    document.querySelectorAll(".sidebar a").forEach(link => {
        link.addEventListener("click", e => {
            e.preventDefault();
            document.querySelectorAll(".sidebar a").forEach(a => a.classList.remove("active"));
            link.classList.add("active");
            const section = document.querySelector(link.getAttribute("href"));
            section.scrollIntoView({ behavior: "smooth" });
        });
    });
});

