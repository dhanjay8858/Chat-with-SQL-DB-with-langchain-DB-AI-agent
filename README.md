<div align="center">

# 🗃️ AI Database Assistant (Production Edition)

### _A natural language AI interface for SQL databases combining ChatGPT, DBeaver, and MySQL Workbench._

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)

</div>

---

## 📌 Overview

**AI Database Assistant** is an enterprise-grade natural language interface for SQL databases. Built with a modular clean architecture using **LangChain SQL Agent**, **Groq Llama 3.3 70B** (`llama-3.3-70b-versatile`), **SQLAlchemy**, and **Plotly**, it converts plain English prompts into optimized SQL queries, executes them safely, and delivers interactive visual analytics.

Default LLM: **`llama-3.3-70b-versatile`** (Groq's top tool-calling model designed specifically for LangChain SQL Agents).

---

## ✨ Enterprise Capabilities (16 Phases Implemented)

| Feature | Description |
| :--- | :--- |
| 🤖 **Flagship Tool-Calling Model** | Powered by `llama-3.3-70b-versatile` on Groq with custom error recovery for zero parsing failures |
| 🗂️ **Database Explorer** | Full schema inspection — table columns, data types, primary/foreign keys, indexes, and live table previews |
| ✍️ **Natural Language CRUD** | `SELECT`, `INSERT`, `UPDATE`, and `DELETE` operations generated dynamically from natural language |
| 🛡️ **Safe Execution Layer** | Risk analysis rating (`LOW` to `CRITICAL`), SQL preview cards, impact explanations, and confirmation dialogs |
| 💻 **SQL Execution Panel** | Execution timing (ms), rows returned/affected, status badges, and syntax-highlighted SQL code blocks |
| 📖 **AI SQL Explainer** | 4-part breakdown: Purpose, Clause-by-Clause, Performance & Complexity (`O(N)` vs `O(log N)`), and Index Optimizations |
| 📈 **Database Analytics & Quality** | Missing values (NULL) audit, duplicate record scans, and statistical summaries (Min, Max, Avg, Median) |
| 🔍 **Interactive Data Grid** | Real-time multi-column search, pagination, click-to-sort, column resizing, and row count indicators |
| 📊 **Plotly Visualizations** | Automated Bar Charts, Pie Charts, Line Charts, Scatter Plots, Histograms, Box Plots, and Heatmaps |
| 📜 **Persistent Query History** | File-backed JSON history (`query_history.json`) with search, 1-click query re-run, and log deletion |
| 📥 **Multi-Format Exports** | 1-Click exports to **CSV (.csv)**, **Excel (.xlsx)**, **JSON (.json)**, and styled **PDF (.pdf)** reports |
| 🧠 **AI Dataset Insights** | Automatic IQR outlier detection (`1.5 * IQR`), statistical metrics, and natural language distribution summaries |
| 🔐 **Access Control & Security** | `🔒 Read Only Mode (Analyst)` vs `👤 Admin Mode (Full Access)` with strict blocking of `DROP TABLE`, `TRUNCATE`, and mass mutations |
| ⚡ **Performance Optimization** | SQLAlchemy connection pooling (`pool_size=10`, `pool_pre_ping=True`), sub-millisecond schema metadata caching (`0.19 ms`), and auto-invalidation |
| 🎨 **Premium Dark UI/UX** | Custom glassmorphism design system (`styles.py`), Google Fonts (`Inter` / `JetBrains Mono`), gradient tab highlights |

---

## 🏗️ Modular Project Architecture

```
Chat-with-SQL-DB-with-langchain-DB-AI-agent/
├── app.py                 # Main Streamlit application entry point
├── config/                # Settings & security configuration
│   ├── settings.py        # System constants & Groq LLM factory (llama-3.3-70b-versatile default)
│   └── security.py        # Security modes & policy engine (Read-Only vs Admin)
├── database/              # Database connection & inspection layer
│   ├── connection.py      # SQLAlchemy engine factory with connection pooling
│   ├── inspector.py       # Schema introspection & metadata caching
│   └── crud.py            # Natural language CRUD helper functions
├── agents/                # LangChain SQL Agent orchestration
│   └── sql_agent.py       # ReAct SQL agent with custom parsing error recovery
├── services/              # Business logic & execution services
│   ├── sql_executor.py    # Centralized SQL execution engine
│   ├── safety.py          # Safety middleware & confirmation evaluator
│   ├── sql_explainer.py   # AI query explainer & AST parser
│   └── ai_insights.py     # Database analytics & IQR outlier detection
├── ui/                    # Streamlit UI layout & components
│   ├── sidebar.py         # DB connection, credentials & security mode selector
│   ├── chat.py            # Conversational chat loop & confirmation card UI
│   ├── explorer.py        # Database Explorer panel & schema viewer
│   ├── preview.py         # Live table preview component
│   ├── sql_panel.py       # SQL execution preview panel with metrics
│   ├── data_grid.py       # Interactive searchable/paginated data grid
│   ├── history_ui.py      # Query history manager tab
│   └── styles.py          # Custom CSS design system & Google Fonts
├── charts/                # Plotly data visualization engine
│   └── visualizer.py      # Auto chart recommendation & Plotly renderer
├── exports/               # Multi-format report export handlers
│   ├── csv_export.py      # CSV export handler
│   ├── excel_export.py    # Excel (.xlsx) export handler
│   ├── json_export.py     # JSON export handler
│   └── pdf_export.py      # Styled PDF report generator
├── history/               # Persistent query history storage
│   └── query_history.py   # JSON file-backed logger
├── utils/                 # Helpers & validators
│   ├── logger.py          # Centralized logging module
│   └── validators.py      # SQL risk level analyzer
├── student.db             # Pre-built sample SQLite database
├── .gitignore             # Git ignore rules hiding .env, .venv, etc.
├── requirements.txt       # Python package dependencies
└── README.md              # Project documentation
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/dhanjay8858/Chat-with-SQL-DB-with-langchain-DB-AI-agent.git
cd Chat-with-SQL-DB-with-langchain-DB-AI-agent
```

### 2. Create & Activate Virtual Environment

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

### 4. Configure Environment Variables (Hidden in `.gitignore`)

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> 🔑 Get your API key at [console.groq.com](https://console.groq.com). Alternatively, enter your Groq API Key directly in the app sidebar!

### 5. Run the Application

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser 🎉

---

## 💡 Example Queries

| Query Type | Example Prompt | Action |
| :--- | :--- | :--- |
| **SELECT** | `"Show all students"` | Displays interactive data grid with search, pagination, exports, & charts |
| **ANALYTICS** | `"What is the average marks of all students?"` | Returns calculated mean metric (`90.17`) |
| **TOP SCORER** | `"Who scored the highest marks?"` | Returns top performer (`ANSHU` with `99` marks) |
| **INSERT** | `"Add a student named Rahul in AI class, section A, with 85 marks"` | Previews SQL, evaluates risk, presents confirmation card |
| **UPDATE** | `"Update MARKS of RAM to 95"` | Previews `UPDATE STUDENT SET MARKS = 95 WHERE NAME = 'RAM'` for approval |
| **DELETE** | `"Delete student named Rahul"` | Previews `DELETE FROM STUDENT WHERE NAME = 'Rahul'` for approval |

---

## 🛡️ Security Modes

- **🔒 Read Only Mode (Analyst)**: Blocks all `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, and `TRUNCATE` operations.
- **👤 Admin Mode (Full Access)**: Enables write operations with confirmation card middleware. Strictly blocks dangerous DDL (`DROP TABLE`, `TRUNCATE`) and mass `DELETE`/`UPDATE` queries without `WHERE` clauses.

---

## 🔒 Security Note (Git Ignore)

The `.gitignore` file automatically excludes sensitive files:
- `.env` & `.env.local` *(API Keys)*
- `.venv/` *(Virtual Environment)*
- `query_history.json` *(Local Query History)*
- `__pycache__/` *(Python Bytecode)*

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).
