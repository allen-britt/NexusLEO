/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $RunCaseResponse = {
    properties: {
        claims: {
            type: 'array',
            contains: {
                type: 'ClaimOut',
            },
            isRequired: true,
        },
        ingest_result: {
            type: 'IngestResult',
            isRequired: true,
        },
    },
} as const;
