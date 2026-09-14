# Product Requirements Document (PRD)
**Project Name:** CAREERCRAWL – Internship & Job Finder  
**Version:** 1
**Type:** Python Application (CLI + Streamlit Ready)  
**Primary Language:** Python only  
**Duration:** 2-Week Internship Project  

---

## 1. Project Overview

**CAREERCRAWL** is a Python-based application that helps users find internships and jobs by scraping listings from **Internshala**.  

The application supports both **CLI** and future **Streamlit** interfaces. It uses a **hybrid scraping system**:

- Primary Method → `requests` + `BeautifulSoup` (lightweight & fast)
- Backup Method → `Selenium` (used only when BeautifulSoup fails)

Each search is manually triggered by the user. The tool scrapes a limited number of listings (configurable 5–10), shows a preview table, and saves the results in both **JSON** and **Excel** formats with timestamped filenames.

---

## 2. Goals

- Build a reliable and ethical internship/job finder focused on Internshala.
- Implement a hybrid scraping system with proper fallback.
- Provide structured data storage (JSON + Excel).
- Deliver a clean and beautiful user interface (CLI first).
- Minimize the risk of getting blocked.
- Allow easy viewing, filtering, and basic analysis of saved data.
- Keep the codebase modular and deployment-friendly.

---

## 3. Scope

### In Scope (Must Have)
- Scraping from **Internshala only**
- Hybrid Scraping System (requests + BeautifulSoup → Selenium fallback)
- User-triggered search cycles
- Configurable number of results (5–10)
- Configuration file (`config.json`)
- Preview table before saving
- Saving data in JSON + Excel
- Timestamped filenames
- Beautiful CLI interface using `rich`
- File navigation system
- Filtering of saved data
- Basic statistics
- Open apply link in browser
- Simple search history log
- Proper error handling

### Out of Scope
- LinkedIn or other aggressive websites

---

## 4. Features

### 4.1 Hybrid Scraping System
- **Primary:** `requests` + `BeautifulSoup`
- **Backup:** `Selenium` (triggered automatically if primary method fails)
- Proper error handling and logging when switching methods
- User is informed which method was used

### 4.2 Search / Find Cycle
- User starts a new search manually
- Inputs:
  - Job Type (Internship / Job)
  - Keywords / Skills
  - Location (optional)
- Scrapes only the configured number of results (default 5–10)
- Shows a **preview table** using `rich` before saving
- User can confirm or cancel the save

### 4.3 Configuration File (`config.json`)
Users can configure:
- Default keywords
- Number of results per search (5–10)
- Request delay range
- Default location
- Preferred scraping method
- Headless mode (for Selenium)

### 4.4 Data Saving
- Every search creates **new files**
- Filename format:  
  `jobtype_YYYY-MM-DD_HH-MM-SS.json`  
  `jobtype_YYYY-MM-DD_HH-MM-SS.xlsx`

- Folder Structure:

```
saved/
├── internship/
└── job/
```

### 4.5 Preview Table
After scraping, display a clean table showing:
- Title
- Company
- Location
- Stipend / Salary
- Key Skills
- Apply Link (shortened)

### 4.6 View & Navigate Saved Files
- List saved files separately for Internships and Jobs
- Navigate using numbers
- View summary and full details

### 4.7 Filtering
Filter saved data by:
- Job Type
- Skills (single or multiple)
- Location
- Stipend / Salary range
- Keywords in title
- Source

### 4.8 Basic Statistics
For any saved file show:
- Total listings
- Most common skills
- Average stipend (when available)
- Location distribution
- Remote vs Onsite count

### 4.9 Open Apply Link
- Option to open the selected apply link in the default web browser

### 4.10 Search History Log
- Maintain a simple local history of previous searches
- Store: keyword, job type, date, number of results, method used

### 4.11 Beautiful CLI Interface
- Built using `rich` library
- Colored menus, tables, panels, and progress indicators
- Clean and professional look

---

## 5. Non-Functional Requirements

| Category          | Requirement                                      |
|-------------------|--------------------------------------------------|
| Performance       | Search should complete within 30–60 seconds      |
| Reliability       | Strong error handling & fallback mechanism       |
| Stealth           | Anti-blocking measures mandatory                 |
| Usability         | Clear menus and feedback                         |
| Maintainability   | Modular and clean code                           |
| Compatibility     | Windows, macOS, Linux                            |

---

## 6. Anti-Blocking Measures

- Limit results to 5–10 per search
- Random delays between requests
- Rotate User-Agents
- Use realistic headers
- Prefer lightweight `requests` method first
- Use Selenium only as backup
- Clear responsible usage disclaimer

---

## 7. Data Schema

```json
{
  "id": "unique_id",
  "title": "Python Developer Intern",
  "company": "ABC Technologies",
  "location": "Bangalore / Remote",
  "job_type": "Internship",
  "stipend_salary": "₹10,000/month",
  "duration": "3 Months",
  "skills": ["Python", "Django", "SQL"],
  "posted_on": "2 days ago",
  "apply_link": "https://internshala.com/...",
  "description": "Short description...",
  "source": "Internshala",
  "scraped_at": "2026-09-12 22:15:30",
  "method_used": "BeautifulSoup / Selenium"
}
```

## 8. Suggested Project Structure

```
careercrawl/
│
├── main.py
├── config.json
├── cli/
│   └── interface.py
├── scraper/
│   ├── hybrid_scraper.py
│   ├── requests_scraper.py
│   └── selenium_scraper.py
├── storage/
│   ├── json_handler.py
│   ├── excel_handler.py
│   └── history.py
├── utils/
│   ├── filters.py
│   ├── stats.py
│   └── helpers.py
├── saved/
│   ├── internship/
│   └── job/
└── requirements.txt
```

## 9. Error Handling Strategy

- Network timeout → Retry with delay
- BeautifulSoup fails to extract data → Automatically switch to Selenium
- Selenium fails → Show clear error message to user
- Invalid user input → Show helpful validation messages
- File saving errors → Notify user and prevent crash

## 10. Future Enhancements

- Full Streamlit Web Interface
- Support for more websites
- Advanced skill matching
- Export filtered results
- Theme customization

## 11. Success Criteria

- Hybrid scraping works reliably (BeautifulSoup first, Selenium as backup)
- Data is correctly saved in JSON and Excel
- Preview table and statistics work properly
- Clean and professional CLI experience
- Minimal blocking risk during normal usage
- Modular and well-documented code