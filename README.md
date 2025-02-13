# 🎢 Endless Line - Theme Park Analytics
> A data-driven project for optimizing theme park experiences, developed during the Eleven Strategy Hackathon (February 2025)

## 🚀 Quick Start

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hadri96/Hackathon-ElevenStrategy.git
cd Hackathon-ElevenStrategy
```

### 2️⃣ Configure API Keys
Create a `.secret` file in the root directory with your API credentials:

```ini
# OpenWeatherMap Configuration
OPENWEATHERMAP_API_KEY=your_api_key_here

# Backblaze B2 Configuration
B2DBNAME=your_bucket_name
B2keyID=your_key_id
B2keyNAME=your_key_name
B2keyAPPKEY=your_application_key
B2endpoint=your_endpoint_url
AWS_REQUEST_CHECKSUM_CALCULATION=WHEN_REQUIRED
AWS_RESPONSE_CHECKSUM_VALIDATION=WHEN_REQUIRED
```

### 3️⃣ Install the Package
```bash
pip install -e .
```

### 4️⃣ Run the Application
```bash
python3 main.py
```
The application will start and be available at `http://127.0.0.1:8050/` in your web browser.

## 🔑 API Setup Guide

### ☁️ OpenWeatherMap Setup
1. Create an account at [OpenWeatherMap](https://openweathermap.org/api)
2. Navigate to the API keys section in your account dashboard
3. Subscribe to the free tier API plan
4. Copy your API key and add it to the `.secret` file

### 💾 Backblaze B2 Setup
1. Sign up for [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html)
2. In your B2 dashboard:
   - Create a new bucket
   - Generate an application key
   - Note down your bucket name and endpoint URL
3. Add your B2 credentials to the `.secret` file:
   - `B2DBNAME`: Name of your storage bucket
   - `B2keyID`: Your application key ID
   - `B2keyNAME`: Name for your key
   - `B2keyAPPKEY`: Your application key
   - `B2endpoint`: Your regional endpoint (format: https://s3.{region}.backblazeb2.com)

## 📦 Installation

### 3️⃣ Install the Package
```bash
pip install -e .
```

### 🔄 Update the Package
To get the latest changes, simply run:
```bash
pip install -e .
```

## 📝 Notes
- Make sure to keep your `.secret` file private and never commit it to version control
- The free tier of OpenWeatherMap API should be sufficient for development purposes
- For production use, consider upgrading to paid API tiers based on usage requirements

## 📁 Repository Structure
```
├──endless_line/
│	├── data_utils/               # Data handling utilities
│	│   ├── dashboard_utils.py    # Dashboard data processing
│	│   ├── dataloader.py        # Data loading and cleaning
│	│   └── weather_forecast.py  # Weather API integration
│	│
│	├── interface/               # Frontend components
│	│   ├── assets/             # Static assets (CSS, images)
│	│   ├── widgets/            # Reusable UI components
│	│   ├── app.py             # Main Dash application
│	│   ├── dashboard_customer.py  # Customer dashboard
│	│   ├── dashboard_operator.py  # Operator dashboard
│	│   ├── home.py            # Landing page
│	│   └── about.py           # About page
│	│
│	└── models/                 # ML model implementations
│		├── attendance/        # Attendance prediction models
│		└── waiting_time/      # Queue time prediction models
│
│
├── exploration/            # Data exploration and analysis
│
├── models/                 # ML models pickle exports
│
├── main.py               # Application entry point
│
├── data/                  # Raw data files
│
└── pyproject.toml         # Package metadata
```

## 🤝 Contributing
Feel free to submit issues and enhancement requests!

