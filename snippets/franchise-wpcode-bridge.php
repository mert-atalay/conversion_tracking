<?php
/**
 * CEFA Franchise Conversion Tracking Bridge for WPCode.
 *
 * Deployment fallback for live franchise sites when direct PHP plugin-file
 * writes are blocked by the host. This snippet keeps the same Phase 1
 * tracking boundary as the plugin and does not alter CRM/Synuma delivery.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! function_exists( 'cefa_franchise_ct_bootstrap' ) ) {
	/**
	 * Register CEFA franchise tracking hooks once.
	 *
	 * @return void
	 */
	function cefa_franchise_ct_bootstrap(): void {
		static $bootstrapped = false;

		if ( $bootstrapped ) {
			return;
		}

		$bootstrapped = true;

		add_action( 'rest_api_init', 'cefa_franchise_ct_register_routes' );
		add_action( 'wp_footer', 'cefa_franchise_ct_print_bridge_js', 99 );

		foreach ( array( 1, 2 ) as $form_id ) {
			add_action(
				'gform_pre_submission_' . $form_id,
				static function () use ( $form_id ): void {
					cefa_franchise_ct_backfill_attribution_post_fields();
					cefa_franchise_ct_ensure_posted_event_id( $form_id );
				},
				5
			);

			add_action(
				'gform_after_submission_' . $form_id,
				static function ( array $entry, array $form ) use ( $form_id ): void {
					unset( $form );
					cefa_franchise_ct_store_payload( $entry, $form_id );
				},
				20,
				2
			);

			add_filter(
				'gform_confirmation_' . $form_id,
				static function ( $confirmation, array $form, array $entry, bool $is_ajax ) use ( $form_id ) {
					unset( $form, $is_ajax );

					return cefa_franchise_ct_attach_confirmation_token( $confirmation, $entry, $form_id );
				},
				999,
				4
			);
		}
	}

	/**
	 * Return the active site context.
	 *
	 * @return array<string, string>
	 */
	function cefa_franchise_ct_context(): array {
		$host = '';

		if ( isset( $_SERVER['HTTP_HOST'] ) ) {
			$host = sanitize_text_field( wp_unslash( $_SERVER['HTTP_HOST'] ) );
		}

		if ( '' === $host ) {
			$host = (string) wp_parse_url( home_url(), PHP_URL_HOST );
		}

		$host = strtolower( preg_replace( '/:\d+$/', '', $host ) );

		if ( in_array( $host, array( 'franchisecefa.com', 'www.franchisecefa.com', 'cefafranusdev.wpenginepowered.com' ), true ) ) {
			return array(
				'site_context' => 'franchise_us',
				'market'       => 'usa',
				'country'      => 'US',
			);
		}

		return array(
			'site_context' => 'franchise_ca',
			'market'       => 'canada',
			'country'      => 'CA',
		);
	}

	/**
	 * Register the one-time payload endpoint.
	 *
	 * @return void
	 */
	function cefa_franchise_ct_register_routes(): void {
		register_rest_route(
			'cefa-franchise-conversion/v1',
			'/payload/(?P<event_id>[A-Za-z0-9._:-]{8,128})',
			array(
				'methods'             => array( 'GET', 'POST' ),
				'callback'            => 'cefa_franchise_ct_rest_payload',
				'permission_callback' => '__return_true',
				'args'                => array(
					'event_id' => array(
						'type'              => 'string',
						'required'          => true,
						'sanitize_callback' => 'sanitize_text_field',
					),
				),
			)
		);
	}

	/**
	 * Return and consume a server-confirmed payload.
	 *
	 * @param WP_REST_Request $request REST request.
	 * @return array<string, mixed>|WP_Error
	 */
	function cefa_franchise_ct_rest_payload( WP_REST_Request $request ) {
		nocache_headers();

		$event_id = cefa_franchise_ct_normalize_event_id( (string) $request->get_param( 'event_id' ) );

		if ( '' === $event_id ) {
			return new WP_Error( 'invalid_event_id', 'Invalid event ID.', array( 'status' => 400 ) );
		}

		$key     = cefa_franchise_ct_transient_key( $event_id );
		$payload = get_transient( $key );

		if ( ! is_array( $payload ) ) {
			return new WP_Error( 'payload_not_found', 'Tracking payload is no longer available.', array( 'status' => 404 ) );
		}

		delete_transient( $key );

		return $payload;
	}

	/**
	 * Ensure the submit POST has an event ID for this request.
	 *
	 * @param int $form_id Gravity Forms form ID.
	 * @return string
	 */
	function cefa_franchise_ct_ensure_posted_event_id( int $form_id ): string {
		$event_id = '';

		foreach ( array( 'cefa_ct_event_id_' . $form_id, 'cefa_ct_event_id' ) as $key ) {
			if ( isset( $_POST[ $key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing
				$event_id = cefa_franchise_ct_normalize_event_id( sanitize_text_field( wp_unslash( $_POST[ $key ] ) ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing
				break;
			}
		}

		if ( '' === $event_id ) {
			$event_id = wp_generate_uuid4();
		}

		$_POST[ 'cefa_ct_event_id_' . $form_id ] = $event_id; // phpcs:ignore WordPress.Security.NonceVerification.Missing
		$_POST['cefa_ct_event_id']              = $event_id; // phpcs:ignore WordPress.Security.NonceVerification.Missing

		return $event_id;
	}

	/**
	 * Backfill the existing GAConnector hidden fields from first-party cookies.
	 *
	 * This does not change business/CRM fields. It only fills the tracking-only
	 * hidden fields already present on Forms 1 and 2.
	 *
	 * @return void
	 */
	function cefa_franchise_ct_backfill_attribution_post_fields(): void {
		foreach ( cefa_franchise_ct_attribution_fields() as $key => $field_id ) {
			$value = cefa_franchise_ct_cookie_attribution_value( $key );

			if ( '' === $value ) {
				continue;
			}

			$post_key = 'input_' . $field_id;

			if ( 'gclid' === $key && '' !== cefa_franchise_ct_current_gclid() ) {
				$_POST[ $post_key ] = $value; // phpcs:ignore WordPress.Security.NonceVerification.Missing
				continue;
			}

			if ( cefa_franchise_ct_should_write_post_field( $post_key ) ) {
				$_POST[ $post_key ] = $value; // phpcs:ignore WordPress.Security.NonceVerification.Missing
			}
		}
	}

	/**
	 * Determine whether a tracking POST field is missing or placeholder-like.
	 *
	 * @param string $post_key POST key.
	 * @return bool
	 */
	function cefa_franchise_ct_should_write_post_field( string $post_key ): bool {
		if ( ! isset( $_POST[ $post_key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing
			return true;
		}

		$value = strtolower( trim( sanitize_text_field( wp_unslash( $_POST[ $post_key ] ) ) ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing

		return '' === $value || in_array( $value, array( 'undefined', 'null', '(not set)', 'not set' ), true );
	}

	/**
	 * Ensure the Gravity Forms entry has a tracking event ID in entry meta.
	 *
	 * @param array<string, mixed> $entry   Gravity Forms entry.
	 * @param int                  $form_id Gravity Forms form ID.
	 * @return string
	 */
	function cefa_franchise_ct_ensure_entry_event_id( array $entry, int $form_id ): string {
		$entry_id = (int) rgar( $entry, 'id' );
		$event_id = '';

		if ( function_exists( 'gform_get_meta' ) && $entry_id > 0 ) {
			$event_id = cefa_franchise_ct_normalize_event_id( (string) gform_get_meta( $entry_id, 'cefa_conversion_tracking_event_id' ) );
		}

		if ( '' === $event_id ) {
			$event_id = cefa_franchise_ct_ensure_posted_event_id( $form_id );
		}

		if ( function_exists( 'gform_update_meta' ) && $entry_id > 0 ) {
			gform_update_meta( $entry_id, 'cefa_conversion_tracking_event_id', $event_id, $form_id );
		}

		return $event_id;
	}

	/**
	 * Build and store a server-confirmed payload after successful submission.
	 *
	 * @param array<string, mixed> $entry   Gravity Forms entry.
	 * @param int                  $form_id Gravity Forms form ID.
	 * @return array<string, mixed>
	 */
	function cefa_franchise_ct_store_payload( array $entry, int $form_id ): array {
		if ( 'spam' === (string) rgar( $entry, 'status' ) ) {
			return array();
		}

		$payload = cefa_franchise_ct_payload_from_entry( $entry, $form_id );

		if ( empty( $payload['event_id'] ) ) {
			return array();
		}

		set_transient( cefa_franchise_ct_transient_key( (string) $payload['event_id'] ), $payload, 30 * MINUTE_IN_SECONDS );

		return $payload;
	}

	/**
	 * Add the one-time payload event ID to Gravity Forms page/redirect confirmations.
	 *
	 * @param string|array         $confirmation Gravity Forms confirmation.
	 * @param array<string, mixed> $entry        Gravity Forms entry.
	 * @param int                  $form_id      Gravity Forms form ID.
	 * @return string|array
	 */
	function cefa_franchise_ct_attach_confirmation_token( $confirmation, array $entry, int $form_id ) {
		$payload = cefa_franchise_ct_store_payload( $entry, $form_id );

		if ( empty( $payload['event_id'] ) ) {
			return $confirmation;
		}

		$params = array(
			'cefa_tracking'          => '1',
			'cefa_tracking_event_id' => rawurlencode( (string) $payload['event_id'] ),
		);

		if ( is_array( $confirmation ) && ! empty( $confirmation['redirect'] ) ) {
			$confirmation['redirect'] = add_query_arg( $params, (string) $confirmation['redirect'] );

			return $confirmation;
		}

		if ( is_array( $confirmation ) && 'page' === (string) rgar( $confirmation, 'type' ) ) {
			$query_string = ltrim( trim( (string) rgar( $confirmation, 'queryString' ) ), '?' );
			$existing     = array();

			if ( '' !== $query_string ) {
				wp_parse_str( $query_string, $existing );
			}

			$confirmation['queryString'] = build_query( array_merge( $existing, $params ) );

			return $confirmation;
		}

		return $confirmation;
	}

	/**
	 * Build a non-PII dataLayer payload from a saved entry.
	 *
	 * @param array<string, mixed> $entry   Gravity Forms entry.
	 * @param int                  $form_id Gravity Forms form ID.
	 * @return array<string, mixed>
	 */
	function cefa_franchise_ct_payload_from_entry( array $entry, int $form_id ): array {
		$context  = cefa_franchise_ct_context();
		$event_id = cefa_franchise_ct_ensure_entry_event_id( $entry, $form_id );
		$payload  = array(
			'event'               => 1 === $form_id ? 'franchise_inquiry_submit' : 'real_estate_site_submit',
			'event_id'            => $event_id,
			'event_scope'         => 'primary',
			'site_context'        => $context['site_context'],
			'business_unit'       => 'franchise',
			'market'              => $context['market'],
			'country'             => $context['country'],
			'form_id'             => (string) $form_id,
			'form_family'         => 1 === $form_id ? 'franchise_inquiry' : 'site_inquiry',
			'lead_type'           => 1 === $form_id ? 'franchise_lead' : 'real_estate_lead',
			'lead_intent'         => 1 === $form_id ? 'franchise_inquiry' : 'submit_a_site',
			'inquiry_success'     => true,
			'event_source_url'    => esc_url_raw( (string) rgar( $entry, 'source_url' ) ),
			'inquiry_success_url' => '',
			'tracking_source'     => 'helper_plugin',
			'deployment_source'   => 'wpcode_bridge',
		);

		if ( 1 === $form_id ) {
			$payload['location_interest']             = cefa_franchise_ct_entry_value( $entry, '32' );
			$payload['location_interest_name']        = cefa_franchise_ct_location_name( $payload['location_interest'] );
			$payload['investment_range']              = cefa_franchise_ct_entry_value( $entry, '7' );
			$payload['opening_timeline']              = cefa_franchise_ct_entry_value( $entry, '10' );
			$payload['school_count_goal']             = cefa_franchise_ct_entry_value( $entry, '11' );
			$payload['ownership_structure']           = cefa_franchise_ct_entry_value( $entry, '12' );
			$payload['location_availability_status']  = 'unknown';
		} else {
			$payload['site_offered_by']               = cefa_franchise_ct_entry_value( $entry, '39' );
			$payload['property_square_footage_range'] = cefa_franchise_ct_entry_value( $entry, '34' );
			$payload['outdoor_space_range']           = cefa_franchise_ct_entry_value( $entry, '35' );
			$payload['availability_timeline']         = cefa_franchise_ct_entry_value( $entry, '36' );
		}

		foreach ( cefa_franchise_ct_attribution_fields() as $key => $field_id ) {
			$payload[ $key ] = cefa_franchise_ct_entry_attribution_value( $entry, $key, $field_id );
		}

		return $payload;
	}

	/**
	 * Return the GAConnector field mapping already present on franchise forms.
	 *
	 * @return array<string, string>
	 */
	function cefa_franchise_ct_attribution_fields(): array {
		return array(
			'lc_source'    => '14',
			'lc_medium'    => '15',
			'lc_campaign'  => '16',
			'lc_content'   => '17',
			'lc_term'      => '18',
			'lc_channel'   => '19',
			'lc_landing'   => '20',
			'lc_referrer'  => '21',
			'fc_source'    => '22',
			'fc_medium'    => '23',
			'fc_campaign'  => '24',
			'fc_content'   => '25',
			'fc_term'      => '26',
			'fc_channel'   => '27',
			'fc_referrer'  => '28',
			'gclid'        => '29',
			'ga_client_id' => '30',
		);
	}

	/**
	 * Return the GAConnector cookie mapping for the existing hidden fields.
	 *
	 * @return array<string, string>
	 */
	function cefa_franchise_ct_attribution_cookie_map(): array {
		return array(
			'lc_source'    => 'gaconnector_lc_source',
			'lc_medium'    => 'gaconnector_lc_medium',
			'lc_campaign'  => 'gaconnector_lc_campaign',
			'lc_content'   => 'gaconnector_lc_content',
			'lc_term'      => 'gaconnector_lc_term',
			'lc_channel'   => 'gaconnector_lc_channel',
			'lc_landing'   => 'gaconnector_lc_landing',
			'lc_referrer'  => 'gaconnector_lc_referrer',
			'fc_source'    => 'gaconnector_fc_source',
			'fc_medium'    => 'gaconnector_fc_medium',
			'fc_campaign'  => 'gaconnector_fc_campaign',
			'fc_content'   => 'gaconnector_fc_content',
			'fc_term'      => 'gaconnector_fc_term',
			'fc_channel'   => 'gaconnector_fc_channel',
			'fc_referrer'  => 'gaconnector_fc_referrer',
			'gclid'        => 'gaconnector_gclid',
			'ga_client_id' => 'gaconnector_GA_Client_ID',
		);
	}

	/**
	 * Read an attribution value from the saved entry and fall back to cookies.
	 *
	 * @param array<string, mixed> $entry    Gravity Forms entry.
	 * @param string               $key      Attribution key.
	 * @param string               $field_id Field ID.
	 * @return string
	 */
	function cefa_franchise_ct_entry_attribution_value( array $entry, string $key, string $field_id ): string {
		$value = cefa_franchise_ct_entry_value( $entry, $field_id );

		if ( 'gclid' === $key && '' !== cefa_franchise_ct_current_gclid() ) {
			return cefa_franchise_ct_current_gclid();
		}

		if ( '' !== $value && ! in_array( strtolower( $value ), array( 'undefined', 'null', '(not set)', 'not set' ), true ) ) {
			return $value;
		}

		return cefa_franchise_ct_cookie_attribution_value( $key );
	}

	/**
	 * Read and sanitize a Gravity Forms entry value.
	 *
	 * @param array<string, mixed> $entry    Gravity Forms entry.
	 * @param string               $field_id Field ID.
	 * @return string
	 */
	function cefa_franchise_ct_entry_value( array $entry, string $field_id ): string {
		$max_length = in_array( $field_id, array( '20', '21', '28' ), true ) ? 1000 : 220;

		return substr( sanitize_text_field( (string) rgar( $entry, $field_id ) ), 0, $max_length );
	}

	/**
	 * Read a sanitized attribution value from the current request cookies.
	 *
	 * @param string $key Attribution key.
	 * @return string
	 */
	function cefa_franchise_ct_cookie_attribution_value( string $key ): string {
		if ( 'gclid' === $key ) {
			$current_gclid = cefa_franchise_ct_current_gclid();

			return '' !== $current_gclid ? $current_gclid : cefa_franchise_ct_read_cookie( 'gaconnector_gclid', 220 );
		}

		if ( 'ga_client_id' === $key ) {
			$client_id = cefa_franchise_ct_read_cookie( 'gaconnector_GA_Client_ID', 220 );

			return '' !== $client_id ? $client_id : cefa_franchise_ct_ga_client_id_from_cookie();
		}

		$map = cefa_franchise_ct_attribution_cookie_map();

		if ( empty( $map[ $key ] ) ) {
			return '';
		}

		$max_length = in_array( $key, array( 'lc_landing', 'lc_referrer', 'fc_referrer' ), true ) ? 1000 : 220;

		return cefa_franchise_ct_read_cookie( $map[ $key ], $max_length );
	}

	/**
	 * Prefer the current Google Ads click ID from Google's own first-party cookie.
	 *
	 * @return string
	 */
	function cefa_franchise_ct_current_gclid(): string {
		$gcl_aw = cefa_franchise_ct_read_cookie( '_gcl_aw', 500 );

		if ( '' === $gcl_aw ) {
			return '';
		}

		$parts = explode( '.', $gcl_aw, 3 );

		if ( count( $parts ) < 3 ) {
			return '';
		}

		return substr( sanitize_text_field( $parts[2] ), 0, 220 );
	}

	/**
	 * Parse GA client ID from the `_ga` cookie when GAConnector did not expose it.
	 *
	 * @return string
	 */
	function cefa_franchise_ct_ga_client_id_from_cookie(): string {
		$ga_cookie = cefa_franchise_ct_read_cookie( '_ga', 220 );

		if ( '' === $ga_cookie ) {
			return '';
		}

		if ( 1 !== preg_match( '/^GA\d+\.\d+\.(.+)$/', $ga_cookie, $matches ) ) {
			return '';
		}

		return substr( sanitize_text_field( $matches[1] ), 0, 220 );
	}

	/**
	 * Read and sanitize a cookie.
	 *
	 * @param string $cookie_name Cookie name.
	 * @param int    $max_length  Maximum value length.
	 * @return string
	 */
	function cefa_franchise_ct_read_cookie( string $cookie_name, int $max_length ): string {
		if ( ! isset( $_COOKIE[ $cookie_name ] ) ) {
			return '';
		}

		return substr( sanitize_text_field( wp_unslash( $_COOKIE[ $cookie_name ] ) ), 0, $max_length );
	}

	/**
	 * Resolve a numeric location field to its public title when available.
	 *
	 * @param string $value Saved location value.
	 * @return string
	 */
	function cefa_franchise_ct_location_name( string $value ): string {
		if ( ! is_numeric( $value ) ) {
			return $value;
		}

		$title = get_the_title( (int) $value );

		return '' !== $title ? sanitize_text_field( $title ) : $value;
	}

	/**
	 * Normalize event IDs.
	 *
	 * @param string $event_id Event ID candidate.
	 * @return string
	 */
	function cefa_franchise_ct_normalize_event_id( string $event_id ): string {
		$event_id = trim( $event_id );

		if ( '' === $event_id || strlen( $event_id ) > 128 ) {
			return '';
		}

		return preg_match( '/^[A-Za-z0-9._:-]+$/', $event_id ) ? $event_id : '';
	}

	/**
	 * Payload transient key.
	 *
	 * @param string $event_id Event ID.
	 * @return string
	 */
	function cefa_franchise_ct_transient_key( string $event_id ): string {
		return 'cefa_fct_' . hash( 'sha256', $event_id );
	}

	/**
	 * Print the browser bridge.
	 *
	 * @return void
	 */
	function cefa_franchise_ct_print_bridge_js(): void {
		$context = cefa_franchise_ct_context();
		$config  = array(
			'restBase'       => esc_url_raw( rest_url( 'cefa-franchise-conversion/v1/payload/' ) ),
			'siteContext'    => $context['site_context'],
			'market'         => $context['market'],
			'country'        => $context['country'],
			'trackingSource' => 'helper_plugin',
			'formContracts'  => array(
				'1' => array(
					'event'       => 'franchise_inquiry_submit',
					'form_family' => 'franchise_inquiry',
					'lead_type'   => 'franchise_lead',
					'lead_intent' => 'franchise_inquiry',
				),
				'2' => array(
					'event'       => 'real_estate_site_submit',
					'form_family' => 'site_inquiry',
					'lead_type'   => 'real_estate_lead',
					'lead_intent' => 'submit_a_site',
				),
			),
		);
		?>
		<script>
		(function(w, d) {
			'use strict';
			var cfg = <?php echo wp_json_encode( $config ); ?>;
			var params = new URLSearchParams(w.location.search || '');
			var eventId = params.get('cefa_tracking_event_id') || '';
			var consumedKey = 'cefa_franchise_conversion_consumed_events';
			var microKey = 'cefa_franchise_conversion_micro_events';

			function readStore(key) {
				try {
					return JSON.parse(w.sessionStorage.getItem(key) || '[]');
				} catch (err) {
					return [];
				}
			}

			function writeStore(key, values) {
				try {
					w.sessionStorage.setItem(key, JSON.stringify(values.slice(-50)));
				} catch (err) {}
			}

			function hasStored(key, value) {
				return readStore(key).indexOf(value) !== -1;
			}

			function markStored(key, value) {
				var values = readStore(key);
				if (values.indexOf(value) === -1) {
					values.push(value);
					writeStore(key, values);
				}
			}

			function uuid() {
				if (w.crypto && typeof w.crypto.randomUUID === 'function') {
					return w.crypto.randomUUID();
				}
				return 'evt_' + Date.now() + '_' + Math.random().toString(16).slice(2);
			}

			function push(payload) {
				if (!payload || !payload.event || !payload.event_id || hasStored(consumedKey, payload.event_id)) {
					return;
				}
				payload.inquiry_success_url = w.location.href;
				w.dataLayer = w.dataLayer || [];
				w.dataLayer.push(payload);
				markStored(consumedKey, payload.event_id);
			}

			function fetchFinalPayload() {
				if (params.get('cefa_tracking') !== '1' || !eventId || hasStored(consumedKey, eventId)) {
					return;
				}
				w.fetch(cfg.restBase + encodeURIComponent(eventId), { method: 'POST', credentials: 'same-origin', cache: 'no-store' })
					.then(function(response) {
						if (!response.ok) {
							throw new Error('payload unavailable');
						}
						return response.json();
					})
					.then(push)
					.catch(function() {});
			}

			function formIdFromElement(element) {
				var form = element && element.closest ? element.closest('form[id^="gform_"]') : null;
				if (!form) {
					return '';
				}
				return String(form.id || '').replace('gform_', '');
			}

			function microPayload(eventName, formId) {
				var contract = cfg.formContracts[String(formId)] || {};
				return {
					event: eventName,
					event_id: uuid(),
					event_scope: 'micro',
					site_context: cfg.siteContext,
					business_unit: 'franchise',
					market: cfg.market,
					country: cfg.country,
					form_id: String(formId),
					form_family: contract.form_family || '',
					lead_type: contract.lead_type || '',
					lead_intent: contract.lead_intent || '',
					page_location: w.location.href,
					tracking_source: cfg.trackingSource,
					deployment_source: 'wpcode_bridge'
				};
			}

			function pushMicro(eventName, formId, onceKey) {
				var key = eventName + ':' + formId + ':' + (onceKey || '');
				if (hasStored(microKey, key)) {
					return;
				}
				w.dataLayer = w.dataLayer || [];
				w.dataLayer.push(microPayload(eventName, formId));
				markStored(microKey, key);
			}

			d.addEventListener('focusin', function(event) {
				var formId = formIdFromElement(event.target);
				if (formId === '1' || formId === '2') {
					pushMicro('form_start', formId, 'start');
				}
			}, true);

			d.addEventListener('click', function(event) {
				var target = event.target && event.target.closest ? event.target.closest('button, input[type="submit"]') : null;
				var formId = formIdFromElement(target);
				if ((formId === '1' || formId === '2') && target) {
					pushMicro('form_submit_click', formId, 'submit-click');
				}
			}, true);

			fetchFinalPayload();
		})(window, document);
		</script>
		<?php
	}

	cefa_franchise_ct_bootstrap();
}
