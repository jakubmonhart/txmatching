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
import { ForbiddenCountryCombinationGenerated } from './forbiddenCountryCombinationGenerated';
import { ManualRecipientDonorScoreGenerated } from './manualRecipientDonorScoreGenerated';


export interface ConfigurationGenerated { 
    blood_group_compatibility_bonus?: number;
    forbidden_country_combinations?: Array<ForbiddenCountryCombinationGenerated>;
    manual_donor_recipient_scores?: Array<ManualRecipientDonorScoreGenerated>;
    max_allowed_number_of_cycles_to_be_searched?: number;
    max_allowed_number_of_matchings?: number;
    max_cycle_length?: number;
    max_matchings_to_show_to_viewer?: number;
    max_matchings_to_store_in_db?: number;
    max_number_of_distinct_countries_in_round?: number;
    max_number_of_solutions_for_ilp?: number;
    max_sequence_length?: number;
    maximum_total_score?: number;
    minimum_total_score?: number;
    require_better_match_in_compatibility_index?: boolean;
    require_better_match_in_compatibility_index_or_blood_group?: boolean;
    require_compatible_blood_group?: boolean;
    required_patient_db_ids?: Array<number>;
    scorer_constructor_name?: string;
    solver_constructor_name?: ConfigurationGeneratedSolverConstructorNameEnum;
    use_binary_scoring?: boolean;
    use_split_resolution?: boolean;
}
export enum ConfigurationGeneratedSolverConstructorNameEnum {
    AllSolutionsSolver = 'AllSolutionsSolver',
    IlpSolver = 'ILPSolver'
};



