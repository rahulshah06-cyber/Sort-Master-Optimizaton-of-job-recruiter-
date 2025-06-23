import pandas as pd
import re
import heapq
import datetime

df = pd.read_csv("job_candidates.csv")

df.drop_duplicates(inplace=True)

irrelevant_columns = ['Contact', 'Job Portal', 'Company Profile']
df.drop(columns=[col for col in irrelevant_columns if col in df.columns], inplace=True)

df['Experience'] = df['Experience'].fillna("0 Years")
df['skills'] = df['skills'].fillna("")

def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'\s+', ' ', text.strip())
    return text

text_cols = ['Contact Person', 'Experience', 'Qualifications', 'location', 'Country',
             'Work Type', 'Preference', 'Job Title', 'Role', 'Job Description', 'Benefits', 'skills',
             'Responsibilities', 'Company']

for col in text_cols:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)

def extract_min_experience(exp):
    match = re.search(r'(\d+)', str(exp))
    return int(match.group(1)) if match else 0

df['Experience_Value'] = df['Experience'].apply(extract_min_experience)

def salary_to_midpoint(s):
    if isinstance(s, str):
        numbers = [int(n.replace('K', '')) for n in re.findall(r'\d+K', s)]
        if len(numbers) == 2:
            return sum(numbers) / 2
    return None

df['Salary_Mid'] = df['Salary Range'].apply(salary_to_midpoint)

df = df[df['Experience_Value'] > 0]

df.reset_index(drop=True, inplace=True)

df.to_csv("cleaned_candidates.csv", index=False)
print("\nData cleaned and saved to 'cleaned_candidates.csv'.")

def apply_filters(df_original):
    while True:
        df_filtered = df_original.copy()
        print("\n🔍 Apply filters (press Enter to skip any field):")
        exp_filter = input("Min Experience (in years, e.g., 3): ").strip()
        qual_filter = input("Qualifications (e.g., PhD, MBA): ").strip().lower()
        work_type_filter = input("Work Type (e.g., Full-Time, Intern): ").strip().lower()
        job_title_filter = input("Job Title (e.g., Web Developer): ").strip().lower()
        role_filter = input("Role (e.g., Frontend Web Developer): ").strip().lower()
        location_filter = input("Location (e.g., New York, Santiago): ").strip().lower()

        if exp_filter.isdigit():
            df_filtered = df_filtered[df_filtered['Experience_Value'] >= int(exp_filter)]
        if qual_filter:
            df_filtered = df_filtered[df_filtered['Qualifications'].str.lower().str.contains(qual_filter)]
        if work_type_filter:
            df_filtered = df_filtered[df_filtered['Work Type'].str.lower().str.contains(work_type_filter)]
        if job_title_filter:
            df_filtered = df_filtered[df_filtered['Job Title'].str.lower().str.contains(job_title_filter)]
        if role_filter:
            df_filtered = df_filtered[df_filtered['Role'].str.lower().str.contains(role_filter)]
        if location_filter:
            df_filtered = df_filtered[df_filtered['location'].str.lower().str.contains(location_filter)]

        if df_filtered.empty:
            print("\nNo candidates found with the given filters. Please try again.")
        else:
            return df_filtered.reset_index(drop=True)

df = apply_filters(df)

candidates = [(i, df.loc[i, 'Experience_Value'], df.loc[i]) for i in df.index]

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])
        return merge(left, right)
    return arr

def merge(left, right):
    result = []
    while left and right:
        if left[0][1] >= right[0][1]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2][1]
    left = [x for x in arr if x[1] > pivot]
    middle = [x for x in arr if x[1] == pivot]
    right = [x for x in arr if x[1] < pivot]
    return quick_sort(left) + middle + quick_sort(right)

def heap_sort(arr):
    heap = [(-x[1], i, x) for i, x in enumerate(arr)]
    heapq.heapify(heap)
    sorted_list = []
    while heap:
        _, _, item = heapq.heappop(heap)
        sorted_list.append(item)
    return sorted_list

sorted_merge = merge_sort(candidates.copy())
sorted_quick = quick_sort(candidates.copy())
sorted_heap = heap_sort(candidates.copy())

def build_rank_dict(sorted_list):
    return {item[0]: rank for rank, item in enumerate(sorted_list)}

merge_ranks = build_rank_dict(sorted_merge)
quick_ranks = build_rank_dict(sorted_quick)
heap_ranks = build_rank_dict(sorted_heap)

average_ranks = []
for i in df.index:
    avg_rank = (merge_ranks[i] + quick_ranks[i] + heap_ranks[i]) / 3
    average_ranks.append((i, avg_rank, df.loc[i]))

final_sorted = sorted(average_ranks, key=lambda x: x[1])

try:
    top_n = int(input("\nHow many top candidates would you like to see? (default = 5): ").strip())
except ValueError:
    top_n = 5

top_n = min(top_n, len(final_sorted))  # Prevent overflow

print(f"\nTop {top_n} Recommended Candidates Based on Filtered Results:\n")
top_rows = []

for rank, (_, score, row) in enumerate(final_sorted[:top_n], start=1):
    print(f"{rank}. {row['Contact Person']} | Exp: {row['Experience']} | Skills: {row['skills']}")
    row_data = row.to_dict()
    row_data['Consensus Rank'] = rank
    row_data['Average Rank Score'] = round(score, 2)
    top_rows.append(row_data)

export_df = pd.DataFrame(top_rows)
export_format = input("\nExport results? Type 'csv', 'excel' or press Enter to skip: ").strip().lower()
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if export_format == "csv":
    filename = f"top_candidates_{timestamp}.csv"
    export_df.to_csv(filename, index=False)
    print(f"Results saved to '{filename}'")
elif export_format == "excel":
    filename = f"top_candidates_{timestamp}.xlsx"
    export_df.to_excel(filename, index=False)
    print(f"Results saved to '{filename}'")
else:
    print("Unsupported export format or skipped.")
