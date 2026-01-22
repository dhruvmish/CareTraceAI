# CareTrace AI - System Architecture

## Overview

CareTrace AI is a **multi-agent system** designed around the principle of **separation of concerns**. Each agent has a single, well-defined responsibility and communicates only through shared memory (Qdrant vector database).

---

## Agent Architecture

### 1. IngestionAgent
**File:** `src/agents/ingestion_agent.py`

**Responsibility:** Convert raw inputs into structured semantic events

**Inputs:**
- Audio files (WAV, MP3)
- Prescription images (JPG, PNG)
- Manual text entries

**Processing:**
- Audio → Whisper transcription → symptom text
- Image → Tesseract OCR → drug name extraction
- Manual → structured event creation

**Output:**
```python
{
    "patient_id": "patient_001",
    "event_type": "symptom" | "prescription",
    "text": "transcribed or OCR text",
    "timestamp": "2024-01-20T10:30:00",
    "drugs": ["Aspirin", "Metformin"],  # for prescriptions
    "metadata": {
        "source": "audio" | "prescription_image" | "manual_entry",
        "filename": "symptom_001.wav"
    }
}
```

**Key Methods:**
- `process_audio(audio_path, patient_id)` → event dict
- `process_prescription(image_path, patient_id)` → event dict
- `create_manual_event(...)` → event dict

**Does NOT:**
- Store data (delegates to MemoryAgent)
- Validate drug interactions
- Analyze patterns

---

### 2. MemoryAgent
**File:** `src/agents/memory_agent.py`

**Responsibility:** Single source of truth for all Qdrant operations

**Core Functions:**
1. **Storage**
   - `store_event(event)` → stores patient events
   - `store_drug_interaction(interaction)` → stores known interactions
   - `store_synthetic_patient(profile)` → stores population data

2. **Retrieval**
   - `get_patient_history(patient_id, event_type, limit)` → filtered events
   - `get_all_drug_interactions()` → interaction database

3. **Semantic Search**
   - `search_similar_symptoms(query_text, patient_id, limit)` → similar events
   - `search_similar_patients(query_text, limit)` → similar profiles

**Embedding Model:**
- sentence-transformers/all-MiniLM-L6-v2
- 384-dimensional vectors
- Cosine similarity for matching

**Qdrant Collections:**

#### Collection 1: `patient_events`
```python
{
    "vector": [384-dim embedding],
    "payload": {
        "patient_id": "patient_001",
        "event_type": "symptom",
        "text": "having headaches...",
        "timestamp": "2024-01-20T10:30:00",
        "drugs": [],
        "metadata": {...}
    }
}
```

#### Collection 2: `drug_interactions`
```python
{
    "vector": [384-dim embedding],
    "payload": {
        "drug_a": "Warfarin",
        "drug_b": "Aspirin",
        "severity": "severe",
        "explanation": "Increased bleeding risk...",
        "evidence": "FDA database"
    }
}
```

#### Collection 3: `synthetic_patient_profiles`
```python
{
    "vector": [384-dim embedding],
    "payload": {
        "patient_id": "synthetic_042",
        "age": 58,
        "conditions": ["Diabetes", "Hypertension"],
        "medications": ["Metformin", "Lisinopril"],
        "symptoms": ["headache", "fatigue"],
        "summary": "Age 58 with Diabetes..."
    }
}
```

**Does NOT:**
- Process raw inputs (delegates to IngestionAgent)
- Make safety decisions
- Analyze patterns

---

### 3. SafetyAgent
**File:** `src/agents/safety_agent.py`

**Responsibility:** Detect drug-drug interactions

**Workflow:**
```
1. User wants to add new drug
2. SafetyAgent queries MemoryAgent for patient's current drugs
3. SafetyAgent queries MemoryAgent for interaction database
4. Checks if new drug + current drug pairs exist in database
5. Returns alerts with severity and evidence
```

**Key Method:**
```python
check_new_medication(patient_id, new_drug) -> {
    "safe": False,
    "new_drug": "Warfarin",
    "current_drugs": ["Aspirin", "Metformin"],
    "interactions": [
        {
            "drug_a": "Warfarin",
            "drug_b": "Aspirin",
            "severity": "severe",
            "explanation": "...",
            "evidence": "..."
        }
    ],
    "max_severity": "severe",
    "message": "Found 1 severe interaction"
}
```

**Does NOT:**
- Store data directly in Qdrant
- Make prescription decisions
- Recommend alternative medications

---

### 4. PatternAgent
**File:** `src/agents/pattern_agent.py`

**Responsibility:** Detect recurring symptom patterns over time

**Analysis Types:**

1. **Recurring Symptoms**
   - Extract keywords from symptom reports
   - Count occurrences across timeline
   - Flag patterns that repeat ≥2 times

2. **Medication Correlation**
   - Check if symptom timing aligns with new prescriptions
   - Look for temporal proximity (within 7 days)
   - Suggest potential adverse reactions

**Key Methods:**
```python
detect_recurring_symptoms(patient_id) -> {
    "has_patterns": True,
    "recurring_symptoms": [
        {
            "symptom_keyword": "headache",
            "occurrence_count": 3,
            "dates": ["2024-01-15", "2024-01-18", "2024-01-20"],
            "reports": ["full text of each report"]
        }
    ]
}

correlate_with_medications(patient_id, symptom_keyword) -> {
    "correlation_found": True,
    "correlations": [
        {
            "symptom_text": "headache started...",
            "symptom_date": "2024-01-18",
            "prescription_drugs": ["Ibuprofen"],
            "prescription_date": "2024-01-15",
            "days_apart": 3
        }
    ]
}
```

**Does NOT:**
- Diagnose conditions
- Recommend treatments
- Store new data

---

### 5. PopulationAgent
**File:** `src/agents/population_agent.py`

**Responsibility:** Find similar patients for evidence-based insights

**Workflow:**
```
1. Build summary of current patient's profile
   - Current medications
   - Recent symptoms
   - Known conditions (from history)

2. Embed summary using same model as MemoryAgent

3. Search synthetic_patient_profiles collection

4. Return top-K similar patients with scores

5. Analyze population-level patterns:
   - Common medications among similar patients
   - Frequent symptoms
   - Shared conditions
```

**Key Methods:**
```python
find_similar_patients(patient_id, limit=3) -> {
    "found_similar": True,
    "similar_patients": [
        {
            "patient_id": "synthetic_042",
            "similarity_score": 0.87,
            "age": 56,
            "conditions": ["Diabetes"],
            "medications": ["Metformin"],
            "symptoms": ["headache", "fatigue"]
        }
    ]
}

get_population_insights(patient_id, focus="medications") -> {
    "insight_type": "medications",
    "common_medications": [
        {"drug": "Metformin", "frequency": 8},
        {"drug": "Lisinopril", "frequency": 6}
    ],
    "message": "Among 10 similar patients..."
}
```

**Does NOT:**
- Make treatment recommendations
- Predict outcomes
- Store patient data

---

## Data Flow Diagram

```
┌─────────────────┐
│   User Input    │
│ (Audio/Image)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│     IngestionAgent          │
│ - Transcribe audio          │
│ - Extract text from image   │
│ - Structure event           │
└────────┬────────────────────┘
         │
         ▼ event dict
┌─────────────────────────────┐
│      MemoryAgent            │
│ - Embed text                │
│ - Store in Qdrant           │
└─────────────────────────────┘
         │
         │ (Data stored in Qdrant)
         │
         ▼
┌──────────────────────────────────────────┐
│        User Requests Analysis            │
└──────────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┬────────────────┐
         │                  │                  │                │
         ▼                  ▼                  ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ SafetyAgent  │  │ PatternAgent │  │ Population   │  │  UI Display  │
│              │  │              │  │ Agent        │  │              │
│ Queries      │  │ Queries      │  │              │  │ Shows all    │
│ MemoryAgent  │  │ MemoryAgent  │  │ Queries      │  │ results      │
│ for drugs    │  │ for symptoms │  │ MemoryAgent  │  │              │
│              │  │              │  │ for similar  │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌────────────────────────────────────────────────────┐
│              Analysis Results                      │
│  - Drug interaction alerts                         │
│  - Recurring symptom patterns                      │
│  - Similar patient insights                        │
└────────────────────────────────────────────────────┘
```

---

## Why This Architecture?

### 1. Separation of Concerns
Each agent has ONE job:
- IngestionAgent: input processing
- MemoryAgent: data storage/retrieval
- SafetyAgent: interaction checking
- PatternAgent: temporal analysis
- PopulationAgent: similarity matching

### 2. Testability
Agents can be tested in isolation:
```python
# Test SafetyAgent without UI or database
memory_mock = MockMemoryAgent()
safety = SafetyAgent(memory_mock)
result = safety.check_new_medication("patient_001", "Warfarin")
assert result["safe"] == False
```

### 3. Scalability
Add new agents without modifying existing ones:
- **CostAgent**: Estimate medication costs
- **AdherenceAgent**: Track medication compliance
- **RiskAgent**: Calculate fall/bleeding risk scores

### 4. Maintainability
Clear boundaries make debugging easier:
- OCR failing? → Check IngestionAgent
- Wrong similarity results? → Check MemoryAgent embeddings
- Missed interaction? → Check SafetyAgent logic + interaction database

---

## Qdrant Usage Patterns

### 1. Insert with Vector
```python
# MemoryAgent
embedding = self.encoder.encode(text).tolist()
point = PointStruct(
    id=uuid.uuid4(),
    vector=embedding,
    payload=event_data
)
client.upsert(collection_name="patient_events", points=[point])
```

### 2. Filtered Retrieval (No Vector Needed)
```python
# Get all prescriptions for patient_001
filter_obj = Filter(
    must=[
        FieldCondition(key="patient_id", match=MatchValue(value="patient_001")),
        FieldCondition(key="event_type", match=MatchValue(value="prescription"))
    ]
)
results = client.scroll(
    collection_name="patient_events",
    scroll_filter=filter_obj,
    limit=100
)
```

### 3. Semantic Search with Filter
```python
# Find similar symptoms for specific patient
query_embedding = self.encoder.encode("chest pain").tolist()
filter_obj = Filter(
    must=[
        FieldCondition(key="patient_id", match=MatchValue(value="patient_001")),
        FieldCondition(key="event_type", match=MatchValue(value="symptom"))
    ]
)
results = client.search(
    collection_name="patient_events",
    query_vector=query_embedding,
    query_filter=filter_obj,
    limit=5
)
```

---

## Error Handling

Every agent implements graceful degradation:

### IngestionAgent
- Audio file not found → FileNotFoundError with clear message
- Whisper fails → Exception with transcription error details
- OCR produces empty text → Returns event with empty drug list

### MemoryAgent
- Qdrant connection fails → ConnectionError with troubleshooting steps
- Embedding fails → Exception with model loading error
- Empty search results → Returns empty list (not error)

### SafetyAgent
- No patient history → Returns "safe: true, no medications on record"
- No interactions found → Returns "safe: true"
- Interaction database empty → Logs warning, continues

### PatternAgent
- Insufficient data (< 2 symptoms) → Returns "has_patterns: false"
- No temporal correlation → Returns "correlation_found: false"

### PopulationAgent
- No patient data → Returns "found_similar: false, insufficient data"
- All similarities below threshold → Returns list but flags low confidence
- Synthetic population empty → Returns "found_similar: false"

---

## Performance Considerations

### Embedding Caching
MemoryAgent loads model once and reuses:
```python
@st.cache_resource
def init_agents():
    memory = MemoryAgent()  # Loads embedding model once
    ...
```

### Batch Operations
When loading demo data:
```python
# Batch upsert instead of one-by-one
points = [create_point(event) for event in batch]
client.upsert(collection_name="patient_events", points=points)
```

### Limit Query Results
Always set reasonable limits:
```python
# Don't retrieve entire history
history = memory.get_patient_history(patient_id, limit=50)
```

---

## Security & Privacy

### Demo Environment
- All data stored locally
- No external API calls (except Qdrant)
- No PHI leaves local machine

### Production Considerations
- HIPAA-compliant Qdrant deployment
- Encryption at rest and in transit
- Access control and audit logging
- De-identification of patient data before similarity matching

---

This architecture is designed for **clarity**, **safety**, and **scalability**—from hackathon demo to production healthcare system.