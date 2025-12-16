/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $VersionOut = {
    properties: {
        git_sha: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        schema_revision: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        service: {
            type: 'string',
            isRequired: true,
        },
        version: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
