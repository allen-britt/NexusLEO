/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $CaseExportAuditEvent = {
    properties: {
        action: {
            type: 'string',
            isRequired: true,
        },
        actor: {
            type: 'string',
            isRequired: true,
        },
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
        input_refs_json: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
            isRequired: true,
        },
        output_refs_json: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
            isRequired: true,
        },
        tool: {
            type: 'string',
            isRequired: true,
        },
        tool_version: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
