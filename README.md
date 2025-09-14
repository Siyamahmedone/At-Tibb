# At-Tibb (v1.1)
#### Video Demo:  <https://youtu.be/mrhkODf59fw>
#### Live Demo: <https://at-tibb.onrender.com>  
#### Description:
**At-Tibb** is a web application designed for managing doctor and clinic information and creating, processing, and storing patient prescriptions dynamically. The app features auto-suggestions for medications and their details, efficient management of prescription data, and storage in a database for future retrieval and review.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [File Structure](#file-structure)
- [Credits](#credits)
- [License](#license)

---

## Overview
At-Tibb is a fully responsive and user-friendly web application that allows clinics and doctors to manage their prescription workflow efficiently. It provides:

- Dynamic prescription forms with columns for medications, doses, forms, schedules, timing, and durations.
- Ability to add, remove, and update prescription rows dynamically.
- Prevention of duplicate medication entries within a prescription.
- Auto-suggestions for medication names and types using a pre-defined dataset (`medData`), which is stored locally for quick access.
- The use of `localStorage` for structured medication data along with doctor and clinic information to enable fast loading, with options to refresh or update data anytime.
- Editing and saving prescriptions at any stage.
- A history page to review all past actions and access prescription details via dedicated links.
- A search page with asynchronous queries to provide real-time suggestions and optimal management of available data.
- An account page for updating personal information and changing passwords.
- Dynamic flash messages to provide immediate feedback to users.
- Features for printing or exporting prescriptions to PDF.

The application is designed for both desktop and mobile use, featuring auto-resizing textareas, dynamic datalists, and smooth keyboard navigation for efficiency.


---

## Features

- **Dynamic Table Rows:** Add or remove medication rows in real-time to create or modify prescriptions efficiently.
- **Datalists & Auto-suggestions:** Populated dynamically from `medData`, providing accurate medication names and associated types.
- **Local Storage:** Doctor and clinic information along with medication data is saved and loaded automatically, improving speed and user experience.
- **Auto Date Fill:** Automatically sets the current date for prescriptions and search suggestions.
- **Keyboard Friendly:** Prevents accidental form submission with the Enter key. Supports Enter/Space for button actions and smooth tab navigation across fields.
- **Flash Messages:** Provides instant visual feedback for successful actions or errors; alerts auto-dismiss after five seconds.
- **Responsive Design:** Works across devices, from PCs to smartphones, and includes features for printing and saving prescriptions.
- **Data Integrity:** Prevents duplicate entries for medications within a single prescription and dynamically updates datalists to exclude used medications.

---

## Installation

**Requirements:**

    - **Python 3**
    - **cs50**
    - **Flask**
    - **Flask-Session**
    - **pytz**
    - **requests**

**Install dependencies:**
    ```bash
    pip install -r requirements.txt


**Run the application:**
    ```bash
    flask run

**Access the app in your browser at:**

    http://localhost:5000/

---

## Usage

1. **Doctor & Clinic Info**: Register an account filling out your account details, which are stored locally as well as in server for fast retrieval. Update anytime.

2. **Prescription Form:**

- Enter medication details; suggestions appear dynamically from medData.
- Add medication rows using the Add Row button.
- Remove rows by enabling Remove Medication and selecting the desired row.
- To update prescription medication list after subsequent prescription entry use "Refresh" from the navigation bar.

3. Saving Prescriptions: Click Save to store the data in the database, after which you would be directed to view page of the prescription

4. From the view page you can review, print, and edit the prescription

5. Editing the prescription you can change medication rows, add, remove row and update the prescription any time, any stage

6. History & Search: Review past prescriptions, and use the search page to find patient or medication records efficiently.

7. Using Search page to fill up all available or known to you information to get relevant prescriptions in results

8. Keyboard Shortcuts: Navigate smoothly with Tab, no worry as app would prevent accidental Enter submission, and use Enter/Space to trigger buttons.


## Scripts ##
1. **Layout Script** (`script.js`)

- Loads doctor and clinic data from localStorage.

- Highlights the active navigation link.

- Auto-dismisses flash messages.

- Sets the current date automatically.

- Initializes auto-resizing textareas.

- Handles AJAX requests for username verification and dynamic search queries.


2. **Form Page Script** (form.js)

- Manages the dynamic medication table: add, remove, and update rows.

- Updates input IDs and associated datalist references, especially when rows are removed.

- Dynamically populates datalists for medication names and types.

- Prevents duplicate medication names within a prescription.

- Disables accidental form submission with Enter keypress.


## File Structure

    project/
    ├── app.py
    ├── helpers.py
    ├── requirements.txt
    ├── prescription.db
    ├── template
    │   ├── login.html
    │   ├── register.html
    │   ├── index.html      # Main dashboard
    │   ├── view.html       # view page
    │   ├── edit.html
    │   ├── search.html
    │   ├── history.html
    │   ├── account.html
    │   ├── change.html
    │   ├── password.html
    │   └── view.html
    │
    ├── static/
    │   ├── script.js       # Layout script
    │   ├── script_form.js  # Form script
    │   ├── style.css       # Stylesheet
    │   └── logo.png        # App logo
    │
    └── README.md


## Credits
The project was developed solely by me as the final project for **CS50x** with some help from
- The CS50 week 9 problemset, finance and it's implementation as inspiration. 
- ChatGPT and AI models for suggestions and debugging of the app, it's scripts and improving it's pages
- Special thanks to my friends for helpful ideas and suggestions.
- Built using **Python, Flask, SQLite, HTML, CSS, and JavaScript**.


## License ##

This project is licensed under the MIT License.
