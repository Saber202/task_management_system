// التعامل مع نموذج الاشتراك
document.getElementById("subscribe-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    // جمع البيانات من النموذج
    const start_date = document.getElementById("start_date").value;
    const frequency = document.getElementById("frequency").value;
    const report_time = document.getElementById("report_time").value;

    const data = {
        start_date: start_date,
        frequency: frequency,
        report_time: parseInt(report_time)
    };

    // إرسال الطلب إلى API الاشتراك
    fetch("/subscription/subscribe", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`  // توكن المستخدم
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);  // عرض رسالة الاشتراك الناجح
        } else if (data.error) {
            alert(data.error);  // عرض أي أخطاء إذا حدثت
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
});

// التعامل مع زر إلغاء الاشتراك
document.getElementById("unsubscribe-button").addEventListener("click", function() {
    // إرسال طلب لإلغاء الاشتراك
    fetch("/subscription/unsubscribe", {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`  // توكن المستخدم
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);  // عرض رسالة إلغاء الاشتراك الناجح
        } else if (data.error) {
            alert(data.error);  // عرض أي أخطاء إذا حدثت
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
});
