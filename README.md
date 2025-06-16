# MTN MoMo SMS Analysis Dashboard

A full-stack application for analyzing MTN Mobile Money SMS transactions. This application processes SMS data in XML format, stores it in a PostgreSQL database, and provides an interactive dashboard for visualization and analysis.

## Features

- XML file upload and processing
- Transaction categorization and analysis
- Interactive dashboard with charts and statistics
- Real-time data updates
- Responsive design

## Tech Stack

### Backend
- Node.js
- Express.js
- PostgreSQL
- XML parsing with xml2js

### Frontend
- HTML5
- CSS3 (Tailwind CSS)
- JavaScript
- Chart.js for visualizations

## Prerequisites

- Node.js 14 or higher
- PostgreSQL
- npm or yarn

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd momo-data-analysis
```

2. Install dependencies:
```bash
npm install
```

3. Set up PostgreSQL database:
```bash
# Create a new database
createdb momo_db

# Set environment variables
echo "DATABASE_URL=postgresql://postgres:postgres@localhost/momo_db" > .env
```

4. Run the backend server:
```bash
# Development mode with auto-reload
npm run dev

# Production mode
npm start
```

5. Open the frontend:
- Open `index.html` in your web browser

## Usage

1. Open the dashboard in your web browser
2. Click "refresh data" 
3. Wait for the processing to complete
4. View the dashboard with charts and statistics
5. Use the filters to analyze specific transaction types or date ranges

## API Endpoints
 
- `GET /transactions`: Get list of transactions
- `GET /statistics`: Get transaction statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
 
 