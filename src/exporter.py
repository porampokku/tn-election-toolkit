from pathlib import Path


def export_dataframe(df, output_path):
    """
    Export one parsed constituency to CSV and Excel.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_path.with_suffix(".csv"),
        index=False,
        encoding="utf-8-sig",
    )

    df.to_excel(
        output_path.with_suffix(".xlsx"),
        index=False,
    )
