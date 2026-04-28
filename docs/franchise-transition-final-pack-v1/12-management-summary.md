# Management Summary

## What has been completed

The parent staging tracking problem has been solved with a CEFA-owned helper plugin approach.

One successful parent inquiry now produces a clean `school_inquiry_submit` event, and GTM can map that event to GA4 and future destinations.

## What is next

The next decision is franchise tracking, especially Meta dataset handling.

## Recommendation in plain language

Do not break live franchise Meta learning just to make the architecture clean immediately.

Instead:

1. Keep active Canada franchise campaigns on the shared dataset temporarily.
2. Add clean franchise parameters and custom conversions.
3. Test a separate franchise Canada dataset in parallel.
4. Migrate gradually.
5. Set up USA franchise separately by default.

## Why

Canada franchise may already be relying on the shared dataset for Meta optimization. Abruptly changing the dataset or optimization event can weaken performance.

But keeping everything shared forever is not acceptable because parent enrollment and franchise-investor leads are different business outcomes.

## Final future state

```text
Parent Canada -> parent measurement boundary
Franchise Canada -> Canada franchise measurement boundary
Franchise USA -> USA franchise measurement boundary
```

Shared infrastructure can remain. Shared optimization datasets should not remain the clean future state.
