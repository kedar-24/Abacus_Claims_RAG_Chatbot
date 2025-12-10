# 🏥 Claims Intelligence Assistant

> **A smart AI-powered tool to search and analyze insurance claims data using natural language.**

Ask questions like *"Show all denied claims"* or *"Why are claims being denied?"* and get instant answers with beautiful visualizations.

---

## 📑 Table of Contents
- [What Does This App Do?](#-what-does-this-app-do)
- [Requirements](#-requirements)
- [Installation Guide](#-installation-guide)
  - [Step 1: Install Required Software](#step-1-install-required-software)
  - [Step 2: Get a HuggingFace Token](#step-2-get-a-huggingface-token)
  - [Step 3: Download the Project](#step-3-download-the-project)
  - [Step 4: Run the Application](#step-4-run-the-application)
- [Using the Application](#-using-the-application)
- [Troubleshooting](#-troubleshooting)
- [For Developers](#-for-developers)

---

## 🎯 What Does This App Do?

This application helps you:
- **Search claims** - Find specific claims by patient, doctor, diagnosis, or status
- **Analyze patterns** - Understand why claims are being denied
- **Chat naturally** - Ask questions in plain English, no technical knowledge needed
- **Visualize data** - See charts and tables with claim statistics

### Example Questions You Can Ask:
- "Show all denied claims"
- "Find claims for Dr. Smith"
- "What are the top reasons for denial?"
- "Show me cardiology claims"
- "How many claims are pending?"

---

## 💻 Requirements

Before you start, you'll need:

| Requirement | What it is | Where to get it |
|-------------|-----------|-----------------|
| **Docker Desktop** | Software to run the app | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **HuggingFace Account** | Free AI service account | [huggingface.co/join](https://huggingface.co/join) |

---

## 📦 Installation Guide

### Step 1: Install Required Software

#### Install Docker Desktop

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Click **"Download for Windows"** (or Mac)
3. Run the installer (double-click the downloaded file)
4. Follow the installation wizard (click Next, Next, Install)
5. **Restart your computer** when prompted
6. After restart, open Docker Desktop from the Start menu
7. Wait for Docker to start (you'll see "Docker Desktop is running")

> ⚠️ **Windows Users**: If asked to install WSL 2, follow the prompts to install it.

---

### Step 2: Get a HuggingFace Token

The app uses AI from HuggingFace. You need a free account and token:

1. Go to [huggingface.co/join](https://huggingface.co/join)
2. Create a free account (email + password)
3. Verify your email
4. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
5. Click **"New token"**
6. Give it a name like "claims-app"
7. Select **"Read"** access
8. Click **"Generate"**
9. **Copy the token** (starts with `hf_`) - you'll need this later!

> 💡 **Keep this token safe!** Don't share it with others.

---

### Step 3: Download the Project

#### Option A: Download as ZIP (Easiest)
1. Click the green **"Code"** button on the GitHub page
2. Click **"Download ZIP"**
3. Extract the ZIP file to a folder (e.g., `C:\claims-assistant`)

#### Option B: Using Git (For tech-savvy users)
```bash
git clone https://github.com/kedar-24/Abacus_Claims_RAG_Chatbot.git
cd Abacus_Claims_RAG_Chatbot
```

---

### Step 4: Run the Application

#### 4.1 Configure Your Token

1. Find the file called `.env.example` in the project folder
2. **Copy** it and **rename** the copy to `.env` (just `.env`, nothing else)
3. Open `.env` with Notepad
4. Replace `your_huggingface_token_here` with your actual token:
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   ```
5. Save and close

#### 4.2 Start the Application

1. Open **Command Prompt** (search "cmd" in Windows Start menu)
2. Navigate to the project folder:
   ```
   cd C:\claims-assistant
   ```
   (Replace with your actual folder path)

3. Run this command:
   ```
   docker compose up --build
   ```

4. **Wait patiently** - first run takes 5-15 minutes to download and build everything

5. When you see messages about "backend" and "frontend" being ready, the app is running!

#### 4.3 Open the App

Open your web browser and go to:
```
http://localhost
```

🎉 **You should see the Claims Intelligence interface!**

---

## 🖥️ Using the Application

### The Interface

When you open the app, you'll see:
- A **chat area** in the middle
- An **input box** at the bottom to type questions
- A **Send button** to submit your question

### How to Use

1. **Type a question** in the input box
2. **Click Send** (or press Enter)
3. **Wait a few seconds** for the AI to respond
4. View the **results** - you'll see:
   - A text answer
   - Charts showing statistics
   - A table with claim details

### Sample Questions to Try

| Question | What You'll Get |
|----------|----------------|
| "Show all denied claims" | Table of all denied claims with reasons |
| "Hello, what can you do?" | A friendly explanation of capabilities |
| "What are the top denial reasons?" | Analysis of why claims are denied |
| "Find claims for Dr. Cooper" | Claims associated with that provider |
| "Show approved claims over $5000" | High-value approved claims |

---

## 🔧 Troubleshooting

### "Docker is not recognized"
- Make sure Docker Desktop is installed and running
- Try restarting your computer

### "Page won't load"
- Wait a few more minutes - the app takes time to start
- Check Docker Desktop is running (look for whale icon in taskbar)
- Try refreshing the page

### "Error generating answer"
- Check your HuggingFace token is correct in the `.env` file
- Make sure you have internet connection

### "The app is slow"
- First query takes longer (AI models loading)
- Subsequent queries should be faster

### Need More Help?
Check the Docker logs for error messages:
```
docker compose logs
```

---

## 📊 What's Inside

The app consists of:

| Component | What it does |
|-----------|-------------|
| **Frontend** | The visual interface you interact with |
| **Backend** | Processes your questions and finds answers |
| **AI Model** | Understands and answers your questions |
| **Database** | Stores the claims data |

---

## 🛑 Stopping the Application

To stop the app:
1. Go back to Command Prompt
2. Press `Ctrl + C`
3. Or run: `docker compose down`

---

## 🔄 Starting Again Later

After the first install, starting is easy:
```
cd C:\claims-assistant
docker compose up
```
(No need for `--build` after first time unless you made changes)

---

## 👨‍💻 For Developers

<details>
<summary>Click to expand developer documentation</summary>

### Local Development Setup

#### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Project Structure
```
├── backend/
│   ├── main.py          # FastAPI app
│   ├── rag.py           # RAG logic with LLM
│   ├── vector_store.py  # Vector embeddings
│   └── Dockerfile
├── frontend/
│   ├── src/App.jsx      # Main React component
│   ├── nginx.conf       # Production server config
│   └── Dockerfile
├── docker-compose.yml   # Container orchestration
└── .env                 # Environment variables
```

### Technologies Used
- **Backend**: Python, FastAPI, LangChain, HuggingFace
- **Frontend**: React, Tailwind CSS, Recharts
- **AI**: Llama 3.2, Sentence Transformers
- **Infrastructure**: Docker, Nginx

</details>

---

## 🚀 Future Improvements

### Smarter AI
- **Better AI Models** – Use more powerful AI for more accurate answers
- **Document Upload** – Scan and analyze claim forms, receipts, medical docs
- **Faster Responses** – Show answers as they're being generated (streaming)
- **Offline Mode** – Run AI locally without internet for privacy

### New Features
| Feature | What It Does |
|---------|--------------|
| **User Accounts** | Login system with different access levels |
| **Search History** | Save and revisit your past searches |
| **Export Data** | Download results as Excel or PDF |
| **Email Reports** | Get daily/weekly claim summaries automatically |
| **Alerts** | Get notified when denial rates spike |
| **Date Filters** | Ask "claims from last week" and it understands |

### Better Experience
- 🎤 **Voice Search** – Ask questions by speaking
- 💡 **Smart Suggestions** – Auto-complete as you type
- 🌙 **Dark Mode** – Easy on the eyes
- 📱 **Mobile-Friendly** – Works on phones and tablets
- ⌨️ **Keyboard Shortcuts** – Quick access for power users

### Security
- 🔒 Secure data encryption
- 🛡️ Protection against misuse
- 📋 Activity logging for compliance

---

## 📈 How This Can Scale

### Handle More Users
As your team grows, the app can scale:

| Need | Solution |
|------|----------|
| **More users** | Add more servers behind a load balancer |
| **Faster searches** | Use specialized databases (Pinecone, PostgreSQL) |
| **Quicker responses** | Add caching to remember common queries |
| **Global access** | Deploy to cloud (AWS, Google Cloud, Azure) |

### Upgrade Path

| Phase | What to Do | Result |
|-------|-----------|--------|
| **1** | Add caching | 50-70% faster repeated searches |
| **2** | Use cloud database | Handle millions of claims |
| **3** | Deploy to cloud | Access from anywhere |
| **4** | Add monitoring | Track performance and errors |

### Cloud Options
| Platform | Best For | Est. Cost |
|----------|----------|-----------|
| Railway / Render | Getting started | $20-50/mo |
| AWS / Google Cloud | Enterprise scale | $50-150/mo |
| Self-hosted | Full control | Varies |

---

## 📜 License

This project is for educational purposes.

---

**Made with ❤️ for easier claims management**
