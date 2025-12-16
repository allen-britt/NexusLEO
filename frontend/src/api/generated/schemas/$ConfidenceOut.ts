/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ConfidenceOut = {
    properties: {
        factors_json: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
            isRequired: true,
        },
        level: {
            type: 'string',
            isRequired: true,
        },
        rationale_text: {
            type: 'string',
            isRequired: true,
        },
        rubric_version: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
