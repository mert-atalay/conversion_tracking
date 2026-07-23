'use strict';

const { chromium } = require('playwright');

const targetUrl = process.argv[2];
const expectedContext = process.argv[3];

if (!targetUrl || !expectedContext) {
	console.error('Usage: node tools/franchise-shadow-browser-qa.js <url> <site-context>');
	process.exit(2);
}

const finalEvents = new Set([
	'franchise_inquiry_submit',
	'real_estate_site_submit',
	'cefa_franchise_inquiry_dispatch',
	'cefa_real_estate_site_dispatch',
	'generate_lead'
]);

(async () => {
	const browser = await chromium.launch({ headless: true });
	const context = await browser.newContext();
	const page = await context.newPage();
	const captureResponses = [];
	const conversionRequests = [];

	page.on('response', (response) => {
		if (response.url().includes('/cefa-conversion-tracking/v1/attribution-capture')) {
			captureResponses.push(response.status());
		}
	});

	page.on('request', (request) => {
		const url = request.url();
		const isGoogleSubmitConversion =
			/pagead\/conversion/i.test(url) &&
			!/\/wcm(?:[?#]|$)/i.test(url);

		if (
			isGoogleSubmitConversion ||
			/[?&]ev=Lead(?:&|$)/i.test(url) ||
			/[?&]en=generate_lead(?:&|$)/i.test(url)
		) {
			conversionRequests.push(url.replace(/[?#].*$/, ''));
		}
	});

	await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
	await page.waitForSelector('form#gform_1, form#gform_2', { timeout: 30000 });
	await page.waitForTimeout(5000);

	const result = await page.evaluate((knownFinalEvents) => {
		const config = window.CEFAConversionTracking || {};
		const forms = Array.from(document.querySelectorAll('form#gform_1, form#gform_2'));
		const pushedFinalEvents = (window.dataLayer || [])
			.map((item) => (item && typeof item === 'object' ? item.event : ''))
			.filter((eventName) => knownFinalEvents.includes(eventName));

		return {
			site_context: String(config.siteContext || ''),
			runtime_profile: String(config.runtimeProfile || ''),
			attribution_mode: String(config.attributionMode || ''),
			ledger_mode: String(config.ledgerMode || ''),
			plugin_version_063_loaded: Array.from(document.scripts).some((script) =>
				/cefa-conversion-tracking\.js\?ver=0\.6\.3(?:&|$)/.test(script.src || '')
			),
			forms: forms.map((form) => {
				const token = form.querySelector('input[name="cefa_capture_token"]');

				return {
					id: form.id,
					capture_token_present: Boolean(token && token.value && token.value.length > 20)
				};
			}),
			final_events_seen: pushedFinalEvents
		};
	}, Array.from(finalEvents));

	result.capture_rest_statuses = captureResponses;
	result.conversion_requests_seen = Array.from(new Set(conversionRequests));
	result.pass = Boolean(
		result.site_context === expectedContext &&
		result.runtime_profile === 'attribution_only' &&
		result.attribution_mode === 'shadow' &&
		result.ledger_mode === 'shadow' &&
		result.plugin_version_063_loaded &&
		result.forms.length > 0 &&
		result.forms.every((form) => form.capture_token_present) &&
		result.final_events_seen.length === 0 &&
		result.conversion_requests_seen.length === 0
	);

	console.log(JSON.stringify(result, null, 2));
	await browser.close();
	process.exit(result.pass ? 0 : 1);
})().catch((error) => {
	console.error(error && error.message ? error.message : String(error));
	process.exit(1);
});
