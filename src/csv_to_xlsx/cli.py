import click
import polars as pl


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path(exists=False))
def csv_to_xlsx(input_file: str, output_file: str) -> None:
    df = pl.read_csv(input_file, infer_schema_length=None)
    df.write_excel(output_file)


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path(exists=False))
def xlsx_to_csv(input_file: str, output_file: str) -> None:
    df = pl.read_excel(input_file)
    df.write_csv(output_file)
