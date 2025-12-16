/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $CaseExportCase = {
    properties: {
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
        name: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
