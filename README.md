# 🧠 Agentic Coding RAG | Smart Documentation Assistant 🔀

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-Workflow-purple?logo=databricks&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-black?logo=pinecone&logoColor=white)
![Cohere](https://img.shields.io/badge/Cohere-Command_R-teal)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange)

> **Stop searching. Start asking.** > Transform your fragmented, AI-generated technical documentation (architecture specs, design notes, tasks) into a unified, interactive, and highly intelligent knowledge graph. 

Built as part of an advanced AI development course, this project enables developers to query their project's "brain" directly. Instead of manually `CTRL+F`-ing through dozens of Markdown files to find a single architectural decision, you simply ask the system in natural language.

---

## 🎯 The Core Innovation

This isn't a basic RAG pipeline. The system utilizes an **Event-Driven Workflow** with an autonomous LLM router to handle varying query complexities:

* 🔍 **Semantic Search (Pinecone):** For nuanced technical questions, feature explanations, and conceptual queries.
* 📊 **Structured Extraction (JSON):** For exact programmatic queries requiring full lists, summaries, or specific architectural decisions.
* 🔀 **Intelligent Router:** An LLM-powered selector that analyzes user intent and dynamically routes the query to the optimal data source.

## 🏗️ Architecture & Engine

The project is modularly structured into three distinct engines:

1.  `prepare.py` **(The Vectorizer):** Ingests raw `.md` files, chunks the text, generates high-quality embeddings using **Cohere**, and indexes them into **Pinecone**.
2.  `extract_data.py` **(The Extractor):** Parses documentation to identify and extract strict, typed entities (rules, decisions, open bugs) using **Pydantic** schemas, saving them as structured JSON.
3.  `agent.py` **(The Orchestrator):** The event-driven workflow engine. It validates inputs, triggers the LLM router, retrieves context, and synthesizes a precise response via a clean **Gradio** interface.

*(💡 Note: Insert your Mermaid flow-chart or workflow HTML screenshot here!)*

---
## 📁 Repository Structure

```text
📦 agentic-coding-rag
 ┣ 📂 bakery-rag/           # Raw Markdown documentation
 ┣ 📜 agent.py              # Main Workflow and Gradio UI
 ┣ 📜 prepare.py            # Vector DB indexing script
 ┣ 📜 extract_data.py       # Structured JSON extraction script
 ┣ 📜 extracted_data.json   # Output from the extraction
 ┣ 📜 my_workflow.html      # Interactive LlamaIndex workflow graph
 ┣ 📜 .env                  # API Keys (Ignored by Git)
 ┣ 📜 .gitignore
 ┣ 📜 pyproject.toml        # Dependencies (uv)
 ┗ 📜 README.md             # Project documentation
## ⚙️ Quick Start

### 1. Prerequisites
* Python 3.10+
* [uv](https://github.com/astral-sh/uv) (highly recommended) or `pip`
* API Keys for **Cohere** and **Pinecone**

### 2. Environment Setup
Create a `.env` file in the project root:
```env
COHERE_API_KEY=your_cohere_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
3. Install Dependencies
Bash
uv add python-dotenv llama-index llama-index-vector-stores-pinecone llama-index-embeddings-cohere llama-index-llms-cohere pinecone-client gradio pydantic llama-index-utils-workflow
4. Prime the Database
Before chatting, you must build the knowledge base:

Bash
# 1. Populate the Pinecone Vector DB
uv run prepare.py

# 2. Extract structured JSON insights
uv run extract_data.py
5. Launch the Agent
Bash
uv run agent.py
Navigate to http://127.0.0.1:7860 in your browser to interact with the UI.

🗣️ See It In Action (Recommended Queries)
Test the dynamic routing capabilities with these exact prompts:

Targeting the Vector DB (Semantic):

"What is the primary color defined in the UI guidelines?"
(Expects: A point-specific extraction from Pinecone).

Targeting the JSON Data (Structured):

"Can you list all the open bugs?"
(Expects: An exhaustive list generated from the extracted JSON schema).

Testing the Validator:

"Hi" or "What"
(Expects: Immediate pipeline halt with a validation warning, saving API calls).

🎓 Reflection & Lessons Learned
🛡️ Hallucination Prevention: By leveraging strict synthesis prompts, the Agent effectively uses the retrieved context to admit when information is missing rather than guessing.

🧠 Routing Accuracy: The LLMSingleSelector demonstrates remarkable accuracy in distinguishing between abstract conceptual questions and hard-data list extraction.

🚀 Future Enhancements: * Implement webhooks for real-time sync between local Markdown updates and Pinecone.

Expand Pydantic schemas to track developer task assignments.

Integrate Git-history parsing to enable time-dependent queries (e.g., "What decisions were changed in the last 48 hours?").