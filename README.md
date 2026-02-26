# OLAP Business Intelligence Assistant
### Tier 2 Capstone Project — Streamlit BI Application

A natural language OLAP assistant that lets business users explore the Global Retail Sales dataset (10,000 transactions, 2022–2024) through conversational queries — no SQL or BI tool expertise required.

---

## Features

- **6 OLAP Operations**: Slice, Dice, Group & Summarize, Drill-Down, Roll-Up, Compare
- **Natural Language Interface**: Ask questions in plain English
- **Multi-Turn Conversations**: Follow-up questions maintain context from previous queries
- **Interactive Charts**: Auto-selected bar, line, and pie charts via Plotly
- **Quick Filters**: Sidebar filters by year, region, and category
- **Follow-Up Suggestions**: AI suggests 3 logical next questions after each analysis
- **Error Handling**: Graceful fallback for any LLM or code execution issues

---

## Project Structure

```
olap-streamlit-app/
├── app.py                  # Main Streamlit application
├── prompts.py              # System prompt + response templates
├── data_utils.py           # Data loading, execution, formatting helpers
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API key (never commit this)
├── data/
│   ├── global_retail_sales.csv   # Dataset (10,000 rows)
│   └── generate_dataset.py       # Script to regenerate dataset
└── docs/
    ├── README.md           # This file
    └── prompt_design.md    # Prompt engineering documentation
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone or Download the Project

```bash
# If using git
git clone <your-repo-url>
cd olap-streamlit-app
```

### 2. Create a Virtual Environment (recommended)

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

Open `.streamlit/secrets.toml` and replace the placeholder:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
```

> ⚠️ **Never commit `secrets.toml` to git.** It is already in `.gitignore`.

### 5. Generate the Dataset

```bash
cd data
python generate_dataset.py
cd ..
```

This creates `data/global_retail_sales.csv` with 10,000 synthetic retail transactions.

### 6. Run the Application

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## Usage Guide

### Basic Queries

| What you want | What to type |
|---------------|-------------|
| See overall numbers | *"Give me a dataset overview"* |
| Filter by one dimension | *"Show only 2024 data"* |
| Filter by multiple dimensions | *"Show Electronics sales in Europe"* |
| Aggregate by dimension | *"Total revenue by region"* |
| Navigate hierarchy | *"Break down 2024 Q4 by month"* |
| Compare periods | *"Compare 2023 vs 2024 by category"* |

### Sidebar Filters

Use the **Quick Filters** panel on the left to pre-filter the dataset by year, region, or category. All chat queries will run against your filtered subset.

### Sample Queries (Clickable)

The sidebar lists 6 sample queries you can click to run instantly.

### Follow-Up Questions

After each analysis, the assistant suggests 3 follow-up questions. Click any of them to continue the analysis thread.

### Clear Conversation

Click **🗑️ Clear conversation** at the bottom to reset the chat and start fresh.

---

## OLAP Operations Demonstrated

### 1. Slice — Single Filter
> *"Show only Q4 2024 data"*

Filters the dataset to a single dimension value and summarizes by category.

### 2. Dice — Multiple Filters
> *"Electronics in Europe, 2024"*

Applies multiple simultaneous filters: category + region + year.

### 3. Group & Summarize
> *"Total revenue by region"*

Aggregates revenue, profit, and transaction count grouped by region.

### 4. Drill-Down
> *"Break down 2024 revenue by quarter, then Q4 by month"*

Navigates from annual → quarterly → monthly granularity.

### 5. Roll-Up
> *"Show daily transactions rolled up to monthly totals"*

Aggregates fine-grained data to a higher summary level.

### 6. Compare
> *"Compare 2023 vs 2024 revenue by category"*

Side-by-side comparison across time periods or dimension values.

---

## Technical Architecture

```
User Query (natural language)
        │
        ▼
  Streamlit Chat Input
        │
        ▼
  Anthropic Claude API
  (System Prompt + Chat History)
        │
        ▼
  JSON Response Parsing
  { operation, pandas_code, chart_type, insight, follow_ups }
        │
        ▼
  Safe pandas exec() on filtered DataFrame
        │
        ▼
  Plotly Chart Rendering
  + Formatted Data Table
  + Business Insight
  + Follow-up Buttons
```

---

## API Key & Cost Notes

- This app uses **Claude Sonnet** (`claude-sonnet-4-6`)
- Average cost per query: ~$0.001–$0.003 USD
- Multi-turn context grows with conversation length; clear chat to reset
- Typical demo session (20 queries): ~$0.05

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Error: No module named 'anthropic'` | Run `pip install -r requirements.txt` |
| `API key not configured` | Check `.streamlit/secrets.toml` |
| `FileNotFoundError: global_retail_sales.csv` | Run `python data/generate_dataset.py` |
| Chart not showing | The LLM chose `table` type — expand the data table |
| Wrong results | Try rephrasing — be specific about column names |

---

## Development Notes

- The app uses `st.cache_data` for the dataset (loaded once per session)
- The `execute_pandas_code()` function uses a sandboxed `exec()` with only `pd` and `df` in scope
- LLM output is always validated for JSON structure before execution
- Chat history is stored in `st.session_state` and passed to the API on every turn

---

## License

MIT License — Free to use and modify for educational purposes.
