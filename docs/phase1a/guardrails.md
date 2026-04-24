# Duplicate And False-Positive Guards

## Risks

- Direct thank-you URL visit.
- Thank-you page reload.
- Add-On event and helper event both firing.
- GTM thank-you POC and Add-On event both mapped to platforms.
- Failed validation firing a conversion.
- Browser event ID not matching Gravity Forms field `32.4`.

## Required Guards

Only one final source can be mapped to platform tags:

```text
Gravity Forms Add-On event
OR
Helper plugin event
OR
temporary GTM thank-you POC
```

Preferred final source:

```text
Helper plugin event
```

Do not fire final `school_inquiry_submit` based only on:

```text
/thank-you/?location=<slug>&inquiry=true
```

Required proof:

- Valid event token from confirmed submit, or
- server-generated confirmation payload.

The plugin stores consumed event IDs in `sessionStorage` and consumes the server token after the first successful REST payload fetch.
