from pydantic import BaseModel, ValidationError
from typing import Type
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def validate_records(
    records: list[dict],
    schema: Type[BaseModel],
    source_name: str
) -> tuple[list[BaseModel], list[dict]]:
    """
    Validates a list of raw dicts against a Pydantic schema.

    Rules:
    - Valid records   → returned as Pydantic model instances (type-safe)
    - Invalid records → quarantined with full error details (never silently dropped)

    Args:
        records     : raw list of dicts from an extractor
        schema      : the Pydantic model class to validate against
        source_name : label used in log messages e.g. "CSV", "API", "MongoDB"

    Returns:
        (valid_records, invalid_records)
        valid_records   — list of validated Pydantic model instances
        invalid_records — list of dicts: {"record": original_dict, "errors": [...]}
    """
    valid_records: list[BaseModel] = []
    invalid_records: list[dict] = []

    for i, record in enumerate(records):
        try:
            validated = schema.model_validate(record)
            valid_records.append(validated)

        except ValidationError as e:
            error_summary = e.errors(include_url=False)
            logger.warning(
                f"[{source_name}] Record #{i} INVALID — "
                f"{len(error_summary)} error(s): "
                + ", ".join(
                    f"{err['loc']} → {err['msg']}"
                    for err in error_summary
                )
            )
            invalid_records.append({
                "record": record,
                "errors": error_summary
            })

    # ── Summary log ───────────────────────────────────────────────────────────
    total = len(records)
    n_valid = len(valid_records)
    n_invalid = len(invalid_records)
    pct = round((n_valid / total) * 100, 1) if total > 0 else 0.0

    logger.info(
        f"[{source_name}] Validation complete — "
        f"{n_valid}/{total} valid ({pct}%), "
        f"{n_invalid} quarantined"
    )

    if n_invalid > 0:
        logger.warning(
            f"[{source_name}] {n_invalid} record(s) failed validation. "
            f"Check invalid_records for details before loading."
        )

    return valid_records, invalid_records


def print_invalid_report(invalid_records: list[dict], source_name: str) -> None:
    """
    Pretty-prints a human-readable report of all invalid records.
    Call this during manual testing / debugging.
    """
    if not invalid_records:
        print(f"\n✅  [{source_name}] No invalid records. All data passed validation.\n")
        return

    print(f"\n{'='*60}")
    print(f"  INVALID RECORDS REPORT — {source_name} ({len(invalid_records)} records)")
    print(f"{'='*60}")

    for i, item in enumerate(invalid_records, 1):
        print(f"\n  Record #{i}:")
        print(f"  Raw data : {item['record']}")
        print(f"  Errors   :")
        for err in item["errors"]:
            field = " → ".join(str(loc) for loc in err["loc"])
            print(f"    • [{field}] {err['msg']}")

    print(f"\n{'='*60}\n")