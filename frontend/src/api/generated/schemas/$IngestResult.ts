/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $IngestResult = {
    properties: {
        audit_events_created: {
            type: 'number',
            isRequired: true,
        },
        claim_ids: {
            type: 'array',
            contains: {
                type: 'string',
                format: 'uuid',
            },
            isRequired: true,
        },
        claims_created: {
            type: 'number',
            isRequired: true,
        },
        confidence_created: {
            type: 'number',
            isRequired: true,
        },
        document_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        entities_created: {
            type: 'number',
            isRequired: true,
        },
        evidence_links_created: {
            type: 'number',
            isRequired: true,
        },
        mentions_created: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
