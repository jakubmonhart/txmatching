/**
 * API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { MatchingGenerated } from './matchingGenerated';


export interface CalculatedMatchingsGenerated { 
    calculated_matchings: Array<MatchingGenerated>;
    config_id: number;
    found_matchings_count?: number;
    show_not_all_matchings_found: boolean;
}

