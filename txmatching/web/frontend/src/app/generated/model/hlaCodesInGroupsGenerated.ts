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
import { HlaTypeGenerated } from './hlaTypeGenerated';


export interface HlaCodesInGroupsGenerated { 
    hla_group: HlaCodesInGroupsGeneratedHlaGroupEnum;
    hla_types: Array<HlaTypeGenerated>;
}
export enum HlaCodesInGroupsGeneratedHlaGroupEnum {
    A = 'A',
    B = 'B',
    Drb1 = 'DRB1',
    Other = 'Other'
};


