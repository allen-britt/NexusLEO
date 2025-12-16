/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { IngestRequest } from '../models/IngestRequest';
import type { IngestResult } from '../models/IngestResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class IngestService {
    /**
     * Ingest
     * @param caseId
     * @param requestBody
     * @returns IngestResult Successful Response
     * @throws ApiError
     */
    public static ingestCasesCaseIdIngestPost(
        caseId: string,
        requestBody: IngestRequest,
    ): CancelablePromise<IngestResult> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/cases/{case_id}/ingest',
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
