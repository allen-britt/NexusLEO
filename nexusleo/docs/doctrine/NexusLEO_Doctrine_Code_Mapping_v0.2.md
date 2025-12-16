# NexusLEO Doctrine → Code Mapping (v0.2)

**Document Type:** Doctrine-to-Implementation Mapping  
**System:** NexusLEO  
**Version:** v0.2  
**Status:** Draft (Implementation-bound)  
**Last Updated:** 2025-12-16  

> This document binds **Platform Doctrine v0.2** to concrete backend responsibilities.
> Any behavior not explicitly mapped **does not exist** in NexusLEO.

---

## 1. Officer-first capture (Phase 1)

### Doctrine requirements
- Operators log activity quickly during a shift
- Entries are timestamped and optionally linked to cases
- No decisioning, ranking, or enforcement recommendations

### Code alignment

**Models**
- `backend/app/models/user.py` → `User`
- `backend/app/models/shift_session.py` → `ShiftSession`
- `backend/app/models/activity_log_entry.py` → `ActivityLogEntry`

**Endpoints**
- `POST /users`
  - `backend/app/api/routes/users.py#create_user`
- `POST /shifts/start`
  - `backend/app/api/routes/shifts.py#start_shift`
- `POST /shifts/{shift_id}/end`
  - `backend/app/api/routes/shifts.py#end_shift`
- `POST /shifts/{shift_id}/log`
  - `backend/app/api/routes/shifts.py#log_activity`
- `GET /shifts/{shift_id}/timeline`
  - `backend/app/api/routes/shifts.py#timeline`

**Schemas**
- `backend/app/schemas/user.py` → `UserCreate`, `UserOut`
- `backend/app/schemas/shift.py` → `ShiftStartRequest`, `ShiftStartResponse`, `ShiftEndResponse`
- `backend/app/schemas/activity.py` → `ActivityLogCreate`, `ActivityLogOut`

---

## 2. Auditability (Phase 1)

### Doctrine requirements
Shift operations and activity logging are auditable and immutable.

### Code alignment
- `backend/app/models/audit_event.py` → `AuditEvent`
- Shift audit actions are written in:
  - `backend/app/api/routes/shifts.py` via tool id `nexusleo.shift` and version `0.1.0`

Required actions:
- `shift_started`
- `shift_ended`
- `activity_logged`

---

## 3. Determinism

### Doctrine requirements
Timeline ordering is deterministic.

### Code alignment
- `GET /shifts/{shift_id}/timeline` orders by:
  - `occurred_at ASC`
  - `created_at ASC`
  - `id ASC`

---

**End of NexusLEO Doctrine → Code Mapping v0.2**
