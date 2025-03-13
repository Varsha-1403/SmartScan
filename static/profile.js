function calculateBMI() {
    const height = parseFloat(document.getElementById("height").value) / 100;
    const weight = parseFloat(document.getElementById("weight").value);
    const age = parseFloat(document.getElementById("age").value);
    const gender = document.getElementById("gender").value;

    if (!height || !weight || height <= 0 || weight <= 0 || !age || !gender) {
        alert("Please enter valid height, weight, age, and gender!");
        return;
    }

    const bmi = (weight / (height * height)).toFixed(2);
    document.getElementById("bmi-result").innerText = `Your BMI: ${bmi}`;

    let advice = "";
    let calories = 0, protein = 0, carbohydrates = 0;

    if (bmi < 18.5) {
        advice = "You are underweight. Focus on a calorie-dense diet.";
        calories = weight * 30;
        protein = weight * 1.2;
        carbohydrates = (calories * 0.55) / 4;
    } else if (bmi < 24.9) {
        advice = "You have a healthy weight. Maintain a balanced diet.";
        calories = weight * 25;
        protein = weight * 1;
        carbohydrates = (calories * 0.50) / 4;
    } else if (bmi < 29.9) {
        advice = "You are overweight. Focus on a calorie-controlled diet.";
        calories = weight * 20;
        protein = weight * 1.2;
        carbohydrates = (calories * 0.45) / 4;
    } else {
        advice = "You are obese. Consult a healthcare professional for guidance.";
        calories = weight * 18;
        protein = weight * 1.2;
        carbohydrates = (calories * 0.40) / 4;
    }

    document.getElementById("bmi-advice").innerText = advice;
    document.getElementById("nutrition-result").innerHTML = `
        <p>Estimated Daily Needs:</p>
        <ul>
            <li>Calories: ${calories.toFixed(2)} kcal</li>
            <li>Protein: ${protein.toFixed(2)} g</li>
            <li>Carbohydrates: ${carbohydrates.toFixed(2)} g</li>
        </ul>
    `;

    // Save BMI data to backend
    fetch("/save_bmi", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bmi, calories, protein, carbohydrates, age, gender })
    })
    .catch(error => console.error("❌ Error saving BMI data:", error));
}

function scanFromFile() {
    console.log("Hello")
    const fileInput = document.getElementById("upload-image");
    const file = fileInput.files[0];
    
    if (!file) {
        alert("Please upload a barcode image first.");
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(event) {
        const img = new Image();
        img.src = event.target.result;
        img.onload = function() {
            document.getElementById("image-preview").src = img.src;
            // Use Tesseract.js to extract barcode
            Tesseract.recognize(img, 'eng',)
                .then(({ data: { text } }) => {
                    const barcode = text.replace(/[^0-9]/g, "").trim();
                    if (barcode.length > 6) {
                        fetchProductInfo(barcode);
                    } else {
                        alert("Could not detect a valid barcode. Please try again.");
                    }
                })
                .catch(error => {
                    console.error("❌ Error extracting barcode:", error);
                    alert("Failed to extract barcode. Please try again.");
                });
        };
    };
    reader.readAsDataURL(file);
}

function fetchProductInfo(barcode) {
    if (!barcode) {
        alert("Invalid barcode. Please try again.");
        return;
    }
    
    console.log("📡 Fetching product info for barcode:", barcode);
    fetch("/process_food", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ barcode, quantity: 1 })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("❌ Failed to fetch product info.");
        }
        return response.json();
    })
    .then(data => {
        const productInfo = document.getElementById("product-info");
        productInfo.innerHTML = `
            <h3>Product Information</h3>
            <p><strong>Name:</strong> ${data.food_info.name}</p>
            <p><strong>Calories:</strong> ${data.food_info.calories.toFixed(2)} kcal</p>
            <p><strong>Protein:</strong> ${data.food_info.protein.toFixed(2)} g</p>
            <p><strong>Carbs:</strong> ${data.food_info.carbs.toFixed(2)} g</p>
            <p><strong>Ingredients:</strong> ${data.food_info.ingredients}</p>
            ${data.food_info.image ? `<img src="${data.food_info.image}" alt="Product Image" width="150">` : ""}
        `;

        const suggestionDiv = document.getElementById("product-suggestion");
        if (data.alternatives) {
            suggestionDiv.innerHTML = `
                <h3>Recommended Alternatives</h3>
                ${data.alternatives.map(item => `
                    <div class="alternative-item">
                        <p><strong>Name:</strong> ${item.product_name}</p>
                        <p><strong>Why:</strong> ${item.why}</p>
                    </div>
                `).join("")}
            `;
        } else {
            suggestionDiv.innerHTML = `<p>${data.message}</p>`;
        }

        // Display health scale visualization
        const healthScaleDiv = document.getElementById("health-scale");
        const healthScaleData = [
            {
                x: ["Calories", "Protein", "Carbs"],
                y: [data.health_scale.calories, data.health_scale.protein, data.health_scale.carbs],
                type: "bar",
                name: "Health Scale"
            }
        ];
        Plotly.newPlot(healthScaleDiv, healthScaleData, { title: "Health Scale Visualization" });
    })
    .catch(error => {
        console.error("❌ Error fetching product info:", error);
        alert("Failed to fetch product details. Please try again.");
    });
}