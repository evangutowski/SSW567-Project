import json
import time
import csv
from MRTD import encode_mrz, decode_mrz, validate_mrz

INPUT_FILE = "records_decoded.json"
OUTPUT_CSV = "timing_results.csv"

def transform(record):
    return {
        "document_type": "P",
        "issuing_country": record["line1"]["issuing_country"],
        "surname": record["line1"]["last_name"],
        "given_names": record["line1"]["given_name"],
        "passport_number": record["line2"]["passport_number"],
        "country_code": record["line2"]["country_code"],
        "birth_date": record["line2"]["birth_date"],
        "sex": record["line2"]["sex"],
        "expiration_date": record["line2"]["expiration_date"],
        "personal_number": record["line2"].get("personal_number", "")
    }

def run_encode(records, use_tests=False):
    for r in records:
        fields = transform(r)
        line1, line2 = encode_mrz(fields)

        if use_tests:
            decoded = decode_mrz(line1, line2)
            validate_mrz(line1, line2)

def measure(records, use_tests):
    start = time.perf_counter()
    run_encode(records, use_tests)
    end = time.perf_counter()
    return end - start

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_records = json.load(f)["records_decoded"]

    sizes = [100] + list(range(1000, 10001, 1000))
    results = []

    for k in sizes:
        subset = all_records[:k]
        t_no_test = measure(subset, use_tests=False)
        t_with_test = measure(subset, use_tests=True)
        results.append([k, t_no_test, t_with_test])
        print(f"Done {k}")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "t_no_test", "t_with_test"])
        writer.writerows(results)

if __name__ == "__main__":
    main()