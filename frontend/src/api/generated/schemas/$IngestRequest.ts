/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $IngestRequest = {
    properties: {
        actor: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        document_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
    },
} as const;
