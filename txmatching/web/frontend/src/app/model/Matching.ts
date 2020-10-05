import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientPair } from '@app/model/Patient';

export interface Matching extends ListItem {
  db_id: number;
  score: number;
  rounds: Round[];
  countries: MatchingCountry[];
}

export interface Round {
  transplants: Transplant[];
}

export interface Transplant extends PatientPair {
  score?: number;
  compatible_blood?: boolean;
  donor?: string;
  recipient?: string;
}

export interface MatchingCountry {
  country_code: string;
  donor_count: number;
  recipient_count: number;
}

export const matchingBatchSize = 10;
