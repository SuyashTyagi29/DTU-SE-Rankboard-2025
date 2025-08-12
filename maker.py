import pandas as pd

# ====== INPUT FILES ======
BRANCH_SWITCHERS_FILE = "branch_switchers_sem1_2_results.csv"
SEM1_2_FILE           = "SE_sem1_2_results_CG_filled_final.csv"
SEM3_6_FILE           = "SE_results.csv"
SEM7_8_FILE           = "SE_sem7_8_results_with_names.csv"
OUTPUT_FILE           = "final_results.csv"

# ====== HELPER ======
def standardize(df, roll_col='roll_no', name_col='name'):
    # Ensure consistent roll number format
    if roll_col in df.columns:
        df[roll_col] = df[roll_col].astype(str).str.upper().str.strip()

    # Standardize names (Title Case for output)
    if name_col in df.columns:
        df[name_col] = df[name_col].astype(str).str.title().str.strip()

    # Ensure semester exists and fill NaN with 0
    if 'semester' in df.columns:
        df['semester'] = pd.to_numeric(df['semester'], errors='coerce').fillna(0).astype(int)
    return df

# ====== LOAD DATA ======
branch_switchers = pd.read_csv(BRANCH_SWITCHERS_FILE)
sem1_2           = pd.read_csv(SEM1_2_FILE)
sem3_6           = pd.read_csv(SEM3_6_FILE)
sem7_8           = pd.read_csv(SEM7_8_FILE)

# ====== STANDARDIZE ======
branch_switchers = standardize(branch_switchers, roll_col='new_roll_no')
sem1_2           = standardize(sem1_2)
sem3_6           = standardize(sem3_6)
sem7_8           = standardize(sem7_8)

# ====== MERGE sem1-2 results ======
merged_sem1_2 = pd.concat([
    sem1_2.rename(columns={'roll_no': 'roll_no'}),
    branch_switchers.rename(columns={'new_roll_no': 'roll_no'})
], ignore_index=True)

# Keep only needed columns for sem1-2
merged_sem1_2 = merged_sem1_2[['roll_no', 'name', 'semester', 'sgpa', 'credits']]

# ====== Prepare sem3-6 ======
# Extract semester from filename column if missing
if 'semester' not in sem3_6.columns and 'pdf' in sem3_6.columns:
    sem3_6['semester'] = sem3_6['pdf'].str.extract(r'(\d+)').astype(int)
sem3_6 = sem3_6[['roll_no', 'name', 'semester', 'sgpa', 'credits']]

# ====== Prepare sem7-8 ======
sem7_8 = sem7_8[['roll_no', 'name', 'semester', 'sgpa', 'credits']]

# ====== Combine all ======
all_data = pd.concat([merged_sem1_2, sem3_6, sem7_8], ignore_index=True)

# ====== Pivot to wide format ======
all_data['roll_no'] = all_data['roll_no'].astype(str).str.upper().str.strip()

wide = all_data.pivot_table(
    index='roll_no',
    columns='semester',
    values=['sgpa', 'credits'],
    aggfunc='first'
)

# Flatten column names: (metric, semester) -> semX_metric
wide.columns = [f"sem{sem}_{metric}" for metric, sem in wide.columns]
wide = wide.reset_index()

# ====== Add Name Column ======
name_map = all_data.groupby('roll_no')['name'].first().reset_index()
wide = wide.merge(name_map, on='roll_no', how='left')

# ====== Ensure all semester columns exist ======
sem_list = list(range(1, 9))
for s in sem_list:
    for col in (f"sem{s}_sgpa", f"sem{s}_credits"):
        if col not in wide.columns:
            wide[col] = pd.NA

# ====== Calculate total_credits & cgpa ======
credit_cols = [f"sem{s}_credits" for s in sem_list]
sgpa_cols   = [f"sem{s}_sgpa" for s in sem_list]

def calc_row_cgpa(row):
    total_credits = 0.0
    total_points  = 0.0
    for sg_col, cr_col in zip(sgpa_cols, credit_cols):
        sg = row.get(sg_col)
        cr = row.get(cr_col)
        if pd.notna(sg) and pd.notna(cr):
            try:
                sgf = float(sg)
                crf = float(cr)
            except:
                continue
            total_credits += crf
            total_points  += sgf * crf
    if total_credits > 0:
        return round(total_points / total_credits, 2), int(total_credits) if float(total_credits).is_integer() else total_credits
    else:
        return pd.NA, 0

cgpa_vals, total_cred_vals = zip(*(calc_row_cgpa(r) for _, r in wide.iterrows()))
wide['total_credits'] = total_cred_vals
wide['cgpa']          = cgpa_vals

# ====== Order Columns ======
ordered_cols = ['roll_no', 'name']
for s in sem_list:
    ordered_cols.extend([f"sem{s}_sgpa", f"sem{s}_credits"])
ordered_cols.extend(['total_credits', 'cgpa'])
wide = wide[[c for c in ordered_cols if c in wide.columns]]

# ====== Sort and Save ======
wide = wide.sort_values(by='roll_no').reset_index(drop=True)
wide.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Done — saved: {OUTPUT_FILE} (rows: {len(wide)})")
