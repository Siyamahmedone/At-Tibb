// Layout Script

// Load data from localStorage
// Load Doctor Info
const doctorStored = localStorage.getItem("doctorRow");
let doctorRow = null;
if (doctorStored) {
    doctorRow = JSON.parse(doctorStored);
    console.log("Loaded doctorRow:", doctorRow);
}
// Load Clinic info
const clinicStored = localStorage.getItem("clinicRow");
let clinicRow = null;
if (clinicStored) {
    clinicRow = JSON.parse(clinicStored);
    console.log("Loaded clinicRow:", clinicRow);
}


// Initial Setup of layout after DOM
document.addEventListener("DOMContentLoaded", function() {
    // ---Navigation-Bar---
    // get current path
    const path = window.location.pathname;
    // select all nav links
    const navLinks = document.querySelectorAll(".navbar-nav .nav-link");
    navLinks.forEach(link => {
        // remove existing active class if any
        link.classList.remove("active");
        // if the href matches the current path
        if (link.getAttribute("href") === path) {
            link.classList.add("active");
        }
    });

    // ---Flash message---
    // Auto-dismiss after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }, 5000);
    });

    // ---Header-Row---
    // For general page
    // Set doctor Info
    if (doctorRow) {
        safeSetText("doctor-name", doctorRow.doctor_name);
        safeSetText("qualification", doctorRow.qualification);
        safeSetText("department", doctorRow.department);
        safeSetText("registration", doctorRow.registration);
    }
    // Set clinic Info
    if (clinicRow) {
        safeSetText("clinic-name", clinicRow.clinic_name)
        safeSetText("address", clinicRow.address)
        safeSetText("contact", clinicRow.contact)
        safeSetText("email", clinicRow.email)
    }

    // For Account page(Changing information)
    // Set doctor Info
    if (doctorRow) {
        safeSetValue("doctor-name", doctorRow.doctor_name);
        safeSetValue("qualification", doctorRow.qualification);
        safeSetValue("department", doctorRow.department);
        safeSetValue("registration", doctorRow.registration);
    }
    // Set clinic Info
    if (clinicRow) {
        safeSetValue("clinic-name", clinicRow.clinic_name)
        safeSetValue("address", clinicRow.address)
        safeSetValue("contact", clinicRow.contact)
        safeSetValue("email", clinicRow.email)
    }

    // Set today's date
    setTodayDate("day", "month", "year");

    // Call textarea resizing function
    initAutoResize();
});


// Helper functions
// Safe-set-up function
function safeSetText(id, text, fallback = "—") {
    const el = document.getElementById(id);
    if (el) el.textContent = text && text.trim() ? text : fallback;
}
function safeSetValue(id, text) {
    const el = document.getElementById(id);
    if (el) el.value = text;
}

// Date function
function setTodayDate(dayId, monthId, yearId) {
    const today = new Date();
    safeSetValue(dayId, String(today.getDate()).padStart(2, "0"));
    safeSetValue(monthId, String(today.getMonth() + 1).padStart(2, "0"));
    safeSetValue(yearId, today.getFullYear());
}


// Clear localStorage (with 1sec delay if account to prevent delet before submit)
function clearData(name) {
    if (name === 'all') {
        ["medData", "doctorRow", "clinicRow"].forEach(key => {
            if (localStorage.getItem(key)) {
                localStorage.removeItem(key);
            }
        });
        console.log("Cleared: all");
    }
    else if (name === 'account') {
        setTimeout(() => {
            ["doctorRow", "clinicRow"].forEach(key => {
                if (localStorage.getItem(key)) {
                    localStorage.removeItem(key);
                }
            });
            console.log("Cleared: account");
        }, 1000); // 1 second delay
    }
}



// Auto-Resizing function for textarea
function initAutoResize(root = document) {
  const areas = root.querySelectorAll("textarea.expand");

  areas.forEach((ta) => {
    const resize = () => {
      ta.style.height = "auto";
      ta.style.height = ta.scrollHeight + "px";
    };

    // keep the UI clean
    ta.style.overflowY = "hidden";

    // initial sizing (for prefilled values)
    requestAnimationFrame(resize);

    // resize on input
    ta.addEventListener("input", resize);
  });
}


// GoToLink on Click function
function goToLink(row) {
    // get ID from the first <td>
    let id = row.cells[0].innerText.trim();

    // redirect to /view?id=...
    window.location.href = `/view?id=${id}`;
}


// AJAX query for register usernames
async function checkUserName(e) {
    let e_val = e.value
    if (e_val) {
        // Make a async query to fetch data
        let response = await fetch(`/users?name=${encodeURIComponent(e_val)}`);
        let results = await response.json();

        // Get feedback element
        const feedback = document.getElementById("username-feedback");
        feedback.textContent = results["msg"];
    }
    else {
        document.getElementById("username-feedback").textContent = '';
    }
}


// AJAX query's for search tab
async function queryName(e) {
    // Get value of focused element(input value)
    let e_val = e.value
    let type = e.id;
    let base_val = e_val; // here element itself base
    // If base.value present
    if (base_val) {
        // Make a async query to fetch data
        let response = await fetch(`/query?value=${encodeURIComponent(base_val)}&type=${encodeURIComponent(type)}`);
        let results = await response.json();
        // prepare HTML for datalist
        let html = '';
        for (let row of results) { // here row is [{},{}...]
            html += `<option value="${row[`${type}`]}">`; // row[type(e.g. patient_name, age...)] = value
        }
        // Set the datalist
        e.list.innerHTML = html;
    }
    else {
        e.list.innerHTML = '';
    }
}

async function queryType(e) {
    // Get value of focused element(input value)
    let type = e.id;
    let base_val;
    if (e.classList.contains("patient")) {
        base_val = document.querySelector('#patient_name').value
    } else if (e.classList.contains("medication")) {
        base_val = document.querySelector('#med_name').value
    }

    // If base.value present
    if (base_val) {
        // Make a async query to fetch data
        let response = await fetch(`/query?value=${encodeURIComponent(base_val)}&type=${encodeURIComponent(type)}`);
        let results = await response.json();

        if (e.tagName.toLowerCase() === "select") { // If it's a drop down select
            // Require no datalist only value
            e.value = results[0] ? results[0][type] : '';
        } else { // If only a input field
            // prepare HTML for setting up a datalist
            let html = '';
            for (let row of results) { // here row is [{},{}...]
                html += `<option value="${row[`${type}`]}">`; // row[type(e.g. patient_name, age...)] = value
            }
            // Set the datalist
            e.list.innerHTML = html;
        }
    }
}
