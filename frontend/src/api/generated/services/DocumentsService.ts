/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocumentCreate } from '../models/DocumentCreate';
import type { DocumentOut } from '../models/DocumentOut';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DocumentsService {
    /**
     * Create Document
     * @param caseId
     * @param requestBody
     * @returns DocumentOut Successful Response
     * @throws ApiError
     */
    public static createDocumentCasesCaseIdDocumentsPost(
        caseId: string,
        requestBody: DocumentCreate,
    ): CancelablePromise<DocumentOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/cases/{case_id}/documents',
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
