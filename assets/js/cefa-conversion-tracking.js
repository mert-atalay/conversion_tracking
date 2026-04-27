(function () {
	'use strict';

	var config = window.CEFAConversionTracking || {};
	var formId = Number(config.formId || 4);
	var eventFieldSelectors = config.eventFieldSelectors || [];
	var consumedKey = config.consumedKey || 'cefa_conversion_tracking_consumed_event_ids';
	var pendingKey = config.pendingKey || 'cefa_conversion_tracking_form4_pending';
	var queryFlag = config.queryFlag || 'cefa_tracking';
	var queryToken = config.queryToken || 'cefa_tracking_token';
	var restPayloadBase = config.restPayloadBase || '';
	var restEventBase = config.restEventBase || '';
	var microConsumedKey = config.microConsumedKey || 'cefa_conversion_tracking_micro_consumed';
	var formStartKey = config.formStartKey || 'cefa_conversion_tracking_form4_started';
	var clickDelayMs = Number(config.clickDelayMs || 0);
	var lastSubmitAttemptAt = 0;
	var validationObserverStarted = false;
	var trackedEvents = Array.isArray(config.trackedEvents)
		? config.trackedEvents
		: [
				'parent_inquiry_cta_click',
				'find_a_school_click',
				'phone_click',
				'email_click',
				'form_start',
				'form_submit_click',
				'validation_error'
			];

	function uuid() {
		if (window.crypto && typeof window.crypto.randomUUID === 'function') {
			return window.crypto.randomUUID();
		}

		return 'cefa_' + Date.now() + '_' + Math.random().toString(36).slice(2);
	}

	function readJson(key, fallback) {
		try {
			var raw = window.sessionStorage.getItem(key);
			return raw ? JSON.parse(raw) : fallback;
		} catch (error) {
			return fallback;
		}
	}

	function writeJson(key, value) {
		try {
			window.sessionStorage.setItem(key, JSON.stringify(value));
		} catch (error) {}
	}

	function normalizeText(value, maxLength) {
		var length = maxLength || 180;

		return String(value || '')
			.replace(/\s+/g, ' ')
			.trim()
			.slice(0, length);
	}

	function parseUrl(value) {
		try {
			return new URL(value, window.location.href);
		} catch (error) {
			return null;
		}
	}

	function currentUrl() {
		return parseUrl(window.location.href);
	}

	function getPagePath() {
		var url = currentUrl();

		return url ? url.pathname : window.location.pathname;
	}

	function getQueryParam(name, url) {
		var parsed = url || currentUrl();

		return parsed ? normalizeText(parsed.searchParams.get(name) || '') : '';
	}

	function schoolSlugFromPath(pathname) {
		var match = String(pathname || '').match(/^\/school\/([^/?#]+)/i);

		return match ? decodeURIComponent(match[1]) : '';
	}

	function inferPageType() {
		var path = getPagePath();

		if (/^\/school\/[^/]+\/?$/i.test(path)) {
			return 'school';
		}

		if (/^\/find-a-school\/?$/i.test(path)) {
			return 'find_a_school';
		}

		if (/submit-an-inquiry-today|inquire-form/i.test(path)) {
			return 'inquiry_form';
		}

		if (/thank-you/i.test(path)) {
			return 'thank_you';
		}

		return 'parent';
	}

	function readFieldValue(root, selectors) {
		var scope = root || document;

		for (var i = 0; i < selectors.length; i++) {
			var field = scope.querySelector(selectors[i]);

			if (field && field.value) {
				return normalizeText(field.value, 220);
			}
		}

		return '';
	}

	function findField(root, selectors) {
		var scope = root || document;

		for (var i = 0; i < selectors.length; i++) {
			var field = scope.querySelector(selectors[i]);

			if (field) {
				return field;
			}
		}

		return null;
	}

	function field32Value(root, subfield) {
		return readFieldValue(root, [
			'[name="input_32_' + subfield + '"]',
			'[name="input_32.' + subfield + '"]',
			'#input_' + formId + '_32_' + subfield,
			'input[data-cefa-si-meta="' + subfield + '"]'
		]);
	}

	function field32Field(root, subfield) {
		return findField(root, [
			'[name="input_32_' + subfield + '"]',
			'[name="input_32.' + subfield + '"]',
			'#input_' + formId + '_32_' + subfield,
			'input[data-cefa-si-meta="' + subfield + '"]'
		]);
	}

	function trackingFormFrom(root) {
		if (root && root.matches && root.matches('form#gform_' + formId)) {
			return root;
		}

		if (root && root.closest) {
			return root.closest('form#gform_' + formId);
		}

		if (root && root.querySelector) {
			return root.querySelector('form#gform_' + formId);
		}

		return null;
	}

	function selectedOptionText(select) {
		var option = select && select.selectedOptions && select.selectedOptions[0];

		return option ? normalizeText(option.textContent || '', 220) : '';
	}

	function syncFormTrackingFields(root) {
		var form = trackingFormFrom(root);

		if (!form) {
			return;
		}

		var programSelect = field32Field(form, '2');
		var programNameField = field32Field(form, '7');
		var programName = programSelect && programSelect.value ? selectedOptionText(programSelect) : '';

		if (programNameField && programName) {
			programNameField.value = programName;
		}

		var daysField = field32Field(form, '3');
		var checkedDays = Array.prototype.slice
			.call(form.querySelectorAll('input[id^="input_' + formId + '_32_3_"][type="checkbox"]:checked'))
			.map(function (field) {
				return normalizeText(field.value, 80);
			})
			.filter(Boolean);

		if (daysField && checkedDays.length) {
			daysField.value = checkedDays.join('|');
		}
	}

	function readFormContext(root) {
		syncFormTrackingFields(root);

		var selectedSlug = field32Value(root, '5') || getQueryParam('location');
		var landingSlug = schoolSlugFromPath(getPagePath());

		return {
			form_id: String(formId),
			form_family: 'parent_inquiry',
			lead_type: 'cefa_lead',
			lead_intent: 'inquire_now',
			school_selected_id: field32Value(root, '1'),
			school_selected_slug: selectedSlug,
			school_selected_name: field32Value(root, '6'),
			school_landing_slug: landingSlug,
			school_match_status: landingSlug && selectedSlug ? (landingSlug === selectedSlug ? 'matched' : 'changed') : 'unknown',
			program_id: field32Value(root, '2'),
			program_name: field32Value(root, '7'),
			days_per_week: field32Value(root, '3'),
			inquiry_event_id: field32Value(root, '4') || getPendingEventId()
		};
	}

	function normalizedMicroPayload(payload) {
		var keys = [
			'event_scope',
			'page_context',
			'page_type',
			'page_url',
			'page_path',
			'tracking_source',
			'click_url',
			'click_text',
			'link_url',
			'link_text',
			'link_domain',
			'link_path',
			'cta_id',
			'cta_text',
			'cta_url',
			'cta_location',
			'lead_type',
			'lead_intent',
			'form_id',
			'form_family',
			'school_selected_id',
			'school_selected_slug',
			'school_selected_name',
			'school_landing_id',
			'school_landing_slug',
			'school_match_status',
			'program_id',
			'program_name',
			'days_per_week',
			'inquiry_event_id',
			'phone_number',
			'email_target',
			'validation_error_count'
		];
		var normalized = {
			event: payload.event,
			event_id: payload.event_id || uuid()
		};

		keys.forEach(function (key) {
			normalized[key] = payload[key] === undefined || payload[key] === null ? '' : payload[key];
		});

		return normalized;
	}

	function mergePayload(base, extra) {
		Object.keys(extra || {}).forEach(function (key) {
			if (extra[key] !== '') {
				base[key] = extra[key];
			}
		});

		return base;
	}

	function baseMicroPayload(eventName) {
		return {
			event: eventName,
			event_id: uuid(),
			event_scope: 'micro',
			page_context: 'parent',
			page_type: inferPageType(),
			page_url: window.location.href,
			page_path: getPagePath(),
			tracking_source: 'helper_plugin'
		};
	}

	function eventIsTracked(eventName) {
		return trackedEvents.indexOf(eventName) !== -1;
	}

	function pushMicroPayload(payload, delayMs) {
		if (!payload || !eventIsTracked(payload.event)) {
			return;
		}

		function push() {
			window.dataLayer = window.dataLayer || [];
			window.dataLayer.push(normalizedMicroPayload(payload));
		}

		if (delayMs && delayMs > 0) {
			window.setTimeout(push, delayMs);
			return;
		}

		push();
	}

	function microConsumedIds() {
		var ids = readJson(microConsumedKey, []);

		return Array.isArray(ids) ? ids : [];
	}

	function markMicroConsumed(key) {
		if (!key) {
			return false;
		}

		var ids = microConsumedIds();

		if (ids.indexOf(key) !== -1) {
			return false;
		}

		ids.push(key);
		writeJson(microConsumedKey, ids.slice(-50));

		return true;
	}

	function inferCtaLocation(element) {
		if (!element || !element.closest) {
			return 'unknown';
		}

		if (element.getAttribute('data-cefa-cta-location')) {
			return normalizeText(element.getAttribute('data-cefa-cta-location'), 80);
		}

		if (element.closest('header, [class*="header"], [class*="site-header"]')) {
			return 'header';
		}

		if (element.closest('footer, [class*="footer"], [class*="site-footer"]')) {
			return 'footer';
		}

		if (element.closest('nav, [class*="nav"], [class*="menu"]')) {
			return 'navigation';
		}

		if (element.closest('[class*="hero"], [id*="hero"]')) {
			return 'hero';
		}

		if (element.closest('main, article, section')) {
			return 'content';
		}

		return 'unknown';
	}

	function inferClickEvent(anchor, url) {
		var explicitEvent = anchor.getAttribute('data-cefa-event');

		if (explicitEvent && eventIsTracked(explicitEvent)) {
			return explicitEvent;
		}

		var href = String(anchor.getAttribute('href') || '');
		var path = url ? url.pathname : href;

		if (/^tel:/i.test(href)) {
			return 'phone_click';
		}

		if (/^mailto:/i.test(href)) {
			return 'email_click';
		}

		if (/find-a-school/i.test(path)) {
			return 'find_a_school_click';
		}

		if (/submit-an-inquiry-today|inquire-form|inquiry/i.test(path) || /kindertales\.com/i.test(href)) {
			return 'parent_inquiry_cta_click';
		}

		return '';
	}

	function inferCtaId(eventName, anchor) {
		var explicitId = anchor.getAttribute('data-cefa-cta-id') || anchor.getAttribute('data-cefa-cta');

		if (explicitId) {
			return normalizeText(explicitId, 120);
		}

		return inferPageType() + '_' + eventName;
	}

	function buildClickPayload(eventName, anchor, url) {
		var href = String(anchor.getAttribute('href') || '');
		var text = normalizeText(anchor.innerText || anchor.textContent || anchor.getAttribute('aria-label') || anchor.title || href);
		var payload = baseMicroPayload(eventName);

		mergePayload(payload, {
			click_url: url ? url.href : href,
			click_text: text,
			link_url: url ? url.href : href,
			link_text: text,
			link_domain: url ? url.hostname : '',
			link_path: url ? url.pathname : '',
			cta_id: inferCtaId(eventName, anchor),
			cta_text: text,
			cta_url: url ? url.href : href,
			cta_location: inferCtaLocation(anchor),
			lead_intent: 'parent_inquiry_cta_click' === eventName ? 'inquire_now' : ''
		});

		mergePayload(payload, readFormContext(document));

		if ('parent_inquiry_cta_click' === eventName && !payload.school_selected_slug) {
			payload.school_selected_slug = getQueryParam('location', url) || payload.school_landing_slug;
			payload.school_match_status =
				payload.school_landing_slug && payload.school_selected_slug
					? payload.school_landing_slug === payload.school_selected_slug
						? 'matched'
						: 'changed'
					: 'unknown';
		}

		if ('phone_click' === eventName) {
			payload.phone_number = normalizeText(href.replace(/^tel:/i, ''), 80);
		}

		if ('email_click' === eventName) {
			payload.email_target = normalizeText(href.replace(/^mailto:/i, '').split('?')[0], 120);
		}

		if ('find_a_school_click' === eventName) {
			payload.lead_intent = 'find_a_school';
		}

		return payload;
	}

	function shouldDelayNavigation(event, anchor) {
		if (!clickDelayMs || clickDelayMs < 1 || !anchor || 'A' !== anchor.tagName) {
			return false;
		}

		if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
			return false;
		}

		if (anchor.target && '_self' !== anchor.target) {
			return false;
		}

		if (anchor.hasAttribute('download')) {
			return false;
		}

		return !/^#|^javascript:/i.test(String(anchor.getAttribute('href') || ''));
	}

	function delayedNavigate(anchor) {
		window.setTimeout(function () {
			window.location.href = anchor.href;
		}, clickDelayMs);
	}

	function initMicroClickTracking() {
		if (document.documentElement.getAttribute('data-cefa-micro-clicks-attached') === '1') {
			return;
		}

		document.documentElement.setAttribute('data-cefa-micro-clicks-attached', '1');
		document.addEventListener(
			'click',
			function (event) {
				var anchor = event.target && event.target.closest ? event.target.closest('a[href]') : null;

				if (!anchor) {
					return;
				}

				var url = parseUrl(anchor.getAttribute('href') || '');
				var eventName = inferClickEvent(anchor, url);

				if (!eventName) {
					return;
				}

				var payload = buildClickPayload(eventName, anchor, url);

				if (shouldDelayNavigation(event, anchor)) {
					event.preventDefault();
					pushMicroPayload(payload);
					delayedNavigate(anchor);
					return;
				}

				pushMicroPayload(payload);
			},
			true
		);
	}

	function findEventIdField(scope) {
		var root = scope || document;

		for (var i = 0; i < eventFieldSelectors.length; i++) {
			var found = root.querySelector(eventFieldSelectors[i]);
			if (found) {
				return found;
			}
		}

		return root.querySelector('[id$="_32_4"], [name="input_32_4"], [name="input_32.4"]');
	}

	function ensureEventId(scope) {
		var field = findEventIdField(scope);

		if (!field) {
			return '';
		}

		if (!field.value) {
			field.value = uuid();
		}

		writePending(field.value);

		return field.value;
	}

	function writePending(eventId) {
		if (!eventId) {
			return;
		}

		writeJson(pendingKey, {
			event_id: eventId,
			form_id: String(formId),
			ts: Date.now()
		});
	}

	function getFormInstances() {
		return Array.prototype.slice.call(document.querySelectorAll('form#gform_' + formId));
	}

	function isRendered(element) {
		return !!(element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length));
	}

	function getPrimaryForm() {
		var forms = getFormInstances();

		for (var i = 0; i < forms.length; i++) {
			if (isRendered(forms[i])) {
				return forms[i];
			}
		}

		return forms[0] || null;
	}

	function getValidationForm() {
		var forms = getFormInstances();

		for (var i = 0; i < forms.length; i++) {
			if (forms[i].querySelector('.gform_validation_errors, .validation_error, .gfield_error, [aria-invalid="true"]')) {
				return forms[i];
			}
		}

		var validationNode = document.querySelector('.gform_validation_errors, .validation_error');

		return validationNode && validationNode.closest ? validationNode.closest('form') || getPrimaryForm() : getPrimaryForm();
	}

	function hasValidationErrorState(form) {
		if (!form) {
			return false;
		}

		return !!(
			form.querySelector('.gform_validation_errors, .validation_error, .gfield_error, [aria-invalid="true"]') ||
			document.querySelector('#gform_' + formId + '_validation_container, .gform_validation_errors')
		);
	}

	function initFormTracking() {
		var forms = getFormInstances();

		if (!forms.length) {
			return;
		}

		forms.forEach(function (form) {
			if (!form || form.getAttribute('data-cefa-conversion-tracking-attached') === '1') {
				return;
			}

			form.setAttribute('data-cefa-conversion-tracking-attached', '1');
			ensureEventId(form);

			form.addEventListener(
				'submit',
				function () {
					var eventId = ensureEventId(form);

					if (!eventId) {
						return;
					}

					writePending(eventId);
				},
				true
			);

			initFormMicroTracking(form);
		});
	}

	function formStartConsumed(form, inquiryEventId) {
		var key = [
			formStartKey,
			inquiryEventId || 'no_inquiry_event',
			window.location.pathname
		].join(':');

		return !markMicroConsumed(key);
	}

	function pushFormStart(form) {
		var inquiryEventId = ensureEventId(form);

		if (formStartConsumed(form, inquiryEventId)) {
			return;
		}

		var payload = mergePayload(baseMicroPayload('form_start'), readFormContext(form));
		payload.inquiry_event_id = inquiryEventId || payload.inquiry_event_id;
		pushMicroPayload(payload, 1500);
	}

	function pushSubmitClick(form) {
		var now = Date.now();

		if (now - lastSubmitAttemptAt < 750) {
			return;
		}

		lastSubmitAttemptAt = now;

		var inquiryEventId = ensureEventId(form);
		var payload = mergePayload(baseMicroPayload('form_submit_click'), readFormContext(form));

		payload.inquiry_event_id = inquiryEventId || payload.inquiry_event_id;
		pushMicroPayload(payload, 1750);
	}

	function initFormMicroTracking(form) {
		if (!form || form.getAttribute('data-cefa-conversion-micro-attached') === '1') {
			return;
		}

		form.setAttribute('data-cefa-conversion-micro-attached', '1');

		['focusin', 'change', 'input'].forEach(function (eventName) {
			form.addEventListener(
				eventName,
				function (event) {
					if (!event.target || !event.target.matches || event.target.matches('button, [type="submit"], [type="hidden"]')) {
						return;
					}

					pushFormStart(form);
				},
				true
			);
		});

		form.addEventListener(
			'click',
			function (event) {
				var target = event.target;

				if (
					!target ||
					!target.matches ||
					!target.matches('button[type="submit"], input[type="submit"], #gform_submit_button_' + formId)
				) {
					return;
				}

				pushSubmitClick(form);
			},
			true
		);

		form.addEventListener(
			'submit',
			function () {
				pushSubmitClick(form);
			},
			true
		);
	}

	function initValidationErrorTracking() {
		var form = getValidationForm();

		if (!hasValidationErrorState(form)) {
			return;
		}

		var errorCount = form.querySelectorAll('.gfield_error, [aria-invalid="true"]').length;

		if (errorCount < 1) {
			return;
		}

		var key = [
			'validation_error',
			getPendingEventId() || window.location.pathname,
			String(errorCount)
		].join(':');

		if (!markMicroConsumed(key)) {
			return;
		}

		var payload = mergePayload(baseMicroPayload('validation_error'), readFormContext(form));
		payload.validation_error_count = String(errorCount);
		payload.inquiry_event_id = payload.inquiry_event_id || getPendingEventId();
		pushMicroPayload(payload);
	}

	function scheduleValidationErrorTracking() {
		window.setTimeout(initValidationErrorTracking, 3000);
	}

	function initValidationObserver() {
		if (validationObserverStarted || !window.MutationObserver || !document.body) {
			return;
		}

		validationObserverStarted = true;

		new window.MutationObserver(function () {
			if (
				document.querySelector(
					'#gform_' + formId + '_validation_container, form#gform_' + formId + ' .gform_validation_errors, form#gform_' + formId + ' .validation_error, form#gform_' + formId + ' .gfield_error'
				)
			) {
				scheduleValidationErrorTracking();
			}
		}).observe(document.body, {
			childList: true,
			subtree: true
		});
	}

	function initAjaxConfirmationTracking() {
		var frames = document.querySelectorAll('#gform_ajax_frame_' + formId);

		for (var i = 0; i < frames.length; i++) {
			attachAjaxFrameTracking(frames[i]);
		}
	}

	function attachAjaxFrameTracking(frame) {
		if (!frame || frame.getAttribute('data-cefa-conversion-tracking-frame') === '1') {
			return;
		}

		frame.setAttribute('data-cefa-conversion-tracking-frame', '1');
		frame.addEventListener('load', function () {
			if (ajaxFrameHasConfirmation(frame)) {
				schedulePendingPayloadFetch();
			}
		});
	}

	function ajaxFrameHasConfirmation(frame) {
		try {
			var doc = frame.contentDocument || (frame.contentWindow && frame.contentWindow.document);

			return !!(doc && doc.querySelector('#gform_confirmation_wrapper_' + formId));
		} catch (error) {
			return false;
		}
	}

	function getConsumedIds() {
		var ids = readJson(consumedKey, []);
		return Array.isArray(ids) ? ids : [];
	}

	function hasConsumed(eventId) {
		return getConsumedIds().indexOf(eventId) !== -1;
	}

	function markConsumed(eventId) {
		if (!eventId) {
			return;
		}

		var ids = getConsumedIds();

		if (ids.indexOf(eventId) === -1) {
			ids.push(eventId);
		}

		writeJson(consumedKey, ids.slice(-20));
	}

	function dataLayerAlreadyHas(payload) {
		if (!payload || !payload.event_id || !Array.isArray(window.dataLayer)) {
			return false;
		}

		for (var i = 0; i < window.dataLayer.length; i++) {
			var item = window.dataLayer[i];

			if (
				item &&
				item.event === 'school_inquiry_submit' &&
				item.event_id === payload.event_id
			) {
				return true;
			}
		}

		return false;
	}

	function cleanTrackingParams() {
		try {
			var url = new URL(window.location.href);
			url.searchParams.delete(queryFlag);
			url.searchParams.delete(queryToken);
			window.history.replaceState(null, '', url.toString());
		} catch (error) {}
	}

	function pushPayload(payload) {
		if (!payload || payload.event !== 'school_inquiry_submit' || !payload.event_id) {
			return;
		}

		if (hasConsumed(payload.event_id) || dataLayerAlreadyHas(payload)) {
			cleanTrackingParams();
			return;
		}

		payload.inquiry_success_url = window.location.href;
		window.dataLayer = window.dataLayer || [];
		window.dataLayer.push(payload);
		markConsumed(payload.event_id);
		try {
			window.sessionStorage.removeItem(pendingKey);
		} catch (error) {}
		cleanTrackingParams();
	}

	function fetchPayload(token) {
		if (!restPayloadBase || !token) {
			return;
		}

		window
			.fetch(restPayloadBase + encodeURIComponent(token), {
				credentials: 'same-origin',
				cache: 'no-store',
				headers: {
					Accept: 'application/json'
				}
			})
			.then(function (response) {
				if (!response.ok) {
					throw new Error('Tracking payload unavailable.');
				}

				return response.json();
			})
			.then(pushPayload)
			.catch(cleanTrackingParams);
	}

	function fetchPayloadByEventId(eventId) {
		if (!restEventBase || !eventId) {
			return;
		}

		window
			.fetch(restEventBase + encodeURIComponent(eventId), {
				credentials: 'same-origin',
				cache: 'no-store',
				headers: {
					Accept: 'application/json'
				}
			})
			.then(function (response) {
				if (!response.ok) {
					throw new Error('Tracking payload unavailable.');
				}

				return response.json();
			})
			.then(pushPayload)
			.catch(cleanTrackingParams);
	}

	function schedulePendingPayloadFetch() {
		window.setTimeout(function () {
			fetchPayloadByEventId(getPendingEventId());
		}, 250);
	}

	function getPendingEventId() {
		var pending = readJson(pendingKey, null);

		if (!pending || String(pending.form_id) !== String(formId) || !pending.event_id) {
			return '';
		}

		if (pending.ts && Date.now() - Number(pending.ts) > 30 * 60 * 1000) {
			try {
				window.sessionStorage.removeItem(pendingKey);
			} catch (error) {}
			return '';
		}

		return String(pending.event_id);
	}

	function initThankYouTracking() {
		var url;

		try {
			url = new URL(window.location.href);
		} catch (error) {
			return;
		}

		if (url.searchParams.get(queryFlag) !== '1' && url.searchParams.get('inquiry') !== 'true') {
			return;
		}

		var token = url.searchParams.get(queryToken);

		if (token) {
			fetchPayload(token);
			return;
		}

		fetchPayloadByEventId(getPendingEventId());
	}

	function init() {
		initMicroClickTracking();
		initFormTracking();
		initAjaxConfirmationTracking();
		initValidationObserver();
		initValidationErrorTracking();
		initThankYouTracking();
	}

	document.addEventListener('DOMContentLoaded', init);
	document.addEventListener('gform_post_render', function () {
		init();
		scheduleValidationErrorTracking();
	});
	document.addEventListener('gform_confirmation_loaded', function (event) {
		if (!event.detail || Number(event.detail.formId) === formId) {
			schedulePendingPayloadFetch();
		}
	});
	document.addEventListener('gform/postRender', function (event) {
		if (!event.detail || Number(event.detail.formId) === formId) {
			init();
			scheduleValidationErrorTracking();
		}
	});

	if (window.jQuery) {
		window.jQuery(document).on('gform_post_render gform_post_rendered', function (event, renderedFormId) {
			if (Number(renderedFormId) === formId) {
				init();
				scheduleValidationErrorTracking();
			}
		});

		window.jQuery(document).on('gform_confirmation_loaded', function (event, submittedFormId) {
			if (Number(submittedFormId) === formId) {
				schedulePendingPayloadFetch();
			}
		});
	}
})();
