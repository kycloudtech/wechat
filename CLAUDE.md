# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based customer journey analysis system for QuickCreator (an AI SEO content creation platform). The project analyzes WeChat sales conversations stored in MySQL, uses AI (via OpenAI/Volces API) to generate detailed customer journey reports, and creates visual summaries.

**Core workflow:**
1. Fetch WeChat chat messages from MySQL database (messages_zs table)
2. Send chat transcripts to LLM for analysis
3. Generate markdown reports analyzing sales conversations
4. Convert markdown to images with watermarks (for sharing)

## Architecture

### Data Pipeline

```
MySQL (AWS RDS) → Python scripts → LLM API → Markdown reports → PNG images
```

- **Database**: MySQL on AWS RDS us-east-2 (wechat_messages schema)
- **LLM providers**:
  - Volces (default, Chinese provider) - model `ep-20250210182716-gfw9b`
  - OpenAI (fallback) - model `gpt-5` (note: likely gpt-4 in production)
- **S3 storage**: AWS S3 bucket `qc-window` for WeChat HTML exports

### Key Tables

- `messages_zs`: Main message table with columns:
  - `chat_hash`: Conversation identifier
  - `chat_name`: Customer display name
  - `nick`: Sender nickname
  - `direction`: "发送" (sent) or received
  - `msgtype`: Message type (filtering for "文本"/text)
  - `timestamp`: Message timestamp
  - `msg`: Message content

### Core Modules

**utils.py**
- `call_model()`: LLM API wrapper (supports both Volces and OpenAI)

**customer_journey.ipynb**
- `analyze_buy_customer_journey()`: Analyzes successful sales conversations
- `fetch_messages()`: Queries MySQL for chat history in date range
- Generates detailed customer journey reports with stage analysis

**customer_journey_neg.ipynb**
- `analyze_no_buy_customer_journey()`: Analyzes unsuccessful sales leads
- Same structure but different analysis prompt

**from_mysql.ipynb**
- `summarize_chat_group()`: Aggregates multiple group chats
- Generates weekly digest of SEO community discussions
- `markdown_to_image()`: Converts markdown to watermarked PNG using imgkit

**get_files.ipynb**
- S3 file management using boto3
- Downloads WeChat HTML exports from S3

## Environment Setup

### Dependencies

```bash
pip install mysql-connector-python openai markdown imgkit boto3
```

**System requirement**: wkhtmltopdf must be installed for imgkit (HTML to image conversion)

```bash
# macOS
brew install wkhtmltopdf

# Linux
apt-get install wkhtmltopdf
```

### Database Connection

All notebooks connect to the same MySQL instance:
- Host: `ky-serverless-mysql.cluster-cy5scjl84t4x.us-east-2.rds.amazonaws.com`
- Port: 3306
- Database: `wechat_messages`
- User: `wechat_messages`

**Pattern**: Connection is established, used, then immediately closed in each analysis function.

### API Keys

Two LLM providers are configured:

1. **Volces** (primary, used in customer_journey.ipynb):
   - Base URL: `https://ark.cn-beijing.volces.com/api/v3`
   - Model: `ep-20250210182716-gfw9b`
   - Temperature: 0 (deterministic)

2. **OpenAI** (used in from_mysql.ipynb):
   - Model: `gpt-5`
   - Temperature: 1 (creative)

## Common Tasks

### Analyze a Customer Journey

```python
from customer_journey import analyze_buy_customer_journey

chat_hash = "c9dc84d56adeb3f003f8163974a77449"  # Customer identifier
start_date = "2024-01-01"
end_date = "2025-02-22"

md_report = analyze_buy_customer_journey(chat_hash, start_date, end_date)
# Output: ./buy_customer/购买客户_{customer_name}.md
```

### Batch Process Multiple Customers

See `customer_journey.ipynb` cells for batch processing pattern:

```python
# Get chat hashes for multiple customers
user_hashes = get_chat_hashes(connection, chat_names)

# Process each
for user_name, chat_hash in user_hashes.items():
    analyze_buy_customer_journey(chat_hash, start_date, end_date)
```

### Generate Weekly SEO Group Summary

```python
from from_mysql import summarize_chat_group, markdown_to_image

chat_hashes = [...]  # List of group chat identifiers
summary_md = summarize_chat_group(chat_hashes, "2025-09-13", "2025-09-19")

# Convert to shareable image
markdown_to_image(summary_md, "output.png")
```

### Download WeChat Exports from S3

```python
from get_files import list_files, download_file

bucket = "qc-window"
files = list_files(bucket)
download_file(bucket, "AI SEO学习交流2群.html", "./files/群聊.html")
```

## Prompt Engineering Patterns

### Customer Journey Analysis (Buying Customers)

The system uses a detailed Chinese prompt that instructs the LLM to:
1. Segment the conversation into stages
2. For each stage analyze:
   - Customer behavior and needs
   - Pre-sales consultant performance (highlights + improvement suggestions)
   - Key dialogue excerpts (with timestamps)
   - Bottleneck analysis (if stuck)
   - Success factors (if sale completed)
3. Provide global analysis with actionable recommendations

**Output format**: Markdown with H2 stage headers, blockquotes for dialogue

### Group Chat Summarization

The prompt categorizes discussions into:
- Technical issues
- Tool recommendations
- Best practices
- Optimization strategies
- Q&A
- QuickCreator product features
- Strategy discussions

**Format requirement**:
```markdown
## Category
* **Topic**: Discussion content *(Participants: name1, name2)*
```

**Key constraints**:
- Max 15 items
- No duplicate content across categories
- Participant names at end of each item
- No "discussed XXX" phrasing - preserve actual discussion content

## Message Processing Logic

**Direction mapping**:
- `direction = "发送"` → Label as "售前咨询" (pre-sales)
- Otherwise → Label as "客户" (customer)

**Message format normalization**:
Messages may contain `\n` with sender info in first line:
```python
s = msg.split("\n", 1)
if len(s) == 2:
    actual_msg = s[1]  # Use content after first newline
```

## Output File Conventions

- Customer journey reports: `./buy_customer/购买客户_{customer_name}.md`
- Group summaries: `output.png` (watermarked image)
- Markdown title format: `# {customer_name}` or `# AI SEO群交流精华 {date_range}`

## Security Notes

**WARNING**: This repository contains hardcoded credentials that should be migrated to environment variables:

- Database password
- LLM API keys (Volces and OpenAI)
- AWS credentials (ACCESS_KEY_ID, SECRET_ACCESS_KEY)

Before deploying or sharing this code:
1. Create `.env` file with credentials
2. Use `python-dotenv` to load them
3. Add `.env` to `.gitignore`
4. Rotate exposed credentials

## Data Privacy

This system processes sales conversations. When working with the codebase:
- Customer names and chat content are PII
- Generated reports (in `buy_customer/`) should not be committed to public repos
- S3 bucket contains WeChat exports with personal information
