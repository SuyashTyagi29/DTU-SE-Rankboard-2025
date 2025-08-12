import pandas as pd

df=pd.read_csv("final_results.csv")
df.dropna(inplace=True)
df.sort_values(by='roll_no')

# Detect all semester SGPA and credit columns automatically
sgpa_cols = sorted([c for c in df.columns if c.startswith('sem') and c.endswith('_sgpa')],
                   key=lambda x: int(x.split('_')[0][3:]))
cred_cols = sorted([c for c in df.columns if c.startswith('sem') and c.endswith('_credits')],
                   key=lambda x: int(x.split('_')[0][3:]))

# Ensure numeric
df[sgpa_cols] = df[sgpa_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
df[cred_cols] = df[cred_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

# Calculate total credits
df['total_credits'] = df[cred_cols].sum(axis=1)

# Calculate CGPA (weighted average of SGPA by credits)
def calc_cgpa(row):
    total_points = sum(row[sgpa] * row[cred] for sgpa, cred in zip(sgpa_cols, cred_cols))
    if row['total_credits'] > 0:
        return round(total_points / row['total_credits'], 3)
    return 0

df['cgpa'] = df.apply(calc_cgpa, axis=1)

# Save updated file
df.to_csv("final_results_updated.csv", index=False)
print("✅ CGPA and total credits recalculated & saved to final_results_updated.csv")
