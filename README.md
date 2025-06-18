# MTN MoMo SMS Analysis Dashboard

A full-stack application for analyzing MTN Mobile Money SMS transactions. This application processes SMS data in XML format, stores it in a SQLite database, and provides an interactive dashboard for visualization and analysis.

```
├── backend/
│   ├── main.py                  # Entry point: parses and inserts data
│   ├── api/                     # Flask API to serve data
│   │   └── app.py               # API server script
│   ├── data_cleaning/           # Scripts for cleaning & categorizing
│   │   ├── categorizer.py       # Categorizes SMS transactions
│   │   ├── cleaner.py           # Cleans raw SMS data
│   │   └── sms_loader.py        # Loads SMS data from XML
│   ├── database/                # Database interaction logic
│   │   ├── db_manager.py        # Database manager module
│   │   └── schema.sql           # Database schema definition
│   ├── transactions.db          # SQLite DB with populated data
│   ├── cleaned_sms_data.json    # Cleaned & categorized messages
│   └── unprocessed.log          # Messages that couldn’t be parsed
│
├── frontend/
│   └── index.html               # Dashboard interface
```

## Requested PDF and demo video

-Detailed report in pdf report

- Click [here] [] for the demo video.

## Features

- XML file processing
- Categorization and analysis
- Interactive dashboard with charts and statistics
- Real-time data updates
- Responsive design

## Tech Stack

### Backend

- Python
- Flask
- SQLite

### Frontend

- HTML5
- CSS3 (Tailwind CSS)
- JavaScript
- Chart.js for visualizations

## Prerequisites

- Python
- Flask

## Setup Instructions

1. Clone the repository:

```
git clone <repository-url>
cd momo-data-analysis
```

2. Install dependencies:

```
pip install Flask flask-cors
```

3. Run the backend(Data processing)

```
cd backend
python3 main.py
```

This will:

- Parse the XML messages
- Clean and categorize them
- Insert the result into transactions.db

Unprocessed messages can be viewed in the `unprocessed.log` file.

### To serve data using Flask API run:

```
cd backend/api
python3 app.py
```

This leaunches an API endpoint(e.g. http://localhost:5000) that the frontend can connect to.

4. View the frontend dashboard:

- Open `index.html` in your web browser

The dashboard suppports:

- Filtering by transaction type/date

- Interactive visualizations

- Detailed transaction views

## Usage

1. Open the dashboard in your web browser
2. Wait for the processing to complete
3. View the dashboard with charts and statistics
4. Use the filters to analyze specific transaction types or date ranges

## API Endpoints

- `GET /api/transactions` — fetch all transactions, possibly with filters like type/date.

- `GET /api/transactions/<id>` — fetch a single transaction by ID.

- `GET /api/analytics/summary` — return summarized analytics (like totals per category).

- `GET /api/transaction-types` — return the list of all categories/types (e.g., Airtime, Bank Transfer).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
