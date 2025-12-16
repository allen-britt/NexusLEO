/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ClaimOut } from '../models/ClaimOut';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ClaimsService {
    /**
     * List Claims
     * @param caseId
     * @param limit
     * @param offset
     * @returns ClaimOut Successful Response
     * @throws ApiError
     */
    public static listClaimsCasesCaseIdClaimsGet(
        caseId: string,
        limit: number = 100,
        offset?: number,
    ): CancelablePromise<Array<ClaimOut>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/cases/{case_id}/claims',
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
}
