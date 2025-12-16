/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CaseCreate } from '../models/CaseCreate';
import type { CaseExportBundle } from '../models/CaseExportBundle';
import type { CaseOut } from '../models/CaseOut';
import type { RunCaseRequest } from '../models/RunCaseRequest';
import type { RunCaseResponse } from '../models/RunCaseResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CasesService {
    /**
     * Create Case
     * @param requestBody
     * @returns CaseOut Successful Response
     * @throws ApiError
     */
    public static createCaseCasesPost(
        requestBody: CaseCreate,
    ): CancelablePromise<CaseOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/cases',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Case
     * @param caseId
     * @param limit
     * @param offset
     * @returns CaseExportBundle Successful Response
     * @throws ApiError
     */
    public static exportCaseCasesCaseIdExportGet(
        caseId: string,
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<CaseExportBundle> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/cases/{case_id}/export',
            path: {
                'case_id': caseId,
            },
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Run Case
     * @param caseId
     * @param requestBody
     * @returns RunCaseResponse Successful Response
     * @throws ApiError
     */
    public static runCaseCasesCaseIdRunPost(
        caseId: string,
        requestBody: RunCaseRequest,
    ): CancelablePromise<RunCaseResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/cases/{case_id}/run',
            path: {
                'case_id': caseId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
