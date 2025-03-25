# PlatformNexus Technical Design Document

## 1. Introduction

### 1.1 Purpose
This technical design document outlines the architecture, components, and implementation details for **PlatformNexus**, an innovative platform designed to enhance IT operations through natural language processing (NLP) interface, backed by LLMs and specialized AI agents to assist the engineers with their day-to-day tasks.

### 1.2 Scope
PlatformNexus aims to streamline IT operations by providing engineers with a natural language interface to interact with large language models (LLMs) and specialized AI agents. The platform will facilitate incident management, change request tracking, and application dependency evaluation through an intuitive user interface and powerful backend services.

### 1.3 System Overview
PlatformNexus integrates LLM with domain-specific agents to create a comprehensive solution for operations team. The system features:
- Natural language query processing for technical requests
- Real-time incident monitoring and management
- Specialized AI agents for common IT operational tasks
- Flexible backend LLM integration

### 1.4 Definitions, Acronyms, and Abbreviations
- **LLM**: Large Language Model
- **NLP**: Natural Language Processing
- **MCP**: Model Context Protocol
- **API**: Application Programming Interface
- **UI**: User Interface
- **CR**: Change Request

## 2. System Architecture

### 2.1 High-Level Architecture
PlatformNexus follows a modular, decoupled architecture:

- Architecture Diagram [https://github.com/ewfx/gaipl-troubleshooters/blob/main/artifacts/arch/PlatformNexus.png]

### 2.2 Component Description

#### 2.2.1 User Interface
The user interface provides engineers with a dashboard to interact with the system via natural language queries. Key UI components include:
- Query input panel with NLP capabilities
- Incident monitoring panel displaying recent incidents
- Agent selection panel featuring specialized AI agents
- Response display area
- History tracking for previous interactions

#### 2.2.3 Orchestration & AI Agents Management Layer
This layer manages the various AI agents and orchestrates their interactions. It includes:
- Agent selector
- MCP Client
- MCP Agent
- Context manager
- Response generator

#### 2.2.4 LLM Integration Layer
This layer provides abstraction for LLM backends and handles:
- LLM interfaces
- Prompt engineering
- Response processing

#### 2.2.5 Data Layer
This layer manages data and its operations:
- Application metrics Analyzer
- Application status Collector
- App Dependency dataset
- Change Requests dataset
- Incident dataset

### 2.3 Specialized Agent Descriptions

#### 2.3.1 Heal Agent
The Heal Agent specializes in automated remediation of common IT incidents. It can:
- Analyze incident data
- Recommend remediation steps
- Execute approved remediation workflows
- Generate Runbooks
- Learn from successful resolution patterns

#### 2.3.2 Change Request Tracker Agent
This agent finds a probable match between incident and change request:
- Parse Change Requests
- Parse Incidents
- Search for a probable matching CR for an incident

#### 2.3.3 Application Dependency Eval Agent
This agent analyzes application dependencies:
- Parse Upstream dependencies
- Parse downstream dependencies
- Determine if the incident affects the dependencies

## 3. Technical Implementation Details

### 3.1 Technology Stack

#### 3.1.1 Frontend
   - React 
   - Node.js
   - UI Rendering
   - API Request management

#### 3.1.2 Backend
   - Python 3.8+
   - Google GenAI SDK
   - OpenAi SDK
   - Flask

#### 3.1.3 AI and ML
   - API Calls to gemini-1.5-pro 
   - API Calls to OpenAi gpt-3.5-turbo
   - Prompt engineering and context management
   - Response parsing and validation

#### 3.1.4 Data Storage
   - Json files used for data storage 
   - Change Reqeusts and Incidents Data
   - MCP to provide data context to LLM
   


## 4. System Interactions and User Journeys

### 4.1 Incident Retrieval User Journey

1. **Query Submission**
   - User enters natural language query
   - Frontend validates and sends to backend

2. **Query Parsing and Routing**
   - System analyzes query intent
   - Identifies target agent or LLM
   - Enriches query with context

3. **LLM Processing**
   - Selected LLM processes the enriched query
   - Generates preliminary response

4. **Agent Processing**
   - Specialized agent applies domain knowledge
   - Enhances LLM response with specific actions
   - Generates actionable recommendations

5. **Response Delivery**
   - Response is formatted according to preferences
   - Data is enriched with references and visualizations
   - Final response returned to user

### 4.2 Heal Agent User Journey

1. **Incident Detection**
   - System receives alert from monitoring tools
   - Incident details are captured and classified

2. **Agent Assignment**
   - System determines appropriate agent
   - Heal Agent analyzes incident data

3. **Analysis and Recommendation**
   - Agent applies domain knowledge and past incidents
   - Generates recommendations for resolution

4. **Remediation**
   - User approves recommended actions
   - Agent executes approved remediation steps
   - Progress is tracked and reported

5. **Resolution and Learning**
   - Incident is marked as resolved
   - System updates knowledge base
   - Agent improves through feedback loop

### 4.3 Change Request Tracker User Journey

1. **Query Submission**
   - User enters natural language query
   - Frontend validates and sends query to LLM
   - Agent can check corelation between Incident and Change
   

2. **CR Affected Components**
   - Specilized Agent analyes Incident and CR 
   - Determines potential impact of CR
   - Identifies if a CR cuased the Incident
   - Agent identifies potential reason for application impact
   - Provides analysis on affected components
   - Provides possible remediation measures



## 6. Deployment and Operations

### 6.1 Deployment Strategy
- Containerized deployment using Docker
- Kubernetes orchestration for scaling
- CI/CD pipeline for automated testing and deployment
- Blue-green deployment for zero-downtime updates

### 6.2 Scaling Considerations
- Horizontal scaling for web and application layers
- Vertical scaling for database and LLM components
- Auto-scaling based on load metrics
- Geographic distribution for global availability

### 6.3 Monitoring and Alerting
- Real-time system health monitoring
- Performance metrics collection
- Anomaly detection for unusual patterns
- Alerting integration with on-call systems

### 6.4 Backup and Disaster Recovery
- Regular database backups
- Cross-region replication
- Defined recovery time objectives (RTO)
- Disaster recovery testing procedures

## 7. Future Roadmap

### 7.1 Short-term Enhancements
- Generation of Application Dependency Graph
- Using Heurisitic search for CRs and Incidents

### 7.2 Long-term Vision
- Autonomous incident resolution
- Predictive incident prevention

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| Agent | Specialized AI component designed for specific IT operational tasks |
| Incident | Unplanned outage or interruption or reduction in quality of IT services and applications |
| LLM | Large Language Model, AI system trained on text data |
| NLP | Natural Language Processing, AI field focused on human language |

## Appendix B: References

1. Google Gemini SDK [https://ai.google.dev/gemini-api/docs/sdks]
2. Anthropic Model Context Protocol SDK [https://github.com/modelcontextprotocol]
3. OpenAI SDK [https://platform.openai.com/docs/libraries?language=python]
4. React Developer Quick Start [https://react.dev/learn]
