from txmatching.patients.patient_parameters import HLATyping
from txmatching.utils.hla_system.get_genotype import get_antigen_genotype
from txmatching.utils.hla_system.hla_table import CompatibilityGeneCode

# Traditionally one can calculate index of incompatibility (IK) - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the incompatibility index table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles. Where depending
# on the alleles for each matching allel a certain bonus is added to compatibility index.

COMPABITILITY_INDEX_BONUS_PER_GENE_CODE = {
    CompatibilityGeneCode.A: 1,
    CompatibilityGeneCode.B: 3,
    CompatibilityGeneCode.DR: 9
}


def compatibility_index(donor_hla_typing: HLATyping,
                        recipient_hla_typing: HLATyping) -> float:
    """
    The "compatibility index" is terminus technicus defined by immunologist:
    we calculate number of matches per Compatibility HLA indices and add bonus according
     to number of matches and the hla code.
    This function thus should not be modified unless after consulting with immunologists.
    """
    hla_compatibility_index = 0.0
    for gene_code, ci_bonus in COMPABITILITY_INDEX_BONUS_PER_GENE_CODE.items():
        donor_genotype = get_antigen_genotype(donor_hla_typing.hla_typing_broad_resolution, gene_code)
        recipient_genotype = get_antigen_genotype(recipient_hla_typing.hla_typing_broad_resolution, gene_code)
        common_allele_codes = set(donor_genotype.keys()).intersection(set(recipient_genotype.keys()))

        match_count = 0
        for allele_code in common_allele_codes:
            match_count += min(donor_genotype[allele_code], recipient_genotype[allele_code])

        hla_compatibility_index += match_count * ci_bonus

    return hla_compatibility_index
