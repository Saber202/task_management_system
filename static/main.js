const BASE_URL = "http://127.0.0.1:5000"; // تأكد من صحة الرابط

// Event listener for Sign Up
document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault(); // منع إعادة تحميل الصفحة

    // جمع البيانات من الحقول
    const username = document.getElementById("signup-username").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;

    try {
        const response = await fetch(`${BASE_URL}/signup`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert("Sign Up Successful! You can now Sign In.");
            document.getElementById("signup-form").reset();
        } else {
            alert(`Error: ${data.error || "Unknown error occurred"}`);
        }
    } catch (error) {
        console.error("Error during Sign Up:", error);
        alert("An error occurred while signing up. Please try again.");
    }
});

// Event listener for Sign In
document.getElementById("signin-form").addEventListener("submit", async (event) => {
    event.preventDefault(); // منع إعادة تحميل الصفحة

    // جمع البيانات من الحقول
    const email = document.getElementById("signin-email").value;
    const password = document.getElementById("signin-password").value;

    try {
        const response = await fetch(`${BASE_URL}/signin`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert(`Sign In Successful! Token: ${data.access_token}`);
            document.getElementById("signin-form").reset();
        } else {
            alert(`Error: ${data.error || "Unknown error occurred"}`);
        }
    } catch (error) {
        console.error("Error during Sign In:", error);
        alert("An error occurred while signing in. Please try again.");
    }
});
