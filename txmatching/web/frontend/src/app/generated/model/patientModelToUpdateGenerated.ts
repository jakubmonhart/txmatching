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
import { SexEnumGenerated } from './sexEnumGenerated';
import { PatientModelToUpdateHlaTypingGenerated } from './patientModelToUpdateHlaTypingGenerated';
import { BloodGroupEnumGenerated } from './bloodGroupEnumGenerated';


export interface PatientModelToUpdateGenerated {
    blood_group: BloodGroupEnumGenerated;
    /**
     * Database id of the patient
     */
    db_id: number;
    /**
     * Number of updates of a patient
     */
    etag: number;
    /**
     * Height of the patient in centimeters.
     */
    height?: number;
    hla_typing?: PatientModelToUpdateHlaTypingGenerated;
    note?: string;
    sex?: SexEnumGenerated;
    /**
     * Weight of the patient in kilograms.
     */
    weight?: number;
    /**
     * Year of birth of the patient.
     */
    year_of_birth?: number;
}

