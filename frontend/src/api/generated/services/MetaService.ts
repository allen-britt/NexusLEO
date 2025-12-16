/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { VersionOut } from '../models/VersionOut';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MetaService {
    /**
     * Version
     * @returns VersionOut Successful Response
     * @throws ApiError
     */
    public static versionVersionGet(): CancelablePromise<VersionOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/version',
        });
    }
}
