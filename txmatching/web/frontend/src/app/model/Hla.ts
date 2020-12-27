export interface Hla {
  code: string;
  raw_code: string;
}

export interface Antigen extends Hla {
}

export interface Antibody extends Hla {
  mfi: number;
  cutoff: number;
}

export interface DetailedCompatibilityIndex {
  hla_group: string;
  donor_matches: HlaMatch[];
  recipient_matches: HlaMatch[];
  group_compatibility_index: number;
}

export interface HlaMatch {
  hla_code: string;
  match_type: HlaMatchType;
}

export interface HlaGroupCodes {
  hla_group: string;
  hla_codes: string[];
}

export enum HlaMatchType {
  SPLIT = 'SPLIT',
  BROAD = 'BROAD',
  HIGH_RES = 'HIGH_RES',
  NONE = 'NONE',
  ANTIBODY = 'ANTIBODY'
}

// todo: delete?
// export interface HlaCodesSorted {
//   A: string[];
//   B: string[];
//   DR: string[];
//   OTHER: string[];
//
//   [key: string]: string[];
// }
//
// export interface HlaCodesScore {
//   A: number;
//   B: number;
//   DR: number;
//
//   [key: string]: number;
// }
