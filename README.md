

# **Smart Scan - A Nutrition and Health Management System**

## **Overview**
Smart Scan is a web-based application designed to help users manage their nutrition and health effectively. It provides tools to calculate BMI, recommend healthier food alternatives, track consumed foods, and offer tailored recommendations for older adults. The app uses the **Open Food Facts API** to fetch food data dynamically and provides a user-friendly interface for seamless interaction.

---

## **Features**
1. **BMI Calculator**:
   - Calculates BMI based on user inputs (weight, height, age, gender, and activity level).
   - Provides health recommendations based on BMI category (underweight, normal, overweight, obese).

2. **Food Scanning and Alternatives**:
   - Allows users to scan barcodes or search for food items to get nutritional information.
   - Recommends healthier alternatives based on user preferences and health goals.

3. **Nutrition Tracking**:
   - Tracks consumed foods and displays nutritional data (calories, protein, carbs, etc.) on the Nutrition Page.

4. **Older Adults Section**:
   - Provides specialized recommendations for older adults (age 50+) to improve their health and well-being.

5. **Dynamic Recommendations**:
   - Uses the **Open Food Facts API** to fetch healthy food recommendations dynamically.

---

## **Technologies Used**
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: LocalStorage (temporary data storage)
- **APIs**: Open Food Facts (for food data)
- **Tools**: Visual Studio Code, Git, Live Server (for local testing)

---

## **Challenges Faced**
1. **API Dependency**:
   - The app relies heavily on external APIs (e.g., Open Food Facts). If the API is down or changes its structure, the app may not function properly.

2. **CORS Issues**:
   - While testing locally, the browser blocked API requests due to CORS restrictions. This was resolved by using a local development server (e.g., Live Server).

3. **Limited Food Database**:
   - The Open Food Facts API may not have data for all food items, especially regional or niche products.

4. **Error Handling**:
   - Implementing robust error handling to manage cases where the API fails or user inputs are invalid was challenging.

5. **Responsive Design**:
   - Ensuring the app works seamlessly on both desktop and mobile devices required careful planning and testing.

---

## **Setup Instructions**
Follow these steps to set up and run the project locally:

### **Prerequisites**
- A modern web browser (e.g., Chrome, Firefox, Edge).
- A code editor (e.g., Visual Studio Code).
- Node.js (optional, for running a local server).

### **Steps**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/smart-scan.git
   cd smart-scan
   ```

2. **Open the Project**:
   - Open the project folder in your code editor.

3. **Run the App**:
   - Use a local development server (e.g., Live Server in VS Code) to run the app.
   - Alternatively, open the `index.html` file directly in your browser.

4. **Test the App**:
   - Use the BMI calculator, search for food items, and explore the recommendations.

---

## **How It Works**
1. **BMI Calculation**:
   - The app calculates BMI using the formula:
     \[
     \text{BMI} = \frac{\text{Weight (kg)}}{\text{Height (m)}^2}
     \]
   - It also estimates body fat percentage and daily caloric needs using the Harris-Benedict equation.

2. **Fetching Food Data**:
   - The app uses the Open Food Facts API to fetch food data dynamically. For example:
     ```javascript
     const apiUrl = `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(foodName)}&json=1&page_size=10`;
     const response = await fetch(apiUrl);
     const data = await response.json();
     ```

3. **Filtering and Sorting**:
   - The app filters out unhealthy foods (e.g., high sugar, low fiber) and sorts the results based on the user’s BMI and nutritional goals.

4. **Tracking Consumed Foods**:
   - Consumed foods are saved in `localStorage` and displayed on the Nutrition Page.

---

## **Future Scope**
1. **Backend Integration**:
   - Integrate a backend (e.g., Flask, Node.js) to save user data securely.

2. **User Authentication**:
   - Add user authentication to differentiate between multiple users and provide personalized recommendations.

3. **Meal Planning**:
   - Introduce a feature to plan daily meals based on nutritional goals.

4. **Gamification**:
   - Reward users for achieving health goals (e.g., consuming a certain number of healthy foods).

5. **Multilingual Support**:
   - Make the app accessible to non-English speakers.

---

## **Contributing**
Contributions are welcome! If you’d like to contribute to this project, follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and test thoroughly.
4. Submit a pull request with a detailed description of your changes.

---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**
- **Open Food Facts**: For providing free and open-source food data.
- **Edamam**: For inspiration on nutritional recommendations.
- **Stack Overflow**: For helping resolve technical challenges.

---

## **Contact**
For any questions or feedback, feel free to reach out:
- **Name**:Indugu Varshitha
- **Email**: ivarshitha3@gmail.com
- **GitHub**: https://github.com/Varsha-1403
