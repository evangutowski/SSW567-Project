import json
from MRTD import encode_mrz

INPUT_FILE = "records_decoded.json"
OUTPUT_FILE = "records_encoded.json"


def transform_record(record):
    """Convert dataset format → encode_mrz input format"""

    line1 = record["line1"]
    line2 = record["line2"]

    return {
        "document_type": "P",
        "issuing_country": line1["issuing_country"],
        "surname": line1["last_name"],
        "given_names": line1["given_name"],
        "passport_number": line2["passport_number"],
        "country_code": line2["country_code"],
        "birth_date": line2["birth_date"],
        "sex": line2["sex"],
        "expiration_date": line2["expiration_date"],
        "personal_number": line2.get("personal_number", "")
    }


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)["records_decoded"]

    encoded_list = []

    for record in data:
        fields = transform_record(record)
        line1, line2 = encode_mrz(fields)
        encoded_list.append(f"{line1};{line2}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"records_encoded": encoded_list}, f, indent=4)


if __name__ == "__main__":
    main()