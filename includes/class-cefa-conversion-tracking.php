<?php
/**
 * Main plugin bootstrap.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Coordinates tracking hooks.
 */
final class CEFA_Conversion_Tracking {
	/**
	 * REST namespace.
	 */
	private const REST_NAMESPACE = 'cefa-conversion-tracking/v1';

	/**
	 * Initialize hooks.
	 *
	 * @return void
	 */
	public static function init(): void {
		add_action( 'init', array( 'CEFA_Conversion_Tracking_Attribution_Envelope', 'capture_request' ), 1 );
		add_action( 'init', array( 'CEFA_Conversion_Tracking_Attribution_Ledger', 'maybe_install' ), 2 );
		add_action( 'wp_enqueue_scripts', array( __CLASS__, 'enqueue_scripts' ) );
		add_action( 'rest_api_init', array( 'CEFA_Conversion_Tracking_REST_Controller', 'register_routes' ) );

		if ( 'attribution_only' === CEFA_Conversion_Tracking_Config::runtime_profile() ) {
			foreach ( CEFA_Conversion_Tracking_Config::active_form_ids() as $form_id ) {
				add_action(
					'gform_after_submission_' . $form_id,
					array( __CLASS__, 'persist_attribution_only' ),
					30,
					2
				);
			}

			return;
		}

		add_action( 'init', array( 'CEFA_Conversion_Tracking_Event_ID_Registry', 'maybe_install' ), 3 );

		foreach ( CEFA_Conversion_Tracking_Config::active_form_ids() as $form_id ) {
			add_action(
				'gform_pre_submission_' . $form_id,
				static function () use ( $form_id ): void {
					$form_config = CEFA_Conversion_Tracking_Config::form_config( $form_id );

					CEFA_Conversion_Tracking_Attribution::backfill_posted_fields( $form_config );
					CEFA_Conversion_Tracking_Attribution::apply_primary_compatibility_fields( $form_config );
					CEFA_Conversion_Tracking_Event_ID::ensure_event_id_before_submission( $form_config );
					CEFA_Conversion_Tracking_Submission_Identity::prepare_before_submission( $form_config );
				},
				5
			);
			add_action(
				'gform_pre_submission_' . $form_id,
				static function () use ( $form_id ): void {
					$form_config = CEFA_Conversion_Tracking_Config::form_config( $form_id );

					CEFA_Conversion_Tracking_Attribution::apply_parent_canonical_fields( $form_config );
					CEFA_Conversion_Tracking_Attribution::apply_parent_paid_click_fields( $form_config );
				},
				50
			);

			add_action(
				'gform_after_submission_' . $form_id,
				array( 'CEFA_Conversion_Tracking_Confirmation_Payload', 'store_after_submission_payload' ),
				20,
				2
			);
			add_filter(
				'gform_confirmation_' . $form_id,
				array( 'CEFA_Conversion_Tracking_Confirmation_Payload', 'prepare_confirmation_tracking' ),
				999,
				4
			);
		}
	}

	/**
	 * Save canonical shadow evidence without registering a conversion lifecycle.
	 *
	 * @param array<string, mixed> $entry Gravity Forms entry.
	 * @param array<string, mixed> $form  Gravity Forms form.
	 * @return void
	 */
	public static function persist_attribution_only( array $entry, array $form ): void {
		$form_config = CEFA_Conversion_Tracking_Config::form_config( (int) rgar( $form, 'id' ) );

		if ( empty( $form_config ) || 'spam' === (string) rgar( $entry, 'status' ) ) {
			return;
		}

		$entry = CEFA_Conversion_Tracking_Entry_Attribution::persist_after_submission( $entry, $form_config );

		CEFA_Conversion_Tracking_Attribution_Parity::persist_after_submission( $entry, $form_config );
	}

	/**
	 * Enqueue the lightweight browser bridge.
	 *
	 * The script runs on public pages only and self-activates when a supported
	 * Gravity Form or plugin tracking token is present.
	 *
	 * @return void
	 */
	public static function enqueue_scripts(): void {
		$handle = 'cefa-conversion-tracking';
		$src    = CEFA_CONVERSION_TRACKING_URL . 'assets/js/cefa-conversion-tracking.js';
		$ver    = CEFA_CONVERSION_TRACKING_VERSION;

		wp_enqueue_script(
			$handle,
			$src,
			array(),
			$ver,
			array(
				'in_footer' => true,
				'strategy'  => 'defer',
			)
		);

		wp_localize_script(
			$handle,
			'CEFAConversionTracking',
			array_merge(
				CEFA_Conversion_Tracking_Config::browser_config(),
				array(
					'restPayloadBase'       => esc_url_raw( rest_url( self::REST_NAMESPACE . '/tracking-payload/' ) ),
					'restEventBase'         => esc_url_raw( rest_url( self::REST_NAMESPACE . '/tracking-payload-by-event/' ) ),
					'restAttributionUrl'    => esc_url_raw( rest_url( self::REST_NAMESPACE . '/attribution-capture' ) ),
					'attributionMode'       => CEFA_Conversion_Tracking_Config::attribution_v2_mode(),
					'queryFlag'             => 'cefa_tracking',
					'queryToken'            => 'cefa_tracking_token',
					'consumedKey'           => 'cefa_conversion_tracking_consumed_event_ids',
					'pendingKey'            => 'cefa_conversion_tracking_form4_pending',
					'microConsumedKey'      => 'cefa_conversion_tracking_micro_consumed',
					'formStartKey'          => 'cefa_conversion_tracking_form4_started',
					'clickDelayMs'          => 200,
					'attributionCookieDays' => 90,
					'trackedEvents'         => array(
						'parent_inquiry_cta_click',
						'find_a_school_click',
						'phone_click',
						'email_click',
						'form_start',
						'form_submit_click',
						'validation_error',
					),
				)
			)
		);
	}
}
