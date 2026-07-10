'use strict';

const fs = require('fs');
const vm = require('vm');

function assert(condition, message) {
	if (!condition) {
		throw new Error(message);
	}
}

const sourcePath = 'assets/js/cefa-conversion-tracking.js';
const source = fs.readFileSync(sourcePath, 'utf8').replace(
	/\}\)\(\);\s*$/,
	'window.__cefaTests = { referrerIsOwnSite: referrerIsOwnSite, buildAdvertisingTouchFromUrl: buildAdvertisingTouchFromUrl, captureSignedAttribution: captureSignedAttribution, storeAttributionFormToken: storeAttributionFormToken, syncAttributionFormToken: syncAttributionFormToken };})();'
);
const localValues = {};
const sessionValues = {};
const fetchCalls = [];
const documentEvents = [];
const captureFields = [];
const form = {
	querySelector(selector) {
		return selector === 'input[name="cefa_capture_token"]' ? captureFields[0] || null : null;
	},
	appendChild(field) {
		captureFields.push(field);
	}
};
const context = {
	URL,
	Event: function Event() {},
	console,
	setTimeout,
	clearTimeout,
	window: {
		CEFAConversionTracking: {
			attributionMode: 'shadow',
			ledgerMode: 'shadow',
			runtimeProfile: 'attribution_only',
			restAttributionUrl: 'https://cefa.ca/wp-json/cefa-conversion-tracking/v1/attribution-capture',
			forms: [{ id: 4 }],
			ownHosts: [
				'cefa.ca',
				'www.cefa.ca',
				'franchise.cefa.ca',
				'www.franchisecefa.com'
			]
		},
		location: {
			href: 'https://cefa.ca/find-a-school/',
			hostname: 'cefa.ca',
			pathname: '/find-a-school/',
			protocol: 'https:'
		},
		localStorage: {
			getItem(key) {
				return localValues[key] || null;
			},
			setItem(key, value) {
				localValues[key] = String(value);
			}
		},
		sessionStorage: {
			getItem(key) {
				return sessionValues[key] || null;
			},
			setItem(key, value) {
				sessionValues[key] = String(value);
			}
		},
		crypto: {
			randomUUID() {
				return 'test-uuid';
			}
		},
		fetch(url, options) {
			fetchCalls.push({ url, options });
			return Promise.resolve({
				ok: true,
				json() {
					return Promise.resolve({ capture_token: 'signed.capture_token-1' });
				}
			});
		},
		setTimeout,
		clearTimeout
	},
	document: {
		referrer: 'https://www.cefa.ca/school/oakville-eighth-line/',
		cookie: '',
		readyState: 'loading',
		documentElement: {
			getAttribute() {
				return null;
			},
			setAttribute() {}
		},
		addEventListener(name) {
			documentEvents.push(name);
		},
		createElement() {
			return {};
		},
		querySelector() {
			return null;
		},
		querySelectorAll(selector) {
			return selector === 'form#gform_4' ? [form] : [];
		}
	}
};

vm.runInNewContext(source, context, { filename: sourcePath });

const tests = context.window.__cefaTests;
assert(documentEvents.indexOf('DOMContentLoaded') !== -1, 'Attribution-only mode did not initialize capture.');
assert(documentEvents.indexOf('gform_confirmation_loaded') === -1, 'Attribution-only mode registered a confirmation listener.');
assert(documentEvents.indexOf('gform_post_render') === -1, 'Attribution-only mode registered a form event listener.');
assert(tests.referrerIsOwnSite('www.cefa.ca'), 'Parent www host was not recognized as internal.');
assert(tests.referrerIsOwnSite('franchise.cefa.ca'), 'Approved CEFA cross-property host was not recognized as internal.');
assert(!tests.referrerIsOwnSite('notcefa.ca'), 'Substring-like external host was incorrectly recognized as internal.');

const internalTouch = tests.buildAdvertisingTouchFromUrl();
assert(internalTouch.source === 'direct', 'Internal navigation became a referral source.');
assert(internalTouch.channel === 'direct', 'Internal navigation became a referral channel.');
assert(internalTouch.referrer === '', 'Internal referrer URL was retained.');

context.document.referrer = 'https://www.google.com/search?q=cefa';
const organicTouch = tests.buildAdvertisingTouchFromUrl();
assert(organicTouch.source === 'google', 'Google organic source classification failed.');
assert(organicTouch.channel === 'organic_search', 'Google organic channel classification failed.');

const capturePromise = tests.captureSignedAttribution(
	new URL('https://cefa.ca/?utm_source=google&utm_medium=cpc&utm_campaign=shadow-qa&gclid=test-gclid')
);
assert(fetchCalls.length === 1, 'Signed attribution fallback did not call the REST endpoint.');
assert(fetchCalls[0].options.method === 'POST', 'Signed attribution fallback did not use POST.');
assert(fetchCalls[0].options.headers['X-CEFA-Attribution'] === '1', 'Signed attribution request marker is missing.');
const captureBody = JSON.parse(fetchCalls[0].options.body);
assert(captureBody.params.gclid === 'test-gclid', 'Signed attribution fallback omitted the GCLID.');
assert(captureBody.params.utm_campaign === 'shadow-qa', 'Signed attribution fallback omitted the campaign.');
assert(captureBody.referrer === 'https://www.google.com/search', 'Signed attribution fallback retained a referrer query.');

capturePromise.then(function () {
	assert(captureFields.length === 1, 'Signed capture token was not injected into the supported form.');
	assert(captureFields[0].type === 'hidden', 'Signed capture token field was not hidden.');
	assert(captureFields[0].name === 'cefa_capture_token', 'Signed capture token field name changed.');
	assert(captureFields[0].value === 'signed.capture_token-1', 'Signed capture token field value was not preserved.');

	console.log('Parent attribution browser tests passed.');
});
