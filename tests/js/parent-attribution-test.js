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
	'window.__cefaTests = { referrerIsOwnSite: referrerIsOwnSite, buildAdvertisingTouchFromUrl: buildAdvertisingTouchFromUrl };})();'
);
const localValues = {};
const context = {
	URL,
	Event: function Event() {},
	console,
	setTimeout,
	clearTimeout,
	window: {
		CEFAConversionTracking: {
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
			getItem() {
				return null;
			},
			setItem() {}
		},
		crypto: {
			randomUUID() {
				return 'test-uuid';
			}
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
		addEventListener() {},
		querySelector() {
			return null;
		},
		querySelectorAll() {
			return [];
		}
	}
};

vm.runInNewContext(source, context, { filename: sourcePath });

const tests = context.window.__cefaTests;
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

console.log('Parent attribution browser tests passed.');
