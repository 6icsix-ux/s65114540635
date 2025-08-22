// static/js/search_rooms.js

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
