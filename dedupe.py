import pandas as pd
from fuzzywuzzy import fuzz

# Sample data
data = [
    {"first_name": "Jane", "last_name": "Doe", "email": None, "phone": "1234567890"},
    {"first_name": "John", "last_name": None, "email": "john.doe@example.com", "phone": None},
    {"first_name": "J.", "last_name": "Doe", "email": None, "phone": None},
    {"first_name": None, "last_name": "Smith", "email": "s.smith@example.com", "phone": "0987654321"},
    {"first_name": "Jane", "last_name": "Doe", "email": None, "phone": None},
    {"first_name": "John", "last_name": "Smith", "email": None, "phone": None},
    {"first_name": "J", "last_name": None, "email": None, "phone": None},
]

# as a chief
df = pd.DataFrame(data)

def normalize_name(name):
    """Normalize name by removing periods and converting to lowercase."""
    if name:
        return name.replace(".", "").strip().lower()
    return ""

def deduplicate_records(df):
    deduplicated = []

    for _, row in df.iterrows():
        current_first = normalize_name(row['first_name'])
        current_last = normalize_name(row['last_name'])

        if any((row.equals(d) for d in deduplicated)):
            continue

        for existing in deduplicated:
            existing_first = normalize_name(existing['first_name'])
            existing_last = normalize_name(existing['last_name'])

            score_first = fuzz.partial_ratio(current_first, existing_first)
            score_last = fuzz.partial_ratio(current_last, existing_last)

            # Adjust the threshold for first names
            if score_first > 85 and score_last > 85:
                # Merge logic: prioritize the most complete record
                if row['email'] and not existing['email']:
                    existing['email'] = row['email']
                if row['phone'] and not existing['phone']:
                    existing['phone'] = row['phone']
                break
        else:
            # If no match found, add the record to deduplicated
            deduplicated.append(row.to_dict())
    
    # Remove any duplicates explicitly defined by first and last names being very similar
    final_records = []
    for record in deduplicated:
        if not any(
            (fuzz.partial_ratio(normalize_name(record['first_name']), normalize_name(r['first_name'])) > 85 and
             fuzz.partial_ratio(normalize_name(record['last_name']), normalize_name(r['last_name'])) > 85)
            for r in final_records
        ):
            final_records.append(record)

    return pd.DataFrame(final_records)

deduplicated_df = deduplicate_records(df)
print(deduplicated_df)
