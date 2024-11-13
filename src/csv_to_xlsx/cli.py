import os
from typing import Iterable, Optional

import click
import joblib
import polars as pl
from fastexcel import read_excel
from pathlib import Path


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path(exists=False))
@click.option("--delimiter", type=str, default=None, help="Delimiter for the CSV file")
def csv_to_xlsx(input_file: str, output_file: str, delimiter: Optional[str]) -> None:
    df = pl.read_csv(input_file, infer_schema_length=None, separator=delimiter)
    df.write_excel(output_file)


def _xlsx_to_csv_impl(input_file: str, output_file: str, sheet_name: str | None = None) -> None:
    df = pl.read_excel(input_file, sheet_name=sheet_name, infer_schema_length=None)
    df.write_csv(output_file)


def _mk_safe_sheet_name(sheet_name: str) -> str:
    return "".join(c if c.isalnum() or c == "_" else "_" for c in sheet_name)


def _make_safe_sheet_names(sheet_names: list[str]) -> Iterable[str]:
    result_set = set()

    for sheet_name in sheet_names:
        safe_name = _mk_safe_sheet_name(sheet_name)
        safe_name_suffix = ""
        i = 0

        while safe_name + safe_name_suffix in result_set:
            i += 1
            safe_name_suffix = f"_{i}"

        safe_name = safe_name + safe_name_suffix
        result_set.add(safe_name)
        yield safe_name


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "-a",
    "--all-sheets",
    is_flag=True,
    default=False,
    help="Convert all excel sheets to CSVs. `output_file` is treated as a directory.",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=-1,
    help="Amount of parallel jobs in case '--all-sheets' is used",
)
def xlsx_to_csv(input_file: str, output_file: str, all_sheets: bool, jobs: int) -> None:
    if all_sheets:
        os.makedirs(output_file, exist_ok=True)
        sheet_names = read_excel(input_file).sheet_names

        _ = joblib.Parallel(n_jobs=jobs)(
            joblib.delayed(_xlsx_to_csv_impl)(
                input_file, Path(output_file) / f"{safe_sheet_name}.csv", sheet_name
            )
            for safe_sheet_name, sheet_name in zip(
                _make_safe_sheet_names(sheet_names), sheet_names
            )
        )
    else:
        _xlsx_to_csv_impl(input_file, output_file)

