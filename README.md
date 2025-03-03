# Companies House Digger

Companies House Digger is a Flask-based web application for mining and visualizing company data from the UK’s Companies House. It supports CRUD operations for companies, persons, and their relationships, as well as an interactive network visualization using Vis.js.

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
   .\venv\Scripts\Activate.ps1   
   pip install -r .\requirements.txt
   <move the .env.sample to .env and edit>
   python .\run.py
