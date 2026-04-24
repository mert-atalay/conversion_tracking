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

	function initFormTracking() {
		var form = document.querySelector('#gform_' + formId);

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
		initFormTracking();
		initAjaxConfirmationTracking();
		initThankYouTracking();
	}

	document.addEventListener('DOMContentLoaded', init);
	document.addEventListener('gform_post_render', init);
	document.addEventListener('gform_confirmation_loaded', function (event) {
		if (!event.detail || Number(event.detail.formId) === formId) {
			schedulePendingPayloadFetch();
		}
	});
	document.addEventListener('gform/postRender', function (event) {
		if (!event.detail || Number(event.detail.formId) === formId) {
			init();
		}
	});

	if (window.jQuery) {
		window.jQuery(document).on('gform_confirmation_loaded', function (event, submittedFormId) {
			if (Number(submittedFormId) === formId) {
				schedulePendingPayloadFetch();
			}
		});
	}
})();
