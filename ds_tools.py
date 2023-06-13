import pandas as pd
import numpy as np

def basic_checks(df):
    """
    Carries out a basic analysis of the input DataFrame, including its shape, null values, duplicate rows, 
    and the data types of its columns, and prints a summary of the findings. This function helps in getting 
    a quick overview of the DataFrame structure and any potential issues with the data.

    The function separately analyzes numerical and categorical columns, providing a clearer understanding 
    of the DataFrame structure.

    Args:
        df (pd.DataFrame): The input DataFrame to be analysed.

    Returns:
        None. The function prints a summary of the basic analysis.

    Example:
        >>> data = {'A': [1, 2, 3, 4, 5], 'B': [5, 6, 7, 8, 9]}
        >>> df = pd.DataFrame(data)
        >>> basic_checks(df)

    Notes:
        - The function assumes that the input DataFrame has already been cleaned and properly formatted.
        - This function is intended for an initial analysis and does not cover all possible DataFrame issues.
        - Further data exploration and cleaning might be required based on the output of this function.
    """

    rows = df.shape[0]
    cols = df.shape[1]
    dups = df.duplicated().sum()
    nulls = df.isna().sum().sum()
    null_rows = df.isna().any(axis=1).sum()
    null_rows_pct = round(100 * null_rows / rows, 2)
    dups_pct = round(100 * dups / rows, 2)
    nulls_pct = round(100 * nulls / (rows * cols), 2)
    nulls_by_col_pct = df.isna().sum() / rows * 100
    nulls_by_col_pct = nulls_by_col_pct[nulls_by_col_pct > 0]  # Filter to exclude 0% null columns

    # Split the data types
    numerical = df.select_dtypes(exclude=['object', 'bool'])
    categorical = df.select_dtypes(include=['object', 'bool'])

    print(
        f"==================== SHAPE ====================\n"\
        f"Rows: {rows}\n"\
        f"Columns: {cols}\n"\
        f"\n==================== NULLS ====================\n"\
        f"Nulls: {nulls} null values\n"\
        f"Rows with nulls: {null_rows}, {null_rows_pct}% of the DataFrame\n"
    )
    if len(nulls_by_col_pct) > 0:
        print(f"Nulls percentage (by column):\n{nulls_by_col_pct.to_string(float_format='{:,.3f}%'.format)}")
    print(
        f"Total nulls percentage: {nulls_pct}%\n"\
        f"\n================== DUPLICATES =================\n"\
        f"Duplicates: {dups} rows, {dups_pct}% of the DataFrame\n"
    )
    
    if len(numerical.columns) > 0:
        print(
            f"\n============= NUMERICAL DATA TYPES ============\n"\
            f"{numerical.dtypes}"
        )
    
    if len(categorical.columns) > 0:
        print(
            f"\n=========== CATEGORICAL DATA TYPES ============\n"\
            f"{categorical.dtypes}"
        )
