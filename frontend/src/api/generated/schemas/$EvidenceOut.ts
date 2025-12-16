/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $EvidenceOut = {
    properties: {
        document_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        evidence_link_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        mention: {
            type: 'MentionOut',
            isRequired: true,
        },
        notes: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        weight: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
