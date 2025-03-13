// Load User Profile Data
function loadProfile() {
    let userData = JSON.parse(localStorage.getItem("userProfile"));
    if (userData) {
        document.getElementById("user-name").innerText = userData.name;
        document.getElementById("user-age").innerText = userData.age;
        document.getElementById("user-gender").innerText = userData.gender;
        document.getElementById("user-height").innerText = userData.height;
        document.getElementById("user-weight").innerText = userData.weight;
        document.getElementById("profile-section").classList.remove("hidden");
    } else {
        alert("No user data found. Please complete your profile first.");
    }
}

// BMI Calculation (Reused)
function calculateBMI() {
    let userData = JSON.parse(localStorage.getItem("userProfile"));
    if (userData) {
        let heightM = userData.height / 100;
        let bmi = (userData.weight / (heightM * heightM)).toFixed(2);
        alert(`Your BMI is ${bmi}`);
    } else {
        alert("Enter your profile details first.");
    }
}

// Placeholder Functions
function showHealthStatus() {
    alert("Health Status feature coming soon!");
}

function showNutritionLevels() {
    alert("Nutrition Levels feature coming soon!");
}

// Barcode Scanner Functionality (Reused)
function startScan() {
    Quagga.init({
        inputStream: { type: "LiveStream", target: document.querySelector("#scanner") },
        decoder: { readers: ["ean_reader"] }
    }, function (err) {
        if (err) { console.error(err); return; }
        Quagga.start();
    });
}

// Image Upload for Barcode
function scanFromFile() {
    let file = document.getElementById("upload-image").files[0];
    let reader = new FileReader();
    reader.onload = function (event) {
        document.getElementById("image-preview").src = event.target.result;
    };
    reader.readAsDataURL(file);
}
