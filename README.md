<div align="center">

# 🗃️ Chat with SQL Database using LangChain

### _Ask questions in plain English — get answers from your database instantly._

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)

</div>

---

## 📌 About

**Chat with SQL DB** is an AI-powered conversational interface that lets you query SQL databases using natural language. Built with **LangChain's SQL Agent** and powered by **Groq's Llama 3.3 70B** model, it translates your questions into SQL, executes them, and returns human-readable answers — no SQL knowledge required.

It supports both **SQLite** (local) and **MySQL** (remote) databases out of the box.

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 💬 **Natural Language Querying** | Ask questions in plain English and get accurate database responses |
| 🔄 **Dual Database Support** | Switch between a local SQLite database or connect to a remote MySQL server |
| ⚡ **Groq-Powered LLM** | Ultra-fast inference using Groq's Llama 3.3 70B Versatile model |
| 🤖 **LangChain SQL Agent** | Autonomous agent that reasons, generates SQL, and interprets results |
| 🔐 **Secure API Key Input** | API key entered via sidebar with password masking |
| 💾 **Chat History** | Full conversation history with clear message option |
| 📡 **Streaming Responses** | Real-time streaming with Streamlit callback handler |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                    │
│         (Chat Interface + Sidebar)               │
└──────────────────────┬──────────────────────────┘
                       │  User Query (Natural Language)
                       ▼
┌─────────────────────────────────────────────────┐
│              LangChain SQL Agent                 │
│        (Zero-Shot ReAct Description)             │
└──────────────────────┬──────────────────────────┘
                       │  Generated SQL
                       ▼
          ┌────────────┴────────────┐
          │                         │
   ┌──────▼──────┐          ┌──────▼──────┐
   │   SQLite    │          │    MySQL     │
   │ (student.db)│          │  (Remote)    │
   └─────────────┘          └─────────────┘
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/chat-with-sql-db-langchain.git
cd chat-with-sql-db-langchain
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> 🔑 Get your free API key at [console.groq.com](https://console.groq.com)

### 5. Initialize the SQLite Database (Optional)

If you want to recreate the sample `student.db`:

```bash
python sqlite.py
```

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** 🎉

---

## 🗂️ Project Structure

```
chat-with-sql-db-langchain/
│
├── app.py              # Main Streamlit application with LangChain SQL Agent
├── sqlite.py           # Script to create and populate the sample SQLite database
├── student.db          # Pre-built SQLite database with sample student records
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not tracked by git)
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## 💡 Example Queries

Once the app is running, try asking:

| Query | What it does |
| :--- | :--- |
| `Show me all students` | Returns all records from the STUDENT table |
| `Who scored the highest marks?` | Finds the top scorer |
| `How many students are in section A?` | Counts students filtered by section |
| `What is the average marks of all students?` | Calculates the average |
| `List students who scored above 90` | Filters by marks > 90 |

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io) — interactive web UI
- **LLM:** [Groq](https://groq.com) — Llama 3.3 70B Versatile (ultra-fast inference)
- **Framework:** [LangChain](https://langchain.com) — SQL Agent with ReAct reasoning
- **Database:** SQLite (local) / MySQL (remote via SQLAlchemy)
- **ORM:** [SQLAlchemy](https://sqlalchemy.org) — database engine abstraction

---

## 📋 Sample Database Schema

The included `student.db` contains the following table:

```sql
CREATE TABLE STUDENT (
    NAME    VARCHAR(25),
    CLASS   VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS   INT
);
```

**Sample Records:**

| NAME  | CLASS            | SECTION | MARKS |
| :---- | :--------------- | :-----: | :---: |
| AMIT  | Data Science     |    C    |  98   |
| RAM   | Data Analytic    |    A    |  92   |
| SUMIT | Computer Science |    B    |  96   |
| AMAN  | AI               |    A    |  88   |
| KAMAL | GENAI            |    C    |  68   |
| ANSHU | ML               |    B    |  99   |

---

## ⚙️ MySQL Configuration

To connect to a MySQL database instead of SQLite:

1. Select **"Connect to MySQL Database"** in the sidebar
2. Enter your MySQL credentials:
   - **Hostname** (e.g., `localhost`)
   - **Username** (e.g., `root`)
   - **Password**
   - **Database Name**
3. The agent will automatically connect and allow you to query your MySQL database

> **Note:** Make sure you have the `mysql-connector-python` package installed:
> ```bash
> pip install mysql-connector-python
> ```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**⭐ Star this repo if you found it useful!**

Made with ❤️ using LangChain & Streamlit

</div>

