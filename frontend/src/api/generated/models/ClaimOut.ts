/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConfidenceOut } from './ConfidenceOut';
import type { EvidenceOut } from './EvidenceOut';
export type ClaimOut = {
    audit_event_ids: Array<string>;
    case_id: string;
    claim_type: string;
    confidence?: (ConfidenceOut | null);
    created_at: string;
    evidence: Array<EvidenceOut>;
    id: string;
    object_entity_id?: (string | null);
    predicate: string;
    subject_entity_id?: (string | null);
    text: string;
};

