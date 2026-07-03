# 🦷 AI BOT TOOTHLESS

### AI-Powered Smart Price Tracker

> **Never overpay again.**
> Toothless AI is an intelligent price tracking platform that continuously monitors product prices across multiple e-commerce websites and notifies users whenever prices drop below their desired amount.

---

# 📖 Overview

Online shopping prices fluctuate frequently. Products may become cheaper for only a few hours before returning to their original prices. Constantly checking prices manually is time-consuming and inefficient.

Toothless AI automates this entire process.

Simply provide a product URL, specify your target price, and Toothless AI continuously monitors the product. Whenever the price falls below your desired value, the system instantly sends an email notification.

The project has been designed using a modular architecture, making it easy to maintain, extend, and integrate with additional e-commerce websites in the future.

---

# 🎯 Project Goals

The primary objectives of this project are:

* Automate online price tracking
* Notify users instantly when prices decrease
* Support multiple shopping websites
* Store historical price data
* Visualize pricing trends
* Build a scalable scraping architecture
* Demonstrate real-world Python development practices

---

# ✨ Features

* ✅ Multi-website support
* ✅ Amazon product tracking
* ✅ Flipkart product tracking
* ✅ Myntra product tracking
* ✅ Automatic scheduled monitoring
* ✅ Email alerts
* ✅ SQLite database
* ✅ Historical price storage
* ✅ Interactive dashboard
* ✅ Modular scraper architecture
* ✅ Easy configuration
* ✅ Extensible design
* ✅ Lightweight and beginner-friendly

---

# 🛠️ Tech Stack

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| Python        | Core programming language       |
| Flask         | Backend web framework           |
| SQLite        | Database                        |
| BeautifulSoup | HTML parsing                    |
| Requests      | Fetch webpage content           |
| APScheduler   | Automatic background scheduling |
| SMTP          | Email notifications             |
| HTML/CSS      | User Interface                  |
| Bootstrap     | Responsive frontend             |
| JavaScript    | Interactive dashboard           |

---

# 📂 Project Structure

```text
Toothless-AI/
│
├── app.py
├── config.py
├── database.py
├── models.py
├── scheduler.py
├── notifier.py
│
├── scrapers/
│   ├── amazon.py
│   ├── flipkart.py
│   ├── myntra.py
│   └── __init__.py
│
├── templates/
│
├── static/
│
├── database/
│
├── requirements.txt
│
└── README.md
```

---

# 🏗️ How Toothless AI Works

The application follows a simple but scalable workflow.

```
User
   │
   ▼
Enter Product URL
   │
   ▼
Website Detection
   │
   ▼
Corresponding Scraper
   │
   ▼
Extract Product Information
   │
   ▼
Save Price into Database
   │
   ▼
Compare with Target Price
   │
   ▼
Price Dropped?
   │
  Yes
   │
   ▼
Send Email Notification
```

---

# ⚙️ System Architecture

```
                    +----------------+
                    |     User       |
                    +--------+-------+
                             |
                             v
                    +----------------+
                    | Flask Backend  |
                    +--------+-------+
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
     Amazon.py          Flipkart.py        Myntra.py
          |                  |                  |
          +---------+--------+------------------+
                    |
                    v
            Product Information
                    |
                    v
             SQLite Database
                    |
                    v
             Scheduler Service
                    |
                    v
          Email Notification System
```

---

# 📜 Module Explanation

---

## app.py

This is the heart of the application.

Responsibilities:

* Starts the Flask server
* Handles user requests
* Accepts product URLs
* Displays dashboard
* Connects frontend with backend
* Calls appropriate scraper
* Stores product information

---

## config.py

Contains application configuration.

Responsibilities:

* Email credentials
* Database settings
* Scheduler settings
* Secret keys
* Application constants

Keeping configurations separate makes the project cleaner and more secure.

---

## database.py

Handles database connection.

Responsibilities:

* Create database
* Connect SQLite
* Execute queries
* Save products
* Retrieve products
* Update prices

---

## models.py

Defines database structure.

Responsibilities:

* Product table
* Price history
* User settings
* Relationships

---

## notifier.py

Responsible for sending email alerts.

Workflow:

1. Price drops
2. Notification created
3. SMTP server connects
4. Email delivered

---

## scheduler.py

Runs automatically in the background.

Responsibilities:

* Execute tracking periodically
* Check all saved products
* Update prices
* Trigger notifications

Without this module, the user would need to manually refresh prices.

---

# 🛒 Scraper Modules

Each shopping website has its own scraper.

## amazon.py

Responsible for:

* Downloading Amazon product page
* Extracting:

  * Product Name
  * Current Price
  * Image
  * Availability

---

## flipkart.py

Responsible for:

* Parsing Flipkart pages
* Extracting product details
* Returning standardized data

---

## myntra.py

Responsible for:

* Reading Myntra product pages
* Extracting pricing
* Returning common product format

---

# 🔄 Why Separate Scrapers?

Every shopping website has different HTML structures.

Instead of writing one massive scraper filled with conditions, Toothless AI uses independent scraper modules.

Advantages:

* Easy maintenance
* Better readability
* Easy debugging
* Easy expansion
* Cleaner architecture

Adding support for a new website only requires creating one new scraper file.

---

# 🗄️ Database Design

Each tracked product stores:

* Product Name
* Website
* URL
* Current Price
* Target Price
* Last Updated Time
* Price History

This allows users to monitor long-term pricing trends.

---

# 📧 Email Notification Flow

```
Scheduler
      │
      ▼
Check Product Price
      │
      ▼
Compare Target Price
      │
      ▼
Price Lower?
      │
      ▼
Generate Email
      │
      ▼
SMTP Server
      │
      ▼
User Inbox
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Toothless-AI.git
```

Move into the project

```bash
cd Toothless-AI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

# 💡 Future Improvements

The current version is designed with scalability in mind.

Potential future enhancements include:

* AI-based price prediction
* Telegram notifications
* WhatsApp alerts
* Browser extension
* Chrome plugin
* User authentication
* Cloud deployment
* PostgreSQL integration
* Redis caching
* Docker support
* REST API
* Mobile application
* Machine learning recommendation engine

---

# 🎓 Learning Outcomes

This project demonstrates practical knowledge of:

* Python programming
* Web scraping
* Backend development
* Flask
* Database management
* Modular software architecture
* Scheduling jobs
* Email automation
* API design concepts
* Real-world project organization

---

# 🤝 Contributing

Contributions are welcome.

If you have ideas for improvements, bug fixes, or additional e-commerce integrations, feel free to fork the repository, create a feature branch, and submit a pull request.

---

# 📄 License

This project is released under the MIT License.

---

# 👨‍💻 Author

**Joydeep**

Mechanical Engineering Graduate (NIT Durgapur)

Aspiring Data Scientist | Python Developer | AI Enthusiast

If you found this project useful, consider giving it a ⭐ on GitHub.
