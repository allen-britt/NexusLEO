/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CaseExportAuditEvent } from './CaseExportAuditEvent';
import type { CaseExportCase } from './CaseExportCase';
import type { CaseExportDocument } from './CaseExportDocument';
import type { ClaimOut } from './ClaimOut';
export type CaseExportBundle = {
    audit_events: Array<CaseExportAuditEvent>;
    case: CaseExportCase;
    claims: Array<ClaimOut>;
    documents: Array<CaseExportDocument>;
};

