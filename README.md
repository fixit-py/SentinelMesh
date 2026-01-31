# SentinelMesh

**SentinelMesh** is an IoT **Trust, Reliability, and Data Quality Engine** built on top of real LoRaWAN telemetry.  
Instead of focusing only on sensor values, SentinelMesh evaluates **how much the data itself can be trusted**.

It is designed for:
- IoT operations teams  
- Network engineers  
- Infrastructure and facilities monitoring  
- Reliability and maintenance planning  

---

## Why SentinelMesh?

Most IoT dashboards answer:

> “What is the sensor reading?”

SentinelMesh answers:

> “Should I trust this sensor, this gateway, and this data?”

The system analyzes:
- Telemetry consistency  
- RF stability  
- Confidence trends over time  
- Data completeness  
- Gateway reliability  
- Maintenance risk  

All insights are derived **strictly from observed data** — no assumptions, no hallucinations.

---

## Core Capabilities

### Unified Telemetry Normalization
Raw LoRaWAN uplinks from multiple vendors are normalized into a single, consistent event schema:
- Device metadata  
- Measurements  
- RF metrics (RSSI, SNR)  
- Network parameters  
- Confidence inputs  

---

### Confidence & Trust Scoring
Each event is assigned a confidence score based on:
- Missing or incomplete telemetry  
- RF quality and stability  
- Network behavior (frame counters, ADR)  

Confidence trends are tracked over time per device.

---

### Automated Insights Engine
SentinelMesh automatically detects and explains:
- Devices with poor battery telemetry  
- Degrading confidence over time  
- Incomplete or unreliable telemetry  
- Devices that are unreliable despite good RF  

All insights are explainable and reproducible.

---

### Gateway Reliability Analysis
Gateways are analyzed for:
- Average confidence of traffic handled  
- RSSI variance (RF instability)  
- Event volume  

This allows identification of unstable or degraded gateways affecting multiple devices.

---

### Predictive Maintenance Scoring
Devices are ranked by maintenance risk using:
- Battery reporting quality  
- Confidence degradation  
- RF instability  
- Data completeness  

This supports preventive maintenance instead of reactive alerts.

---

### Trust Replay (Time Flow)
A replay interface allows users to:
- Scrub through time  
- Observe confidence changes  
- See when devices or gateways began degrading  
- Perform operational forensics  

---

### Interactive Query Interface
Users can ask supported, data-backed questions, such as:
- What devices exist?  
- What devices are faulty?  
- Which gateway does Door Sensor 08 use?  
- When was the last data received from Temp Sensor 03?  
- Where is Temp Sensor 03?  
- Which gateways are unstable?  

Only questions that can be answered from the dataset are supported.

---

## Example Questions Supported
- What devices exist?  
- What gateways exist?  
- What devices are faulty?  
- Which gateway does Door Sensor 08 use?  
- When was the last data received from Temp Sensor 03?  
- Where is Temp Sensor 03?  
- How many messages has Temp Sensor 03 sent?  
- Which gateways are unstable?  
- Which device needs maintenance?  

---

## Tech Stack
- Python  
- Streamlit – interactive dashboard  
- Pandas – data processing  
- Altair – analytical plotting  
- JSONL – event storage  

No external services, no ML dependencies, no cloud lock-in.

---

## Project Structure

dataset/
├── app.py                    # Streamlit application
├── engine.py                 # Core analytics & metrics
├── query_engine.py           # Deterministic query system
├── enriched_events.jsonl     # Unified event dataset
├── logo.png                  # SentinelMesh logo
└── README.md

## How to Run
1. Install dependencies
pip install streamlit pandas altair

2. Run the application
streamlit run app.py


