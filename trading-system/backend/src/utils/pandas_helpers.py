import pandas as pd

def flatten_columns(df):
    # Handles MultiIndex, tuple columns, and also stringified-tuple columns
    def col_flat(c):
        # Actual tuple
        if isinstance(c, tuple):
            return "_".join([str(x) for x in c if x not in ("", None)])
        # String that looks like a tuple
        if isinstance(c, str) and c.startswith("(") and c.endswith(")"):
            try:
                pieces = eval(c)
                if isinstance(pieces, tuple):
                    return "_".join(str(x) for x in pieces if x not in ("", None))
            except Exception:
                pass
        return str(c)
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex) or any(isinstance(c, tuple) or (isinstance(c, str) and c.startswith("(") and c.endswith(")")) for c in df.columns):
        df.columns = [col_flat(c) for c in df.columns]
    return df
