/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentOut = {
    properties: {
        case_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        created_at: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        metadata_json: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
            isRequired: true,
        },
        sha256: {
            type: 'string',
            isRequired: true,
        },
        type: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
