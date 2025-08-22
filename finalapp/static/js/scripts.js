function validateForm() {
    let email = document.getElementById("email").value.trim();
    let emailError = document.getElementById("email-error");
    let phone = document.getElementById("phone").value.trim();
    let phoneError = document.getElementById("phone-error");
    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirm_password").value;
    let passwordError = document.getElementById("password-error");
    let isValid = true;

    // ตรวจสอบอีเมล
    if (email === "") {
        emailError.textContent = "กรุณาระบุอีเมล";
        emailError.style.color = "red";
        isValid = false;
    } else {
        emailError.textContent = "";
    }

    // ตรวจสอบเบอร์โทรศัพท์ (ต้องเป็นตัวเลข 10 หลัก)
    if (!/^\d{10}$/.test(phone)) {
        phoneError.textContent = "กรุณากรอกหมายเลขโทรศัพท์ให้ถูกต้อง (10 หลัก)";
        phoneError.style.color = "red";
        isValid = false;
    } else {
        phoneError.textContent = "";
    }

    // ตรวจสอบว่าพาสเวิร์ดต้องตรงกัน
    if (password !== confirmPassword) {
        passwordError.textContent = "รหัสผ่านไม่ตรงกัน กรุณากรอกใหม่";
        passwordError.style.color = "red";
        isValid = false;
    } else {
        passwordError.textContent = ""; // เคลียร์ข้อความแจ้งเตือน
    }

    return isValid; // ถ้า `false` จะไม่ให้สมัคร
}

function confirmLogout() {
    return confirm("คุณแน่ใจหรือไม่ว่าต้องการออกจากระบบ ?");
}

// ตรวจสอบอีเมลซ้ำ
document.getElementById("email").addEventListener("blur", function() {
    let email = this.value.trim();
    let emailError = document.getElementById("email-error");

    if (email !== "") {
        fetch(`/check_email/?email=${email}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    emailError.textContent = "อีเมลนี้ถูกใช้ไปแล้ว กรุณาใช้อีเมลอื่น";
                    emailError.style.color = "red";
                } else {
                    emailError.textContent = "";
                }
            });
    }
});

// ตรวจสอบเบอร์โทรซ้ำ
document.getElementById("phone").addEventListener("blur", function() {
    let phone = this.value.trim();
    let phoneError = document.getElementById("phone-error");

    if (phone !== "") {
        fetch(`/check_phone/?phone=${phone}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    phoneError.textContent = "หมายเลขนี้ถูกใช้ไปแล้ว กรุณาใช้หมายเลขอื่น";
                    phoneError.style.color = "red";
                } else {
                    phoneError.textContent = "";
                }
            });
    }
});

document.getElementById("phone").addEventListener("input", function() {
    let phone = this.value.replace(/\D/g, ""); // ลบอักขระที่ไม่ใช่ตัวเลข
    if (phone.length > 10) {
        phone = phone.slice(0, 10); // จำกัดให้เหลือแค่ 10 หลัก
    }
    this.value = phone; // อัปเดตค่าในช่องกรอก
});

// ตรวจสอบพาสเวิร์ดแบบ Real-time
document.getElementById("confirm_password").addEventListener("input", function() {
    let password = document.getElementById("password").value;
    let confirmPassword = this.value;
    let passwordError = document.getElementById("password-error");

    if (password !== confirmPassword) {
        passwordError.textContent = "รหัสผ่านไม่ถูกต้อง กรุณากรอกใหม่อีกครั้ง";
        passwordError.style.color = "red";
    } else {
        passwordError.textContent = "";
    }
});

document.getElementById("searchInput").addEventListener("keyup", function() {
    let filter = this.value.toLowerCase();
    let rows = document.querySelectorAll("#roomTableBody tr");

    rows.forEach(row => {
        let roomNumber = row.querySelector(".room-number")?.textContent.toLowerCase() || "";
        let tenantName = row.querySelector(".tenant-name")?.textContent.toLowerCase() || "";
        let tenantEmail = row.querySelector(".tenant-email")?.textContent.toLowerCase() || "";

        if (roomNumber.includes(filter) || tenantName.includes(filter) || tenantEmail.includes(filter)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
});

