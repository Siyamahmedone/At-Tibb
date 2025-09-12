// Script for Form page
// Initial Setup after DOM
document.addEventListener('DOMContentLoaded', function () {
    // ---Med-list---
    // Get med_list, datalist
    const medList = safeEl('med_list');
    if (!medList || !medData) return; // Return if non-existing
    // Proceed
    // Clear existing options
    medList.innerHTML = '';
    // Populate options
    Object.keys(medData).forEach(medName => {
        const option = document.createElement('option');
        option.value = medName;
        medList.appendChild(option);
    });

    // Default-no-enter function
    document.querySelector('.prescription').addEventListener('keydown', function(e) {
        // If Enter is pressed inside any input
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault(); // prevent form submission
        }
    });
    // Excluded from default: addRow & submit
    let addRowBtn = safeEl('addRowBtn');
    addRowBtn.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault(); // prevents scrolling with space
            addRow();           // call the function just like onclick
        }
    });
    let save = safeEl('save');
    save.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault(); // prevents scrolling with space
            save.click();       // call click to submit
        }
    });

    // Row removal function with Table update(complex)
    // Function is active from beginning monitoring row
    // Getting elements
    const tbody = safeEl('medications');
    const removeButton = safeEl('removeRowBtn');
    // Setting status
    let removeEnabled = false;

    // If clicked removeRowBtn change status
    removeButton.addEventListener('click', () => {
        removeEnabled = !removeEnabled;
        updateRemoveUI();
    });

    // If clicked Row after status enabled(after remove btn pressed)
    tbody.addEventListener('click', (event) => {
        // Condition of Inaction: if remove button not pressed
        if (!removeEnabled) return;

        // Get target row
        const row = event.target.closest('tr');
        if (!row || !tbody.contains(row)) return;

        // remove, update, UI
        removeRow(row);
        updateTable();
        // Turn off remove mode after removing
        removeEnabled = false;
        updateRemoveUI();
    });


    // Associated Functions
    function updateRemoveUI() {
        tbody.classList.toggle('remove-enabled', removeEnabled); // status: removeEnable
        // Set textContent of remove btn
        removeButton.textContent = removeEnabled
          ? 'Cancel' // if true
          : 'Remove Medication'; // if false
    }

    function removeRow(row) {
        // Get row number
        const firstInput = row.querySelector('input');
        if (!firstInput) return;
        const rowNum = parseInt(firstInput.id.split('_')[2], 10); // as, id = med_name_(num)

        // Remove Row Direct
        row.remove();

        // Remove datalists tied to this row
        const datalistIds = ["med_list_", "dose_list_", "form_list_", "schedule_list_", "timing_list_", "duration_list_"];
        datalistIds.forEach(prefix => {
          const dl = safeEl(`${prefix}${rowNum}`);
          if (dl) dl.remove();
        });
    }
    // ---finish---
});

// Function updating table (also associated with removeRow function)
function updateTable() {
    const tbody = safeEl('medications');
    const rows = tbody.querySelectorAll("tr");

    rows.forEach((row, index) => {
        const newNum = index + 1; // sequence numbering starts at 1

        // Update sequence value in the first <td>
        const sequenceCell = row.querySelector("td");
        if (sequenceCell) {
            sequenceCell.textContent = newNum;
        }

        // Update each <td>input inside the row
        const inputs = row.querySelectorAll("input");
        inputs.forEach(input => {
            // --- Fix the input ID ---
            // Get newId from Id = med_name_(num) or (type)_(num)
            const parts = input.id.split("_"); // ["med", "name", "(num")]
            const base = parts.slice(0, -1).join("_"); // "med_name"
            const newId = `${base}_${newNum}`; // "med_name_(newNum)"
            // Set newId
            input.id = newId;

            // --- Fix the datalist ID and list attr ---
            const oldListId = input.getAttribute("list");
            if (oldListId) {
                // Get newListId from listId = (med/type)_list_(num)
                const listParts = oldListId.split("_"); // ["med", "list", "(num)"]
                const listBase = listParts.slice(0, -1).join("_"); // "med_list"
                const newListId = `${listBase}_${newNum}`; // "med_list_(newNum)"

                // Rename(Set the newListId) the datalist if it exists
                const datalist = safeEl(oldListId);
                if (datalist) {
                    datalist.id = newListId;
                }
                // Point input to the renamed datalist
                input.setAttribute("list", newListId);
            }
        });
    });
}


// Additional functions (called by Btn's)
// ---AddRow---
function addRow() {
    // Get elements
    let tbody = safeEl('medications');
    // Get Count to Length of Table
    let count = tbody.rows.length;
    count++; // Increment Count for next row index

    // Create new row <tr>
    let tr = document.createElement('tr');

    // Create Datalists for new Row
    let sec = document.querySelector('.right-section');
    let lists = ["med", "dose", "form", "schedule", "timing", "duration"];
    lists.forEach(listType => {
        let datalist = document.createElement("datalist");
        datalist.id = `${listType}_list_${count}`;
        sec.appendChild(datalist);
    });

    // Create cells <td> for new row <tr>, adding to it's innerHTML
    tr.innerHTML = `
    <td>${count}</td>
    <td><input id=\"med_name_${count}\" list=\"med_list_${count}\" autocomplete=\"off\" type=\"text\" name=\"med_name[]\" class=\"form-control form-control-md\" onfocus=\"setNameList(this)\"></td>
    <td><input id=\"dose_${count}\" list=\"dose_list_${count}\" autocomplete=\"off\" type=\"text\" name=\"dose[]\" class=\"form-control form-control-md\" onfocus=\"setTypeList(this)\"></td>
    <td><input id=\"form_${count}\" list=\"form_list_${count}\" autocomplete=\"off\" type=\"text\" name=\"form[]\" class=\"form-control form-control-md\" onfocus=\"setTypeList(this)\"></td>
    <td><input id=\"schedule_${count}\" list=\"schedule_list_${count}\" autocomplete=\"off\" type=\"text\" name=\"schedule[]\" class=\"form-control form-control-md\" onfocus=\"setTypeList(this)\"></td>
    <td><input id=\"timing_${count}\" list=\"timing_list_${count}\" autocomplete=\"off\" type=\"text\" name=\"timing[]\" class=\"form-control form-control-md\" onfocus=\"setTypeList(this)\"></td>
    <td><input id=\"duration_${count}\" list=\"duration_list_${count}\" autocomplete=\"off\" type=\"text\" name=\"duration[]\" class=\"form-control form-control-md\" onfocus=\"setTypeList(this)\"></td>
    `;

    // Append the new row <tr> into table <tbody>
    tbody.appendChild(tr);

    // focus the new row
    safeEl(`med_name_${count}`).focus();
}


// ---SetNameList---
// Set datalist of medName dynamic exclusion function
function setNameList(element) {
    // Get row number of currnt row
    const rowNum = parseInt(element.id.split("_")[2], 10); // as, id = med_name_(num)
    // Base datalist template
    const allOptions = document.querySelectorAll("#med_list option");

    // Collect values from other rows
    const usedNames = [];
    document.querySelectorAll("[id^='med_name_']").forEach(input => {
        if (input.value && input.value !== element.value) {
            usedNames.push(input.value);
        }
    });

    // Build filtered HTML
    let html = "";
    allOptions.forEach(opt => {
        if (!usedNames.includes(opt.value)) {
            html += `<option value="${opt.value}">`;
        }
    });

    // Set the datalist of the current row
    safeEl(`med_list_${rowNum}`).innerHTML = html;
}

// ---SetTypeList---
// Set datalist of med(Type) based on medName
function setTypeList(element) {
    // Get row number and type of currnt row
    const [type, rowNumStr] = element.id.split("_");
    const rowNum = parseInt(rowNumStr, 10);

    // Get corresponding med_name element of same row
    const med_name = safeEl(`med_name_${rowNum}`);

    // Build HTML of current row type
    let html = '';
    // Only if med_name present in medDat-> proceed
    if (med_name && med_name.value in medData) {
        // Get medRow for medName
        let medRow = medData[med_name.value]
        // Get typeData from medRow
        let type_data = medRow[`${type}_data`];
        // If data not an array
        if (!Array.isArray(type_data)) type_data = [];

        // Write Options from typeData
        for (let data of type_data) {
            html += `<option value="${data}">`;
        }
    }
    // Set the datalist of current row type
    safeEl(`${type}_list_${rowNum}`).innerHTML = html;
}


// Helper function
function safeEl(id) {
    return document.getElementById(id) || null;
}

