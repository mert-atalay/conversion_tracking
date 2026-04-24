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
			'/tracking-payload/(?P<token>[A-Za-z0-9_-]{8,128})',
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
				__( 'Tracking payload is unavailable or already consumed.', 'cefa-conversion-tracking' ),
				array( 'status' => 404 )
			);
		}

		$response = new WP_REST_Response( $payload, 200 );
		$response->header( 'Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0' );

		return $response;
	}
}
