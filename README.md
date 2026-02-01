# 🚀 LEOC - Local Emergency Operating Centre
## Relief Distribution Management System

A beautiful, responsive web application for managing and tracking relief distribution during emergency situations. Built with Python Flask, Bootstrap 5, and Chart.js.

---

## ✨ Features

### Dashboard
- **Real-time Statistics**: Track total distributions, items, locations, and beneficiaries
- **Interactive Charts**: 
  - Doughnut chart for relief items distribution
  - Horizontal bar chart for location-wise distribution
- **Recent Distributions Table**: View last 10 distributions with full details
- **Image Support**: View distribution evidence photos

### Relief Distribution Form
- **Beneficiary Information**: Name, ID, phone number
- **Distribution Details**: Location, relief items, quantity
- **Status Tracking**: Distributed, Pending, In Progress, Delivered
- **Image Upload**: Attach evidence photos to distributions
- **Notes Field**: Add additional information

### Database Management
- SQLite database for reliable data storage
- Automatic image handling with file management
- Delete records with automatic cleanup

---

## 📋 Requirements

- Python 3.7+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1

---

## 🛠️ Installation & Setup

### 1. Navigate to the project directory
```bash
cd /home/prakash/Documents/App\ Development/leoc
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

The app will be available at: **http://localhost:5000**

---

## 📁 Project Structure

```
leoc/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   ├── base.html            # Base template with navbar
│   ├── index.html           # Dashboard page
│   └── form.html            # Relief distribution form
├── static/
│   ├── css/
│   │   └── style.css        # Beautiful responsive styles
│   ├── js/
│   │   └── dashboard.js     # Dashboard functionality
│   ├── uploads/             # Uploaded images directory
│   └── images/              # Static images directory
└── leoc.db                  # SQLite database (auto-created)
```

---

## 🎯 Usage

### Adding a Relief Distribution
1. Click **"New Distribution"** in the navigation bar
2. Fill in beneficiary details (name, ID, phone)
3. Enter distribution location and relief items type
4. Specify quantity and distribution status
5. Optionally upload an image as evidence
6. Add any additional notes
7. Click **"Record Distribution"**

### Viewing Dashboard
1. Click **"Dashboard"** in the navigation bar
2. View statistics cards showing:
   - Total distributions
   - Total items distributed
   - Number of locations served
   - Number of beneficiaries
3. Analyze charts showing:
   - Relief items distribution breakdown
   - Distribution count by location
4. Browse recent distributions in the table
5. View or delete records as needed

---

## 🎨 Design Features

### Beautiful UI Components
- Modern gradient color scheme (Purple & Blue)
- Responsive Bootstrap 5 grid system
- Smooth animations and transitions
- Icon integration with Bootstrap Icons
- Mobile-friendly design

### Interactive Elements
- Real-time data updates (auto-refresh every 30 seconds)
- Hover effects on cards and rows
- Chart animations and interactions
- Form validation and feedback
- Image preview before upload

---

## 📊 Database Schema

### ReliefDistribution Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| beneficiary_name | String | Name of beneficiary |
| beneficiary_id | String | Unique beneficiary ID |
| phone | String | Contact phone number |
| location | String | Distribution location |
| relief_items | String | Type of relief items |
| quantity | Integer | Number of items |
| distribution_date | DateTime | Date and time of distribution |
| status | String | Distribution status |
| notes | Text | Additional notes |
| image_filename | String | Uploaded image filename |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard page |
| GET | `/form` | Distribution form page |
| GET | `/api/distributions` | Get all distributions |
| POST | `/api/distributions` | Add new distribution |
| GET | `/api/statistics` | Get statistics data |
| DELETE | `/api/distributions/<id>` | Delete distribution |

---

## 🚀 Advanced Features

### Statistics Calculation
- Automatic aggregation of items by type
- Location-wise distribution counting
- Real-time data refresh

### Image Management
- Secure filename generation
- Automatic directory creation
- Image cleanup on record deletion
- File size limit (16MB)

### Data Visualization
- Chart.js integration for interactive charts
- Color-coded status badges
- Responsive chart layouts

---

## 🔒 Features & Security

- CSRF-safe form handling
- SQL injection protection via SQLAlchemy ORM
- Secure file upload with filename sanitization
- Input validation and escaping
- Error handling with user-friendly messages

---

## 💡 Tips

- The database is automatically created on first run
- Images are stored in `static/uploads/` directory
- Use meaningful beneficiary IDs for easy tracking
- Add location consistency for better analytics
- Regularly back up your `leoc.db` file

---

## 🐛 Troubleshooting

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Database errors
Delete `leoc.db` and restart the app to recreate it

### Missing uploads directory
The app automatically creates it, but you can manually create:
```bash
mkdir -p static/uploads
```

---

## 📝 License

Local Emergency Operating Centre (LEOC) - Relief Distribution System
2026

---

## 👨‍💻 Developer Notes

- Flask development mode enables auto-reload on code changes
- Set `debug=False` for production deployment
- Consider adding authentication for production use
- Use environment variables for sensitive configuration

---

## 🎓 Learning Resources

Built with:
- **Flask**: Python web framework
- **Flask-SQLAlchemy**: ORM for database
- **Bootstrap 5**: Responsive CSS framework
- **Chart.js**: JavaScript charting library

Happy relief distribution tracking! 🙏
