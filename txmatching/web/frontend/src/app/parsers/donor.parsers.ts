import { DonorGenerated, DonorTypeGenerated } from '../generated';
import { Donor, DonorType } from '../model';
import { parsePatient } from './patient.parsers';
import { parseDetailedScorePerGroup } from './hla.parsers';

export const parseDonor = (data: DonorGenerated): Donor => {
  return {
    ...parsePatient(data),
    active: data.active,
    donor_type: parseDonorType(data.donor_type),
    compatible_blood_with_related_recipient: data.compatible_blood_with_related_recipient,
    related_recipient_db_id: data.related_recipient_db_id,
    score_with_related_recipient: data.score_with_related_recipient,
    detailed_score_with_related_recipient: data.detailed_score_with_related_recipient?.map(parseDetailedScorePerGroup) ?? []
  };
};

export const parseDonorType = ( data: DonorTypeGenerated ): DonorType => {
  return DonorType[data];
};
