/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DemoSeedOut } from '../models/DemoSeedOut';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DemoService {
    /**
     * Demo Seed
     * @returns DemoSeedOut Successful Response
     * @throws ApiError
     */
    public static demoSeedDemoSeedPost(): CancelablePromise<DemoSeedOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/_demo/seed',
        });
    }
}
