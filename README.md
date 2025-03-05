# Companies House Digger

Companies House Digger is a Flask-based web application for mining and visualizing company data from the UK’s Companies House. It supports CRUD operations for companies, persons, and their relationships, as well as an interactive network visualization using Vis.js.  It has one click process for getting Director and Persons with Significant control information and including it in the model.  I built this while trying to understand the 'simple' structure of my local 'water' company.

## Features

- **Companies & Persons Management:**  
  Create, read, update, and delete companies and persons, with details such as company number, registered address, status, and incorporation date.

- **Relationships & Attributes:**  
  Define relationships (e.g., directorship, shareholding) between companies and persons. Relationships can include extra attributes (e.g., number of shares) stored in a separate attributes table.

- **Network Visualization:**  
  View an interactive network map of companies and persons. The network supports:
  - **Focus Mode:** Filter the network by focusing on a specific company with adjustable depth.
  - **Relationship Type Filtering:** Use checkboxes to hide or show certain relationship types.
  - **Directional Edges:** Visualize the direction of relationships with arrows on the edges.

- **Companies House API Integration (Dig Feature):**  
  Enter a company number to fetch data from the Companies House API. The app supports upsert behavior (update if the company exists) and extracts details such as company name, registered address, and status.

## Installation

1. **Clone, Configure and Run:**

   ```bash
   git clone https://github.com/yourusername/CompaniesHouseDigger.git
   cd CompaniesHouseDigger
   python -m venv venv
   .\venv\Scripts\Activate.ps1  or Linux something like source venv/bin/activate
   pip install -r .\requirements.txt
   <move the .env.sample to .env and edit>
   python .\run.py

## Screenshots

![Screenshot 2025-03-05 124440](https://github.com/user-attachments/assets/f077a60b-b810-4cc0-859a-b23d94b6c82e)
List of companies

![Screenshot 2025-03-05 124601](https://github.com/user-attachments/assets/850f68dd-8499-4b03-8620-97b5dadeb866)
Company Details

![Screenshot 2025-03-05 124410](https://github.com/user-attachments/assets/d32decc6-4c8d-4e39-b147-0db0e31745da)
Network View

## Limitations and Bugs
  - **Non-UK companies** are stored as persons.
  - **Companies House data** is very dirty so the same person or company may appear many times with minor differences.
  - **Fixing relationships** is tricky.
  - **Adding relationships** manually is time consuming.
  - **Database** is currently jsut configued as sqlite - it may not perform if you try to model anything large.
  - **No Security** testing has been carried out on this application.  Always assume it's trying to kill you.
 
## To-Do
  - **Shareholders** Automatically grab and process shareholder information from CH.
  - **Accounts** Automatically grab and process company accounts accounts.
  - **Links** Include Links back to CH
