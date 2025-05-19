"""
CCAoA wrapper for the most popular python data science package, Pandas.
Includes custom and shortcut functions for common pandas operations.
Many functions here were moved from the core module after v2.0 release.
"""

import os, re, string, numpy as np, pandas as pd, xlsxwriter, openpyxl, time, warnings

if __name__ == "__main__":
    from ccaoa import core
else:
    from . import core


def check_empty_dataframe(df2check: pd.DataFrame) -> bool:
    """See if a pandas dataframe is empty or not. Returns True/False"""
    # https://stackoverflow.com/questions/19828822/how-to-check-whether-a-pandas-dataframe-is-empty
    result = not (
        df2check is not None
        and isinstance(df2check, pd.DataFrame)
        and not df2check.empty
    )
    return result


def make_valid_colname(col_name: str) -> str:
    """Transform col_name into a valid pandas column name"""
    if col_name is None:
        col_name = "None"
    elif type(col_name) == bool or type(col_name) in (int, float):
        col_name = str(col_name)
    col_name = col_name.replace(" ", "_")
    col_name = re.sub(r"\W+", "", col_name)
    # Check if col_name is hashable and convertable to an instance of type `str`
    if not (
        isinstance(col_name, str)
        or (hasattr(col_name, "__hash__") and callable(col_name.__hash__))
    ):
        col_name = str(col_name)

    # Check if col_name is a reserved word
    if col_name in dir(__builtins__):
        col_name = "col_" + col_name

    # Replace invalid characters with "_"
    col_name = "".join(
        c if c in (string.ascii_letters + string.digits + "_") else "_"
        for c in col_name
    )

    return col_name


def move_column_to_beginning(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """Move a specified column to the beginning (left-hand side) of the dataframe."""
    columns = df.columns.to_list()
    # Check to make sure the column is actually in the dataframe.
    if target_col not in columns:
        # See if there's a different case under which the column is included.
        case_target_col = core.find_value_in_list(
            target_col, columns, return_input=False, case_or_type_sensitive=False
        )
        if case_target_col is False:
            # There's no version of the input in the columns of the DF
            print(
                target_col,
                "is not in the dataframe you passed and will not be moved to the front of it. "
                "Try passing these arguments again.",
            )
            return None
        else:
            # The target column was in there with a different case. Use the DF's version
            target_col = case_target_col
            del case_target_col

    # Move the ID-d column to the front of the dataframe
    columns.remove(target_col)
    cols = [target_col] + columns
    df = df[cols]
    return df


# This is from Google Trends. Need to generalize this function before deploying it!!!
def transpose_df(
    df: pd.DataFrame,
    first_col_as_new_col_names: bool = True,
    old_cols_as_index: bool = True,
    col_of_oldcolumns_name: str = "old_cols",
) -> pd.DataFrame:
    """Transpose a dataframe with specific index manipulation to fit this Google Trends project."""
    # NOTE: Migrate this function to a more generalizable format in ccaoa.core.raccoon module. Then call it here.
    # If the user wanted the first column of the PD DF to function as the column names
    if core.string_to_bool(first_col_as_new_col_names) is True:
        # The first column of the raw dataset containing UOA identifiers will be set as the column names of the new DF.
        first_col = df.columns[0]
        work_df = df.set_index(first_col).transpose()
    else:
        # The first column of the raw dataset containing UOA identifiers will be set as the first row.
        work_df = df.transpose()
    # At this point, the old column headers are the new index column, with the old first column as the first record.
    # # https://stackoverflow.com/a/36013757/15517267
    if core.string_to_bool(old_cols_as_index) is False:
        # If the user wants the old columns bounced out into the first row:
        old_first_column = work_df.columns.name
        if isinstance(col_of_oldcolumns_name, str) is not True:
            try:
                col_of_oldcolumns_name = str(col_of_oldcolumns_name)
            except:
                col_of_oldcolumns_name = "old_cols"
        work_df = index_to_first_column(
            work_df, col_of_oldcolumns_name
        )  # old_first_column)
    # Otherwise, the old column names will still be the index of the output DF.
    return work_df


def index_to_first_column(df: pd.DataFrame, new_index_name="index") -> pd.DataFrame:
    """Add the index of a dataframe as the first column of that dataframe."""
    # Get the name of the old index.
    name_of_existing_idx = df.index.name
    if name_of_existing_idx is None:
        # How it'll be used downstream if there's no name to the IDX.
        name_of_existing_idx = "index"
    # Make sure the new index name is valid.
    new_index_name = make_valid_colname(new_index_name)

    # Extract the index of the dataframe as a column
    df.reset_index(inplace=True)

    # Rename the index column to 'index_col'
    df.rename(columns={name_of_existing_idx: new_index_name}, inplace=True)

    # Move the 'index_col' column to the front of the dataframe
    df = move_column_to_beginning(df, new_index_name)
    return df


def file_to_df(
    inputfil: str,
    xlsxsheet=0,
    indexcolumn=None,
    engine: str = None,
    skip_rows: int = None,
    nrows: int = None,
    keep_default_na: bool = True,
    converters_dict: dict = None,
):
    """Takes an input xlsx or csv file and converts it to a pandas dataframe for downstream usage."""
    if inputfil.endswith(r".xlsx") or inputfil.endswith(r".xls"):
        # https://stackoverflow.com/questions/65254535/xlrd-biffh-xlrderror-excel-xlsx-file-not-supported
        if (
            (inputfil.endswith(r".xls"))
            and (engine == "openpyxl")
            and (engine is not None)
        ):
            # If a .xls file is passed using openpyxl engine, remove that engine designation b/c it won't work.
            engine = None  # "xlrd" is pandas' 1.1.5 default and what we want .
            # See https://pandas.pydata.org/pandas-docs/stable/whatsnew/v1.2.0.html
        if (inputfil.endswith(r".xlsx")) and (engine is None or engine == "xlrd"):
            # If an .xlsx file is passed without using an engine or with xlrd,
            # use the openpyxl engine b/c of recent py3.6 xlrd --upgrade
            engine = "openpyxl"
        if xlsxsheet is None:
            # If None is passed to denote the default value, set the correct default value.
            # # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            xlsxsheet = 0
        fildataframe = pd.read_excel(
            inputfil,
            sheet_name=xlsxsheet,
            index_col=indexcolumn,
            engine=engine,
            skiprows=skip_rows,
            nrows=nrows,
            keep_default_na=keep_default_na,
            converters=converters_dict,
        )
    elif inputfil.endswith(".csv"):
        fildataframe = pd.read_csv(
            inputfil,
            index_col=indexcolumn,
            skiprows=skip_rows,
            nrows=nrows,
            keep_default_na=keep_default_na,
        )
    elif inputfil.endswith(".json"):
        fildataframe = pd.read_json(inputfil)
    else:
        fildataframe = pd.DataFrame

    return fildataframe


def df_to_file(
    in_df: pd.DataFrame,
    outlocat: str,
    index: bool = False,
    mkdir: bool = False,
    sheet_xlsx=None,
    add_to_existing_xlsx: bool = False,
    overwrite_old_sheet: bool = False,
    sheet_is_first_tab: bool = False,
):
    """Function inherited from the geocoding workflow that dictates the output preferences for the pandas dataframes.
    Only XLSX and CSV outputs possible. No XLS functionality. Potential for SQL or Dump files in future.
    A copy now lives in raccoon module. Remove the function here at the next major version release.
    """

    # Maybe in the future you output to different sheet in same input xlsx? idk. make a togglable action.
    # # Hard code for now :(
    # # May have to import openpyxl as engine if this is constructed.
    # Get the dirname for use if mkdir is True
    dirname = os.path.dirname(outlocat)
    # Spit the df out into a file.
    if outlocat.endswith(".xlsx") and (os.path.exists(dirname) or mkdir is True):
        theoutxlsx = outlocat
        # Output the XLSX
        if core.string_to_bool(add_to_existing_xlsx) is True and os.path.exists(
            theoutxlsx
        ):
            # The user has opted to add the data frame to the output XLSX instead of
            # # Get the existing sheets now and store for later
            existing_sheets = pd.ExcelFile(theoutxlsx).sheet_names
            # Use openpyxl to add to your existing sheet.
            # https://stackoverflow.com/a/50020967/15517267
            book = openpyxl.load_workbook(theoutxlsx)
            # if core.string_to_bool(overwrite_old_sheet) is True:
            #     # This means that the user understands that the output sheet will overwrite the old sheet if it exsits.
            #     # This is not pandas' default functionality; it will just add the next numeral to your sheet in write mode.
            #     # So force the overwrite by using Append mode and 'replace' argument.
            #     # NOTE: This is pd v>=1.3 function.
            #     # https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html
            #     pd_xlsx_mode = 'a'
            #     pd_xlsx_existing_sheet_rule = 'replace'
            #     # This should have worked! but it isn't. Only mention of this issue I can see is
            #     # # https://stackoverflow.com/questions/74311731/to-excel-error-valueerror-worksheet-is-not-in-list
            #     # And some issues that aren't very helpful. Don't know if v1.4.x is needed for this..
            #     # # https://github.com/pandas-dev/pandas/issues?q=is%3Aissue+if_sheet_exists%3D+replace+is%3Aclosed
            # else:
            #     # Default to caution and don't auto override and replace/refresh the xlsx sheet. Make a copy instead.
            #     pd_xlsx_mode = 'w'  # (This is PD's default)
            #     pd_xlsx_existing_sheet_rule = 'new'
            # print(pd_xlsx_mode, pd_xlsx_existing_sheet_rule)
            writer = pd.ExcelWriter(theoutxlsx, engine="openpyxl")
            # , mode=pd_xlsx_mode, if_sheet_exists=pd_xlsx_existing_sheet_rule)
            writer.book = book
        else:
            if (
                core.string_to_bool(add_to_existing_xlsx) is True
                and os.path.exists(theoutxlsx) is False
            ):
                # This means that the user was trying to add the input DF to an existing sheet that doesn't exist.
                # Warn them of this.
                print(
                    "The file",
                    os.path.basename(theoutxlsx),
                    "does not exist in the",
                    str(dirname),
                    "directory.\n  The dataframe will be output to a new XLSX file by that name instead.",
                )
            # Continue with v1 output methodology.
            if mkdir is True and os.path.exists(dirname) is False:
                try:
                    os.mkdir(dirname)
                except:
                    raise FileNotFoundError(
                        "There was an error in creating the directory for the file you specified. "
                        "Please check the file name below and try again.\n ",
                        dirname,
                    )
            writer = pd.ExcelWriter(theoutxlsx, engine="xlsxwriter")
            existing_sheets = []
            # pandas will refresh file itself if it already exists in this version.
        # Name the output sheet.
        if sheet_xlsx is None:
            # Use the default sheet name and just use the first 31 characters of the file name.
            # # https://stackoverflow.com/a/3681908/15517267
            formattedsheetname = (os.path.splitext(os.path.basename(theoutxlsx))[0])[
                :31
            ]
        else:
            # The user has defined their own sheet name.
            try:
                # Try using the user-defined sheet name.
                formattedsheetname = str(sheet_xlsx)[:31]
            except:
                # but if there are errors, default to the default.
                formattedsheetname = (
                    os.path.splitext(os.path.basename(theoutxlsx))[0]
                )[:31]
        if (
            core.string_to_bool(add_to_existing_xlsx) is True
            and os.path.exists(theoutxlsx) is True
            and core.string_to_bool(overwrite_old_sheet) is True
            and formattedsheetname in existing_sheets
        ):
            # This means that the user understands that the output sheet will overwrite the old sheet if it exists.
            # This is not pandas' default functionality; it will just add the next numeral to your sheet in write mode.
            # So force the overwrite by removing the current sheet before writing it again.
            # PS. `book` will be a recognized variable here b/c it shares the conditionals of this statement.
            # # If it was defined there, it'll be recognized here.
            book.remove(book[formattedsheetname])
            existing_sheets = book.sheetnames
        copy_num = 0
        while formattedsheetname.lower() in [s.lower() for s in existing_sheets]:
            # The new sheet name is already taken in the output xlsx. Need to change it before it can be saved.
            copyflag = "_copy" + str(copy_num)
            formattedsheetname = formattedsheetname.replace(copyflag, "")
            copy_num += 1
            copyflag = "_copy" + str(copy_num)
            formattedsheetname = formattedsheetname[: 31 - len(copyflag)] + copyflag

        # Write the output xlsx!
        in_df.to_excel(writer, sheet_name=formattedsheetname, index=index)
        writer.save()
        # If the writer has not yet been closed, close it.
        # # Do so by suppressing warnings if the writer has already been closed. We don't need to know that.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            writer.close()

        # # If the user desires it, output the new sheet as the first tab in the Excel workbook.
        if (
            core.string_to_bool(sheet_is_first_tab) is True
            and os.path.exists(theoutxlsx)
            and core.string_to_bool(add_to_existing_xlsx) is True
        ):
            # Give it a moment
            time.sleep(0.75)
            # Re-load the workbook
            book = openpyxl.load_workbook(theoutxlsx)
            # Get the index of the current sheet
            current_index = book.sheetnames.index(formattedsheetname)
            # Move the sheet to the front
            book.move_sheet(formattedsheetname, offset=-current_index)
            # Save the workbook
            book.save(theoutxlsx)
            book.close()

    elif outlocat.endswith(".csv") and (os.path.exists(dirname) or mkdir is True):
        theoutcsv = outlocat
        # Output the CSV
        if mkdir is True and os.path.exists(dirname) is False:
            try:
                os.mkdir(dirname)
            except:
                raise FileNotFoundError(
                    "There was an error in creating the directory for the file you specified. "
                    "Please check the file name below and try again.\n ",
                    dirname,
                )
        # Pandas will refresh file itself if it already exists
        in_df.to_csv(theoutcsv, index=index)
    else:
        print(
            "The input file is not a valid .xlsx or .csv; thus, the dataframe cannot be written.\n"
            "Please check and try again:",
            outlocat,
        )

    return outlocat
