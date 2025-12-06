import re

# Original (greedy - captures SIGN instead of BRIDE_SIGN)
pattern1 = r'ICM2_.*_([A-Z_]+)\.[a-zA-Z0-9]+'

# Better: match non-greedy up to the doc type
pattern2 = r'ICM2_.+?_([A-Z_]+)\.[a-zA-Z0-9]+'

# Best: match the uploader specifically (citizen_N where N is digits)
pattern3 = r'ICM2_citizen_\d+_([A-Z_]+)\.[a-zA-Z0-9]+'

# Or match everything except the last underscore-separated part
pattern4 = r'ICM2_(?:.+?)_([A-Z_]+)\.[a-zA-Z0-9]+'

test_files = ['ICM2_citizen_12_BRIDE_SIGN.jpeg', 'ICM2_citizen_12_GROOM_SIGN.jpeg', 'ICM2_citizen_12_MARRIAGE.jpeg']

print("Pattern 1 (greedy):")
for f in test_files:
    match = re.match(pattern1, f)
    print(f"  {f}: {match.group(1) if match else 'NO MATCH'}")

print("\nPattern 2 (non-greedy):")
for f in test_files:
    match = re.match(pattern2, f)
    print(f"  {f}: {match.group(1) if match else 'NO MATCH'}")

print("\nPattern 3 (specific uploader):")
for f in test_files:
    match = re.match(pattern3, f)
    print(f"  {f}: {match.group(1) if match else 'NO MATCH'}")

print("\nPattern 4 (non-capturing group):")
for f in test_files:
    match = re.match(pattern4, f)
    print(f"  {f}: {match.group(1) if match else 'NO MATCH'}")
