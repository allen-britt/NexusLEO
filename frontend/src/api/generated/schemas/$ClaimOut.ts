/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ClaimOut = {
    properties: {
        audit_event_ids: {
            type: 'array',
            contains: {
                type: 'string',
                format: 'uuid',
            },
            isRequired: true,
        },
        case_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        claim_type: {
            type: 'string',
            isRequired: true,
        },
        confidence: {
            type: 'any-of',
            contains: [{
                type: 'ConfidenceOut',
            }, {
                type: 'null',
            }],
        },
        created_at: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        evidence: {
            type: 'array',
            contains: {
                type: 'EvidenceOut',
            },
            isRequired: true,
        },
        id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        object_entity_id: {
            type: 'any-of',
            contains: [{
                type: 'string',
                format: 'uuid',
            }, {
                type: 'null',
            }],
        },
        predicate: {
            type: 'string',
            isRequired: true,
        },
        subject_entity_id: {
            type: 'any-of',
            contains: [{
                type: 'string',
                format: 'uuid',
            }, {
                type: 'null',
            }],
        },
        text: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
