<?php
/**
 * Main plugin bootstrap.
 *
 * @package CEFA_Phase1A_Tracking_Bridge
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Coordinates Phase 1A tracking hooks.
 */
final class CEFA_Phase1A_Tracking_Bridge {
	/**
	 * REST namespace.
	 */
	private const REST_NAMESPACE = 'cefa-phase1a/v1';

	/**
	 * Initialize hooks.
	 *
	 * @return void
	 */
	public static function init(): void {
		add_action( 'wp_enqueue_scripts', array( __CLASS__, 'enqueue_scripts' ) );
		add_filter( 'gform_pre_submission_4', array( 'CEFA_Phase1A_Tracking_Bridge_Event_ID', 'ensure_event_id_before_submission' ) );
		add_filter( 'gform_confirmation_4', array( 'CEFA_Phase1A_Tracking_Bridge_Confirmation_Payload', 'prepare_confirmation_tracking' ), 10, 4 );
		add_action( 'rest_api_init', array( 'CEFA_Phase1A_Tracking_Bridge_REST_Controller', 'register_routes' ) );
	}

	/**
	 * Enqueue the lightweight browser bridge.
	 *
	 * The script runs on public pages only and self-activates when Form 4 or
	 * a plugin tracking token is present.
	 *
	 * @return void
	 */
	public static function enqueue_scripts(): void {
		$handle = 'cefa-phase1a-tracking-bridge';
		$src    = CEFA_PHASE1A_TRACKING_BRIDGE_URL . 'assets/js/cefa-phase1a-tracking-bridge.js';
		$path   = CEFA_PHASE1A_TRACKING_BRIDGE_DIR . 'assets/js/cefa-phase1a-tracking-bridge.js';
		$ver    = file_exists( $path ) ? (string) filemtime( $path ) : CEFA_PHASE1A_TRACKING_BRIDGE_VERSION;

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
			'CEFAPhase1ATrackingBridge',
			array(
				'formId'              => CEFA_PHASE1A_TRACKING_BRIDGE_FORM_ID,
				'eventFieldSelectors' => array(
					'[name="input_32_4"]',
					'[name="input_32.4"]',
					'#input_4_32_4',
					'input[data-cefa-si-meta="4"]',
				),
				'restPayloadBase'     => esc_url_raw( rest_url( self::REST_NAMESPACE . '/tracking-payload/' ) ),
				'queryFlag'           => 'cefa_tracking',
				'queryToken'          => 'cefa_tracking_token',
				'consumedKey'         => 'cefa_phase1a_consumed_event_ids',
				'pendingKey'          => 'cefa_phase1a_form4_pending',
			)
		);
	}
}
