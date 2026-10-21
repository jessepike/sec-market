"""Durable model work for native Codex Cloud tasks, without nested CLI credentials.

The scheduled agent reads a request and submits a schema-checked response. A
separate governance context answers reviews. Queue identity binds the exact
prompt/schema/policy; deterministic validation remains the publication authority.
"""
import json

from agents import SubscriptionAgent
from contracts import digest, instant, require, utcnow, valid_hash


class WorkPending(ValueError):
    """Expected suspension, not a broken subscription or a completed check."""


def check_schema(value, schema):
    """Validate the small strict JSON-schema vocabulary used by the model adapters."""
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    actual = "null" if value is None else "boolean" if type(value) is bool else "string" if isinstance(value, str) else "object" if isinstance(value, dict) else "array" if isinstance(value, list) else "unsupported"
    require(actual in types, "NATIVE_RESPONSE_TYPE_MISMATCH")
    if "enum" in schema:
        require(value in schema["enum"], "NATIVE_RESPONSE_ENUM_MISMATCH")
    if actual == "object":
        require(set(schema.get("required", [])).issubset(value), "NATIVE_RESPONSE_REQUIRED_FIELD_MISSING")
        properties = schema.get("properties", {})
        require(schema.get("additionalProperties", True) or set(value).issubset(properties), "NATIVE_RESPONSE_EXTRA_FIELD")
        for key, item in value.items():
            require(key in properties, "NATIVE_RESPONSE_UNKNOWN_FIELD")
            check_schema(item, properties[key])
    if actual == "array":
        require(len(value) <= schema.get("maxItems", 1000), "NATIVE_RESPONSE_ARRAY_TOO_LARGE")
        for item in value:
            check_schema(item, schema["items"])


class NativeAgent(SubscriptionAgent):
    queued_work = True
    def __init__(self, config, store, policy_hash, session_id, clock=utcnow):
        super().__init__(config)
        require(bool(session_id) and len(session_id) <= 160, "NATIVE_SESSION_ID_REQUIRED")
        self.store, self.policy_hash, self.session_id, self.clock = store, policy_hash, session_id, clock
        self.stage = None
        self.extraction_session = None

    def extract(self, text, supplier):
        self.stage = "extract"
        return super().extract(text, supplier)

    def review(self, text, candidate, observation, policy_hash):
        self.stage = "review"
        return super().review(text, candidate, observation, policy_hash)

    def review_empty(self, text, supplier, observation, policy_hash):
        self.stage = "review_empty"
        return super().review_empty(text, supplier, observation, policy_hash)

    def call(self, prompt, schema):
        require(self.stage in ("extract", "review", "review_empty"), "NATIVE_WORK_STAGE_REQUIRED")
        request = {"schemaVersion": 1, "stage": self.stage, "policySha256": self.policy_hash,
                   "issuedDay": self.clock()[:10], "prompt": prompt, "responseSchema": schema}
        task_id = digest(request)
        request_key = f"native/requests/{task_id}.json"
        with self.store.lock("native-work-" + task_id, blocking=True):
            task = self.store.read(request_key)
            if task is None:
                require(self.reserve is not None, "NATIVE_BUDGET_RESERVATION_REQUIRED")
                # Reserve once before issuing work; resumes cannot renew this allowance.
                self.reserve("calls", self.config["maxCallsPerRun"])
                if self.stage != "extract":
                    require(bool(self.extraction_session), "NATIVE_REVIEW_EXTRACTION_CONTEXT_REQUIRED")
                task = {"taskId": task_id, "request": request, "createdAt": self.clock(),
                        "createdBySession": self.session_id if self.stage == "extract" else self.extraction_session,
                        "role": "collector" if self.stage == "extract" else "governance"}
                self.store.write_once(request_key, task)
            require(task["request"] == request, "NATIVE_REQUEST_INTEGRITY_MISMATCH")
            answer = self.store.read(f"native/responses/{task_id}.json")
            if answer is None:
                raise WorkPending("NATIVE_WORK_PENDING")
            require(answer["taskId"] == task_id and answer["policySha256"] == self.policy_hash, "NATIVE_RESPONSE_PROVENANCE_MISMATCH")
            check_schema(answer["response"], schema)
            if self.stage == "extract":
                self.extraction_session = answer["submittedBySession"]
            return answer["response"]


def pending_work(store, policy_hash, role, now=None):
    require(role in ("collector", "governance"), "NATIVE_ROLE_REQUIRED")
    now = now or utcnow()
    tasks = []
    for path in sorted((store.root / "native/requests").glob("*.json")):
        task = store.read(str(path.relative_to(store.root)))
        require(task["taskId"] == digest(task["request"]), "NATIVE_REQUEST_INTEGRITY_MISMATCH")
        if task["role"] != role or task["request"]["policySha256"] != policy_hash:
            continue
        if store.read(f"native/responses/{task['taskId']}.json") is not None:
            continue
        # Never answer a stale prompt as today's work. Old requests remain evidence.
        age = (instant(now) - instant(task["createdAt"])).total_seconds()
        if -300 <= age <= 30 * 3600:
            tasks.append(task)
    return tasks


def submit_work(store, task_id, response, role, session_id, policy_hash, now=None):
    require(valid_hash(task_id), "NATIVE_TASK_ID_INVALID")
    require(bool(session_id) and len(session_id) <= 160, "NATIVE_SESSION_ID_REQUIRED")
    task = store.read(f"native/requests/{task_id}.json")
    require(task is not None and digest(task["request"]) == task_id, "NATIVE_REQUEST_MISSING_OR_CORRUPTED")
    require(task["request"]["policySha256"] == policy_hash, "NATIVE_POLICY_MISMATCH")
    require(task["role"] == role, "NATIVE_ROLE_MISMATCH")
    require(role != "governance" or session_id != task["createdBySession"], "NATIVE_REVIEW_REQUIRES_SEPARATE_CONTEXT")
    now = now or utcnow()
    age = (instant(now) - instant(task["createdAt"])).total_seconds()
    require(-300 <= age <= 30 * 3600, "NATIVE_REQUEST_STALE_OR_FUTURE")
    check_schema(response, task["request"]["responseSchema"])
    # An exact retry is allowed. A contradictory second answer cannot replace evidence.
    with store.lock("native-work-" + task_id, blocking=True):
        key = f"native/responses/{task_id}.json"
        existing = store.read(key)
        if existing:
            require(existing["response"] == response and existing["submittedBySession"] == session_id, "NATIVE_RESPONSE_ALREADY_SEALED")
            return existing
        answer = {"taskId": task_id, "policySha256": policy_hash, "role": role,
                  "submittedBySession": session_id, "submittedAt": now, "response": response}
        store.write_once(key, answer)
        return answer
