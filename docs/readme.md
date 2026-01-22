# 🏥 CareTrace AI

**A Production-Grade Multi-Agent Healthcare Safety System**

CareTrace AI is a Qdrant-powered multi-agent system that prevents medication harm by maintaining a longitudinal, multimodal record of patient-reported symptoms and prescriptions, generating evidence-backed medication safety alerts across fragmented care journeys.

---

## 🎯 Problem Statement

**Healthcare is fragmented.** Patients see multiple doctors, fill prescriptions at different pharmacies, and report symptoms across disconnected systems. This fragmentation leads to:

- **Missed drug-drug interactions** (300,000+ preventable adverse events annually in the US alone)
- **Repeated symptom patterns going unnoticed** (patients suffer unnecessarily)
- **Lack of population-level evidence** (physicians treat in isolation)

**CareTrace AI bridges these gaps** by creating a unified, AI-powered memory layer that:
1. **Listens** to patient symptom reports (audio transcription)
2. **Reads** prescription images (OCR)
3. **Remembers** everything using semantic vector search (Qdrant)
4. **Alerts** on drug interactions, symptom patterns, and population insights

---

## 🤖 Why This is a Multi-Agent System

CareTrace AI is **genuinely multi-agent** because:

### Each Agent Has a Single Responsibility
- **IngestionAgent**: Converts audio → text, images → drugs
- **MemoryAgent**: Stores & retrieves from Qdrant (single source of truth)
- **SafetyAgent**: Checks drug interactions
- **PatternAgent**: Detects symptom patterns over time
- **PopulationAgent**: Finds similar patients

### Agents Are Independent
- Each lives in its own Python file
- No agent directly calls another agent
- Agents only communicate through **shared memory (Qdrant)**

### Coordination via Shared Memory
```
IngestionAgent → MemoryAgent (stores event)
                      ↓
SafetyAgent queries MemoryAgent for patient drugs
PatternAgent queries MemoryAgent for symptom history
PopulationAgent queries MemoryAgent for similar patients
```

This architecture is:
- **Scalable** (add new agents without touching existing ones)
- **Testable** (each agent can be tested in isolation)
- **Maintainable** (clear boundaries of responsibility)

---

## 🗄️ Why Qdrant is Essential

**Qdrant is NOT just a database—it's the brain of CareTrace AI.**

### 1. Semantic Search Over Symptoms
Traditional databases match keywords. Qdrant matches **meaning**:
- Query: "chest pain when walking"
- Matches: "pressure in chest during exercise", "angina while climbing stairs"

### 2. Vector Similarity for Patient Matching
Find patients with similar medical profiles using embeddings:
- Input: "Age 58, Diabetes, taking Metformin and Lisinopril, headaches"
- Output: 3 most similar patients from synthetic population

### 3. Filtered Retrieval
Get patient history with complex filters:
```python
# All prescriptions for patient_001 in last 30 days
memory.get_patient_history(
    patient_id="patient_001",
    event_type="prescription"
)
```

### 4. Long-Term Memory
- Persistent storage across sessions
- Handles multimodal data (text embeddings from audio + OCR)
- Scales from demo (5 patients) to production (millions)

**Without Qdrant, we'd need:**
- Separate database for patient records
- Separate vector database for embeddings
- Complex joins and queries
- No semantic search capabilities

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│  (Patient Timeline, Upload, Safety Check, Patterns)     │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent Layer                           │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Ingestion    │  │  Safety      │  │  Pattern     │ │
│  │ Agent        │  │  Agent       │  │  Agent       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │          │
│         └─────────────────┼─────────────────┘          │
│                           │                            │
│                  ┌────────▼────────┐                   │
│                  │  Memory Agent   │                   │
│                  │ (Qdrant Wrapper)│                   │
│                  └────────┬────────┘                   │
└───────────────────────────┼──────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Qdrant Vector DB                     │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ patient_events   │  │ drug_interactions│           │
│  │ (symptoms + rx)  │  │ (curated pairs)  │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  ┌──────────────────────────────────┐                 │
│  │ synthetic_patient_profiles       │                 │
│  │ (population for similarity)      │                 │
│  └──────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Qdrant (local Docker or cloud)
- Tesseract OCR installed on system

### 1. Clone and Install
```bash
git clone <repository-url>
cd caretrace-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Qdrant credentials
```

For local Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Initialize System
```bash
# Setup Qdrant collections
python scripts/setup_qdrant.py

# Generate synthetic patient population
python scripts/generate_synthetic_patients.py

# Load demo data and drug interactions
python scripts/ingest_demo_data.py
```

### 4. 🧑 HUMAN ACTIONS REQUIRED

#### Record Audio Files (Optional but Recommended)
```bash
# Record 8-10 short audio clips (10-20 seconds) in English or Hindi
# Examples:
# - "I have been having headaches for 3 days"
# - "Feeling dizzy after taking my morning medication"
# - "Stomach pain started yesterday"

# Save as: data/audio/symptom_001.wav, symptom_002.wav, etc.
```

#### Take Prescription Photos (Optional but Recommended)
```bash
# Take clear photos of handwritten prescriptions
# Must contain drug names and dosages
# Save as: data/prescriptions/rx_001.jpg, rx_002.jpg, etc.
```

**Note:** The system works without these files using demo data, but real audio/images demonstrate full capabilities.

### 5. Run Application
```bash
streamlit run src/ui/app.py
```

Navigate to `http://localhost:8501`

---

## 🎮 Demo Walkthrough

### Step 1: Select a Patient
Choose from 5 demo patients in the sidebar:
- Sarah Johnson (Diabetes + Hypertension)
- Rajesh Kumar (Heart Disease)
- Maria Garcia (Asthma)
- Ahmed Ali (Chronic Pain)
- Li Wei (Depression)

### Step 2: View Timeline
See the patient's complete history:
- 🗣️ Symptom reports (from audio transcription)
- 💊 Prescriptions (from OCR)
- Timestamps showing care journey

### Step 3: Check Medication Safety
Try adding a new medication:
1. Go to "Safety Check" tab
2. Enter: `Warfarin`
3. Click "Run Safety Check"
4. See interaction alerts with evidence

**Example Result:**
```
⚠️ SEVERE Interaction Found

Drugs: Warfarin ↔ Aspirin
Explanation: Increased risk of bleeding. Both drugs affect blood clotting.
Evidence: FDA drug interaction database
```

### Step 4: Analyze Patterns
1. Go to "Pattern Analysis" tab
2. Click "Analyze Patterns"
3. See recurring symptoms flagged:
   - "headache" appeared 3 times
   - Dates and full reports shown
   - Correlation with medication timing

### Step 5: Find Similar Patients
1. Go to "Population Insights" tab
2. Click "Find Similar Patients"
3. See 3 most similar patients from synthetic population:
   - Similarity scores (vector distance)
   - Common medications
   - Shared conditions

---

## 🛡️ Healthcare Safety & Ethics

### What CareTrace AI IS:
✅ A **safety alert system** for medication interactions  
✅ A **memory tool** for tracking symptom patterns  
✅ A **population insights** platform for evidence-based care  

### What CareTrace AI is NOT:
❌ NOT a diagnostic system  
❌ NOT a prescription system  
❌ NOT an autonomous decision maker  
❌ NOT a replacement for physicians  

### Design Principles:
1. **Human-in-the-Loop**: All alerts are recommendations, not commands
2. **Explainability**: Every alert shows evidence and reasoning
3. **Transparency**: Clear about limitations and data sources
4. **Privacy**: Patient data never leaves local environment in demo

### Hard Boundaries:
- No medical image diagnosis
- No symptom image embeddings
- No black-box ML predictions
- No overclaiming medical capability

---

## 📊 Technical Highlights

### Multimodal Input Processing
- **Audio → Text**: Whisper transcription (supports Hindi + English)
- **Image → Drugs**: Tesseract OCR with pattern extraction
- **Text → Vectors**: sentence-transformers embeddings (384-dim)

### Semantic Search Examples
```python
# Find similar symptoms
memory.search_similar_symptoms(
    query_text="chest pain during exercise",
    limit=5
)

# Find similar patients
population.find_similar_patients(
    patient_id="patient_001",
    limit=3
)
```

### Agent Coordination
```python
# SafetyAgent uses MemoryAgent (doesn't access Qdrant directly)
class SafetyAgent:
    def __init__(self, memory_agent):
        self.memory = memory_agent
    
    def check_new_medication(self, patient_id, new_drug):
        current_drugs = self.memory.get_patient_history(...)
        interactions = self.memory.get_all_drug_interactions()
        # Analyze and return alerts
```

---

## 🔮 Future Enhancements

### Integration with Real Medical APIs
- **RxNorm** for standardized drug names
- **FDA API** for live interaction database updates
- **ICD-10 codes** for condition mapping

### Advanced NER & Medical NLP
- Replace regex drug extraction with medical NER models
- Extract dosages, frequencies, routes of administration
- Identify symptom severity and temporal patterns

### Scalability Improvements
- Horizontal scaling with Qdrant Cloud
- Batch ingestion for large patient populations
- Real-time alerting with webhooks

### Enhanced UI
- Interactive timeline visualization (D3.js)
- Export patient reports as PDF
- Multi-language support (expand beyond Hindi/English)

---

## 📁 Project Structure

```
caretrace-ai/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── data/                        # Data directory
│   ├── audio/                   # Voice recordings (HUMAN)
│   ├── prescriptions/           # Prescription images (HUMAN)
│   └── synthetic_patients/      # Generated population
├── src/
│   ├── config.py                # Configuration
│   ├── agents/
│   │   ├── ingestion_agent.py   # Audio + OCR processing
│   │   ├── memory_agent.py      # Qdrant wrapper
│   │   ├── safety_agent.py      # Drug interaction checks
│   │   ├── pattern_agent.py     # Symptom pattern detection
│   │   └── population_agent.py  # Similar patient finder
│   ├── db/
│   │   ├── qdrant_client.py     # Qdrant connection
│   │   └── collections.py       # Collection schemas
│   ├── ui/
│   │   └── app.py               # Streamlit interface
│   └── utils/
│       ├── logger.py            # Structured logging
│       └── helpers.py           # Utility functions
├── scripts/
│   ├── setup_qdrant.py          # Initialize collections
│   ├── ingest_demo_data.py      # Load demo patients
│   └── generate_synthetic_patients.py  # Create population
└── docs/
    ├── architecture.md          # Detailed system design
    └── ethics_and_limits.md    # Safety boundaries
```

---

## 🙏 Acknowledgments

- **Qdrant** for vector database infrastructure
- **OpenAI Whisper** for audio transcription
- **Tesseract OCR** for prescription image processing
- **Streamlit** for rapid UI development
- **Sentence Transformers** for semantic embeddings

---

## 📄 License

MIT License (for demo purposes)

---

## 🤝 Contributing

This is a hackathon/competition project. For production use, please:
1. Integrate with real medical databases (RxNorm, FDA)
2. Implement HIPAA-compliant storage
3. Add comprehensive testing and validation
4. Conduct clinical trials and safety audits

---

**Built with ❤️ for safer healthcare**