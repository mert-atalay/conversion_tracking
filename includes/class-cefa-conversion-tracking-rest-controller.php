<?php
/**
 * REST route for one-time tracking payload consumption.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * REST controller.
 */
final class CEFA_Conversion_Tracking_REST_Controller {
	/**
	 * Register REST routes.
	 *
	 * @return void
	 */
	public static function register_routes(): void {
		register_rest_route(
			'cefa-conversion-tracking/v1',
			'/tracking-payload/(?P<token>[A-Za-z0-9_.-]{8,512})',
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => array( __CLASS__, 'get_tracking_payload' ),
				'permission_callback' => '__return_true',
				'args'                => array(
					'token' => array(
						'required'          => true,
						'sanitize_callback' => 'sanitize_text_field',
					),
				),
			)
		);

		register_rest_route(
			'cefa-conversion-tracking/v1',
			'/tracking-payload-by-event/(?P<event_id>[A-Za-z0-9_-]{8,128})',
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => array( __CLASS__, 'get_tracking_payload_by_event_id' ),
				'permission_callback' => '__return_true',
				'args'                => array(
					'event_id' => array(
						'required'          => true,
						'sanitize_callback' => 'sanitize_text_field',
					),
				),
			)
		);

		register_rest_route(
			'cefa-conversion-tracking/v1',
			'/attribution-capture',
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => array( __CLASS__, 'capture_attribution' ),
				'permission_callback' => array( __CLASS__, 'allow_same_origin_attribution' ),
			)
		);
	}

	/**
	 * Restrict anonymous attribution writes to the CEFA browser bridge.
	 *
	 * The custom header forces a CORS preflight for cross-origin callers while
	 * the origin check keeps this endpoint scoped to the current CEFA host.
	 *
	 * @param WP_REST_Request $request REST request.
	 * @return bool
	 */
	public static function allow_same_origin_attribution( WP_REST_Request $request ): bool {
		if ( '1' !== (string) $request->get_header( 'x-cefa-attribution' ) ) {
			return false;
		}

		$origin      = (string) $request->get_header( 'origin' );
		$origin_host = strtolower( (string) wp_parse_url( $origin, PHP_URL_HOST ) );
		$site_host   = strtolower( (string) wp_parse_url( home_url( '/' ), PHP_URL_HOST ) );

		return '' !== $origin_host && '' !== $site_host && $origin_host === $site_host;
	}

	/**
	 * Capture attribution through an uncached request for managed hosts.
	 *
	 * @param WP_REST_Request $request REST request.
	 * @return WP_REST_Response
	 */
	public static function capture_attribution( WP_REST_Request $request ): WP_REST_Response {
		$params       = $request->get_param( 'params' );
		$landing_path = (string) $request->get_param( 'landing_path' );
		$referrer     = (string) $request->get_param( 'referrer' );
		$site_host    = strtolower( (string) wp_parse_url( home_url( '/' ), PHP_URL_HOST ) );
		$path         = (string) wp_parse_url( $landing_path, PHP_URL_PATH );
		$server       = array(
			'HTTP_HOST'    => $site_host,
			'REQUEST_URI'  => '/' . ltrim( substr( $path, 0, 500 ), '/' ),
			'HTTP_REFERER' => esc_url_raw( substr( $referrer, 0, 1000 ) ),
		);
		$prepared     = CEFA_Conversion_Tracking_Attribution_Envelope::prepare_cookie(
			is_array( $params ) ? $params : array(),
			$server,
			$_COOKIE
		);
		$stored       = CEFA_Conversion_Tracking_Attribution_Envelope::persist_prepared_cookie( $prepared );
		$envelope     = array();

		if ( ! empty( $prepared['value'] ) ) {
			$envelope = CEFA_Conversion_Tracking_Attribution_Envelope::decode(
				(string) $prepared['value'],
				CEFA_Conversion_Tracking_Config::attribution_v2_secret(),
				CEFA_Conversion_Tracking_Config::site_context()
			);
		}

		if ( empty( $envelope ) ) {
			$envelope = CEFA_Conversion_Tracking_Entry_Attribution::current_verified_envelope();
		}

		$ledger_result = ! empty( $envelope )
			? CEFA_Conversion_Tracking_Attribution_Ledger::capture( $envelope, $_COOKIE )
			: array();
		$response_data = array(
			'status' => ( $stored || ! empty( $ledger_result['cookie_set'] ) ) ? 'stored' : 'unchanged',
		);

		if ( ! empty( $ledger_result['capture_token'] ) ) {
			$response_data['capture_token'] = (string) $ledger_result['capture_token'];
		}

		$response = new WP_REST_Response(
			$response_data,
			200
		);

		$response->header( 'Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0' );

		return $response;
	}

	/**
	 * Consume and return a tracking payload.
	 *
	 * @param WP_REST_Request $request REST request.
	 * @return WP_REST_Response|WP_Error
	 */
	public static function get_tracking_payload( WP_REST_Request $request ) {
		$token   = (string) $request->get_param( 'token' );
		$payload = CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload( $token );

		if ( null === $payload ) {
			return new WP_Error(
				'cefa_conversion_tracking_payload_not_found',
				__( 'Tracking payload is unavailable or expired.', 'cefa-conversion-tracking' ),
				array( 'status' => 404 )
			);
		}

		$response = new WP_REST_Response( $payload, 200 );
		$response->header( 'Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0' );

		return $response;
	}

	/**
	 * Consume and return a tracking payload by event ID.
	 *
	 * @param WP_REST_Request $request REST request.
	 * @return WP_REST_Response|WP_Error
	 */
	public static function get_tracking_payload_by_event_id( WP_REST_Request $request ) {
		$event_id = (string) $request->get_param( 'event_id' );
		$payload  = CEFA_Conversion_Tracking_Duplicate_Guard::consume_payload_by_event_id( $event_id );

		if ( null === $payload ) {
			return new WP_Error(
				'cefa_conversion_tracking_payload_not_found',
				__( 'Tracking payload is unavailable or expired.', 'cefa-conversion-tracking' ),
				array( 'status' => 404 )
			);
		}

		$response = new WP_REST_Response( $payload, 200 );
		$response->header( 'Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0' );

		return $response;
	}
}
