from kidney_exchange.utils.hla_system.hla_table import split_to_broad, HLA_A, HLA_B, HLA_DR
import logging



# TODO combine with hla_table.py https://trello.com/c/sSRh7uRh/126-combine-hlatablepy-and-splittobroadresolutionpy
logger = logging.getLogger(__name__)


def hla_split_to_broad(split_code: str) -> str:
    return split_to_broad.get(split_code) or split_code


HLA_A_broad = list(map(hla_split_to_broad, HLA_A))
HLA_B_broad = list(map(hla_split_to_broad, HLA_B))
HLA_DR_broad = list(map(hla_split_to_broad, HLA_DR))


def is_valid_broad_code(code: str) -> bool:
    for code_list in [HLA_A_broad, HLA_B_broad, HLA_DR_broad]:
        if code in code_list:
            return True

    return False


if __name__ == "__main__":
    test_code = "B38"
    broad_res_code = hla_split_to_broad(test_code)
    logger.info(f"Broad res code: {broad_res_code} [is valid: {is_valid_broad_code(broad_res_code)}]")

    logger.info(HLA_A_broad)
    logger.info(HLA_B_broad)
    logger.info(HLA_DR_broad)