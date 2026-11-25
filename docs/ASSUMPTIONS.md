# Assumptions
Finance supplies the recognition policy and exchange-rate assumption in [Trust decisions](DECISIONS.md).
Core execution is offline. No live AI model has been called. The static presentation is deployed on Vercel Hobby.
Only the supplied calendar window is analyzed. Invalid dates cannot reliably be
attributed to a month and are reported separately. Unsupported-currency amounts
are not INR and cannot provide a finite unconditional revenue bound without a rate.
Monthly totals are calculated from accepted source records.
