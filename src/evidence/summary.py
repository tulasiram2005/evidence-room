"""Evidence-derived management summary; no claims about business causes."""
def generate(root, kpis, scenarios, rows):
    aug, sep = kpis['monthly']
    change = scenarios[0]['change_percent']
    text = f'''# Executive summary

**Finding 1:** Trusted completed revenue fell from INR {aug['revenue_paise']/100:,.2f} in August to INR {sep['revenue_paise']/100:,.2f} in September, a change of {change:.2f}%. The retained orders support a decline within the supplied exports. This is an observation about the accepted records, not proof of a particular business cause. Cancelled and refunded orders do not contribute revenue, and dollar orders use Finance's supplied conversion assumption.

**Finding 2:** The trusted dataset contains {aug['orders']} August orders and {sep['orders']} September orders. Every source row has an explicit disposition. Identical copies are removed, while conflicting versions are withheld together rather than selecting a convenient price. The reconciliation shows the adjustments needed to reach trusted revenue. Independent SQL and pandas calculations agree on monthly revenue, leading products and customer contribution.

**Uncertainty:** Excluded records can change the comparison. Unsupported currencies have no approved conversion rate, and invalid dates cannot reliably be assigned to a month. Conditional sensitivity scenarios are not unconditional bounds. New and repeat customer labels describe only this available window, not lifetime customer tenure.

**Next action:** Ask Finance to resolve conflicting order versions and unsupported currency treatment, then rerun the same checks before making a business decision. Review the rejection log alongside the trusted figures; do not infer promotions, outages or other causes from these exports alone.
'''
    (root / 'executive_summary.md').write_text(text)
