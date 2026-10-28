# Version 2.0 Event System Documentation

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Package**: `backend/app/v2/events/`  
**Date**: 2026-08-03  

---

## 1. Overview

The Event System provides a local, in-memory asynchronous publish/subscribe event bus requiring zero external infrastructure dependencies (No Redis, RabbitMQ, Kafka, or Cloud Event Grid).

---

## 2. Event Models & Subsystems

- `BaseEvent`: Base model carrying `event_id`, `event_type`, `timestamp`, `correlation_id`, `payload`.
- **Supported Events**:
  - `AgentStarted`, `AgentCompleted`, `AgentFailed`
  - `WorkflowStarted`, `WorkflowCompleted`
  - `TaskCreated`, `TaskCompleted`, `TaskFailed`
- `EventStore`: In-memory thread-safe event history log.
- `EventBus`: In-memory topic subscriber and publisher dispatcher.
- `EventPublisher`: Helper wrapper publishing events onto the bus.
