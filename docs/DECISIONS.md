# Trust decisions

Finance definitions are in `challenge_readme.md` and take precedence.
Revenue is quantity × order price for completed orders only, USD × 85.
Cancelled/refunded orders are excluded, never subtracted as refunds.
Status is trimmed and lowercased; COMPLETE remains unmapped.
Only valid dates, master keys and positive finite amounts qualify.
First valid completed date within August–September determines new/repeat;
same-day first orders are all new, not lifetime tenure.

| Rule | Treatment | Sensitivity |
|---|---|---|
| D01 | Identical raw fields: retain first, log subsequent copy | None |
| D02 | Conflicting order ID: quarantine every version | One lowest/highest amount version |
| D03 | Customer absent from master: reject | Accept customer key |
| D04 | Product absent from master: reject | Accept product key |
| D05 | Non-positive or nonfinite quantity/price: reject | Never repair |
| D06 | Unambiguous YYYY/MM/DD: normalize and flag | Reject slash dates |
| D07 | Invalid/impossible date: reject, unattributed month | Known positive amounts assigned to each side in conditional bounds |
| D08 | Trim and lowercase completed: accept | None |
| D09 | Other status: quarantine | Accept unmapped status |
| D10 | USD: exactly 85 INR/USD | Fixed supplied assumption |
| D11 | Other currency: quarantine | Face-value-only illustration, never a verified INR rate |
| D12 | Cancelled/refunded: non-revenue | None |

Additional checks reject blank order keys and dates outside the window.
Rules record every applicable reason; the primary reason uses duplicate/conflict,
then status, date, keys, amounts, format, unmapped status, currency precedence.
A duplicate cancelled/refunded row belongs to the duplicate bucket, not both.

Arithmetic: parse using Decimal, convert to integer INR paise exactly. Sub-paise
input fails rather than silently rounding. SQLite and pandas sum integer paise.
Display-only currency/percent rounding uses two decimals.
Raw field strings are retained; exported potentially executable spreadsheet text
is prefixed with an apostrophe. Genuine negative numeric values remain numeric.
The source CSVs and source line numbers preserve original text.

Waterfall starts with every dated completed-like row (excluding cancelled/refunded),
including unknown statuses, at mixed-currency face value. This is a deliberately
naive number, not comparable INR revenue. Signed reason adjustments reconcile it
exactly, followed by USD conversion. Undated records remain explicitly unattributed.
Confidence uses trusted row coverage; a mixed-currency value ratio would mislead.
Bounds are conditional on listed repairs and supplied amounts; no arbitrary price
repairs or invented exchange rates. Conflicting versions are never summed as one order.
