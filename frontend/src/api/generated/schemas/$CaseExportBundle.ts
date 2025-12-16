/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $CaseExportBundle = {
    properties: {
        audit_events: {
            type: 'array',
            contains: {
                type: 'CaseExportAuditEvent',
            },
            isRequired: true,
        },
        case: {
            type: 'CaseExportCase',
            isRequired: true,
        },
        claims: {
            type: 'array',
            contains: {
                type: 'ClaimOut',
            },
            isRequired: true,
        },
        documents: {
            type: 'array',
            contains: {
                type: 'CaseExportDocument',
            },
            isRequired: true,
        },
    },
} as const;
