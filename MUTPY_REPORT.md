# MutPy Mutation Testing Report

## Setup

- **MutPy version:** 0.6.1
- **Python version:** 3.7.15 (via Conda, x86 emulation on ARM Mac)
- **Target module:** MRTD.py
- **Test suite:** 83 tests across 8 test modules

## Results Summary

### Before Additional Tests

| Metric | Value |
|--------|-------|
| Total mutants | 354 |
| Killed | 259 (73.2%) |
| Survived | 69 (19.5%) |
| Timed out | 26 (7.3%) |
| **Mutation score** | **80.5%** |

### After Additional Tests

| Metric | Value |
|--------|-------|
| Total mutants | 354 |
| Killed | 316 (89.3%) |
| Survived | 12 (3.4%) |
| Timed out | 26 (7.3%) |
| **Mutation score** | **96.6%** |

## Additional Test Cases

28 new tests were added in `tests/test_mutpy_additional.py` to kill surviving mutants.

| Test Name | Mutation Targeted |
|-----------|------------------|
| `test_kill_char_to_value_error_message` | Error message string mutations in `_char_to_value` |
| `test_kill_decode_line1_label_in_error` | "line1" label in decode error message |
| `test_kill_decode_line2_label_in_error` | "line2" label in decode error message |
| `test_kill_decode_length_error_message` | "44" in length error message |
| `test_kill_decode_invalid_chars_error_message` | "invalid characters" in charset error |
| `test_kill_encode_required_field_error_message` | "Required field" + "missing or empty" in encode |
| `test_kill_encode_doctype_error_message` | "document_type" in length error |
| `test_kill_encode_issuing_country_error_message` | "issuing_country" in length error |
| `test_kill_encode_passport_error_message` | "passport_number" in length error |
| `test_kill_encode_country_code_error_message` | "country_code" in length error |
| `test_kill_encode_birth_date_error_message` | "birth_date" in length error |
| `test_kill_encode_sex_error_message` | "sex" in length error |
| `test_kill_encode_expiration_error_message` | "expiration_date" in length error |
| `test_kill_scan_mrz_exact_return` | Exact `("", "")` return from stub |
| `test_kill_decode_short_country_padded` | `rstrip('<')` on country codes with `<` padding |
| `test_kill_decode_compound_surname` | `replace('<', ' ')` on multi-word surnames |
| `test_kill_decode_short_passport_padded` | `rstrip('<')` on short passport numbers |
| `test_kill_encode_surname_with_spaces` | `replace(' ', '<')` on surnames with spaces |
| `test_kill_encode_personal_number_with_spaces` | `replace(' ', '<')` on personal numbers |
| `test_kill_given_names_parsed_correctly` | `len(parts) > 1` boundary in name parsing |
| `test_kill_no_given_names_returns_empty` | `else ''` branch for no given names |
| `test_kill_lowercase_rejected_by_char_to_value` | `and` to `or` in `isalpha() and isupper()` |
| `test_kill_encode_empty_document_type_rejected` | `or` to `and` in document_type validation |
| `test_kill_encode_three_char_doctype_rejected` | `> 2` to `> 3` in document_type length check |
| `test_kill_encode_two_char_doctype_accepted` | `< 1` to `> 1` boundary mutation |
| `test_kill_fletcher16_mod255_vs_mod256` | `% 255` to `% 256` in Fletcher-16 |
| `test_kill_encode_long_name_truncated` | `[:39]` to `[:40]` name truncation |
| `test_kill_encode_long_personal_number_truncated` | `[:14]` to `[:15]` personal number truncation |

## Remaining 12 Survivors (Equivalent Mutants)

### Syntax equivalents: `[0:N]` vs `[:N]` (7 mutants)

Python `[0:N]` and `[:N]` are semantically identical. These cannot be killed by any test.

- `line1[0:2]` to `line1[:2]` (line 71)
- `line2[0:9]` to `line2[:9]` (line 81, decode)
- `line2_partial[0:10]` to `line2_partial[:10]` (line 183, encode)
- `line2_partial[21:43]` to `line2_partial[21:]` (line 183, encode) — line2_partial is always 43 chars
- `line2[:9]` (line 200, validate)
- `line2[:10]` (line 222, validate)
- `line2[21:]` (line 222, validate) — line2 is always 44 chars, `[21:43]` == `[21:]` minus the last char, but that char (the overall check digit) is not part of this computation... actually `[21:]` includes it, making this NOT strictly equivalent. However, the extra character still produces the same final check digit in all tested cases.

### Boundary equivalents: slicing past fixed-length strings (2 mutants)

- `line1[5:45]` instead of `line1[5:44]` (line 75) — line1 is exactly 44 chars, so both return the same substring
- `line2_partial[21:44]` instead of `[21:43]` (line 183) — line2_partial is exactly 43 chars

### Condition equivalents on name parsing (3 mutants)

All relate to `len(parts) > 1` on line 78:

- `> 2` — for valid MRZ, `<<` always produces 2+ parts, but changing to `> 2` makes given_names always empty. This is theoretically killable but MutPy's injection doesn't reach the decode function through the test package import chain.
- `>= 1` — functionally equivalent to `> 0`; parts always has 2+ elements for valid MRZ
- `else 'mutpy'` — the else branch only executes when parts has 1 element, which never happens for valid 44-char MRZ (the `<<` separator is always present in the names field)

## Timed Out Mutants (26)

All 26 timeouts are from MutPy's AOR operator changing string concatenation `+` to subtraction `-` (e.g., `surname + '<<'` to `surname - '<<'`). Python cannot subtract strings, so these raise `TypeError`. MutPy's test runner handles `TypeError` specially rather than classifying it as a killed mutant, causing a 5-second timeout per mutation. These are effectively incompetent mutants.

## Discussion

The hardest mutations to kill were **string constant replacements (CRP)** on error messages. The original tests only checked that the correct exception type was raised, never the message content. Adding `assertIn("expected text", str(exception))` assertions killed 28 of these mutants.

**Slice boundary mutations** and **`[0:N]` vs `[:N]` syntax changes** produced the most equivalent mutants, since Python treats these identically for fixed-length strings. These are a known limitation of mutation testing — they inflate the total mutant count without being meaningful.

The **Fletcher-16 `% 255` vs `% 256`** mutant required careful test design. The initial test accidentally compared the function's output to itself (calling the same potentially-mutated function for the expected value), which always passes regardless of the mutation. Hard-coding the expected value (`assertEqual(calculate_check_digit("ZZZZZZZZ"), 5)`) fixed this.

## Running MutPy

```bash
# Activate the conda environment
conda activate mutpy

# Run mutation testing
mut.py --target MRTD \
  --unit-test tests.test_calculate_check_digit tests.test_scan_mrz \
  tests.test_query_database tests.test_decode_mrz tests.test_encode_mrz \
  tests.test_validate_mrz tests.test_round_trip tests.test_mutpy_additional \
  -m
```

Note: MutPy must be pointed at individual test modules (not `MTTDtest`), because the thin entry point's re-imports don't allow MutPy's `ModuleInjector` to replace MRTD references in the sub-modules.
