# 🎬 Movie Recommendation System (MRS)

> A modern Python-based Movie Recommendation System that helps users discover their next favorite movie using **TMDB API**, **genre-based recommendations**, and **popularity/rating analysis**.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Tkinter-GUI-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/TMDB-API-blueviolet?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge">
</p>

---

# 📖 Overview

Movie Recommendation System (MRS) is a desktop application developed using **Python** and **Tkinter** that allows users to search for any movie and instantly receive detailed information along with intelligent recommendations.

Instead of simply displaying movie information, the application combines **TMDB recommendations**, **genre similarity**, **ratings**, and **popularity** to suggest movies users are likely to enjoy.

The project was built to understand:

* API Integration
* Recommendation Systems
* Desktop GUI Development
* Multithreading
* Real-world Data Processing

---

# ✨ Features

### 🔍 Smart Movie Search

* Search any movie
* Real-time search suggestions
* Autocomplete support

---

### 🎬 Detailed Movie Information

Displays:

* Movie Poster
* Movie Title
* Overview
* Release Year
* Runtime
* Genres
* Language
* Popular Rating
* Vote Count

---

### 🤖 Intelligent Recommendation Engine

Recommends movies using:

* TMDB Recommendation API
* Genre Similarity
* Rating Similarity
* Popularity Ranking

---

### 🖥 Modern Desktop UI

* Minimal Design
* Responsive Layout
* Scrollable Recommendations
* Movie Posters
* Interactive Recommendation Cards

---

### ⚡ Performance Optimized

* Multithreading
* Retry Mechanism for API Calls
* Lazy Image Loading
* Fast Search Experience

---

# 🛠 Tech Stack

| Technology | Purpose              |
| ---------- | -------------------- |
| Python     | Programming Language |
| Tkinter    | GUI Framework        |
| TMDB API   | Movie Database       |
| Requests   | API Communication    |
| Pillow     | Image Processing     |
| Threading  | Background Tasks     |

---

# 📂 Project Structure

```text
Movie-Recommendation-System/
│
├── movie.py                # Main Application
├── requirements.txt        # Dependencies
├── README.md
└── assets/
    ├── screenshots/
    └── logo.png
```

---

# ⚙ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/Movie-Recommendation-System.git
```

```bash
cd Movie-Recommendation-System
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Get TMDB API Key

Create a free account on:

[https://www.themoviedb.org/](https://www.themoviedb.org/)

Generate an API Key and replace

```python
TMDB_API_KEY = "YOUR_API_KEY"
```

inside

```python
movie.py
```

---

# ▶ Run Project

```bash
python movie.py
```

---

# 📸 Screenshots

### Home Screen

> *(Add Screenshot Here)*

---

### Search Suggestions

> *(Add Screenshot Here)*

---

### Movie Details

> *(Add Screenshot Here)*

---

### Recommendations

> *(Add Screenshot Here)*

---

# 🔄 How It Works

```text
            User
              │
              ▼
      Search Movie
              │
              ▼
        TMDB API Request
              │
              ▼
     Fetch Movie Details
              │
              ▼
 Recommendation Algorithm
     │                 │
     ▼                 ▼
TMDB Similar     Genre Matching
Movies           + Rating Score
      \            /
       \          /
        ▼        ▼
     Best Recommendations
              │
              ▼
      Display to User
```

---

# 🧠 Recommendation Logic

The recommendation system combines multiple factors:

* Official TMDB Recommendations
* Matching Genres
* Vote Average
* Movie Popularity
* Duplicate Removal
* Score-Based Ranking

This produces more relevant recommendations than relying solely on one source.

---

# 📚 Learning Outcomes

During this project, I learned:

* Working with REST APIs
* GUI Development using Tkinter
* Multithreading in Python
* Handling JSON Data
* Image Processing
* Recommendation System Basics
* Error Handling
* API Retry Strategies
* Clean UI Design

---

# 🚀 Future Improvements

* User Authentication
* Personalized Recommendations
* Watchlist
* Favorites
* Movie Trailer Support
* AI-Based Recommendation Engine
* Voice Search
* Dark Mode
* Streaming Platform Availability
* Export Recommendations

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve this project:

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Added new feature"
```

4. Push your branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It motivates me to keep building more open-source projects.

---

# 👨‍💻 Author

**Tushar Suhagpure**

🎓 B.Tech Artificial Intelligence & Machine Learning Student

🌱 Learning AI • Machine Learning • Python • Automation • Software Development

---

## 📜 License

This project is licensed under the **MIT License**.

Feel free to use, modify, and improve it for learning purposes.
