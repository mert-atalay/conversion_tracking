<?php
/**
 * Gravity Forms confirmation integration.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Creates server-confirmed tracking payloads after successful submission.
 */
final class CEFA_Conversion_Tracking_Confirmation_Payload {
	/**
	 * Store a server-confirmed payload as soon as Gravity Forms saves the entry.
	 *
	 * @param array $entry Gravity Forms entry.
	 * @param array $form  Gravity Forms form.
	 * @return void
	 */
	public static function store_after_submission_payload( array $entry, array $form ): void {
		if ( CEFA_CONVERSION_TRACKING_FORM_ID !== (int) rgar( $form, 'id' ) ) {
			return;
		}

		if ( 'spam' === (string) rgar( $entry, 'status' ) ) {
			return;
		}

		$entry   = self::ensure_entry_event_id( $entry );
		$payload = CEFA_Conversion_Tracking_DataLayer_Payload::from_entry( $entry );

		CEFA_Conversion_Tracking_Duplicate_Guard::store_payload( $payload );
	}

	/**
	 * Prepare tokenized tracking payload for redirect or inline confirmations.
	 *
	 * @param string|array $confirmation Confirmation config.
	 * @param array        $form         Gravity Forms form.
	 * @param array        $entry        Gravity Forms entry.
	 * @param bool         $is_ajax      Whether AJAX submission is active.
	 * @return string|array
	 */
	public static function prepare_confirmation_tracking( $confirmation, array $form, array $entry, bool $is_ajax ) {
		unset( $is_ajax );

		if ( CEFA_CONVERSION_TRACKING_FORM_ID !== (int) rgar( $form, 'id' ) ) {
			return $confirmation;
		}

		if ( 'spam' === (string) rgar( $entry, 'status' ) ) {
			return $confirmation;
		}

		$entry   = self::ensure_entry_event_id( $entry );
		$payload = CEFA_Conversion_Tracking_DataLayer_Payload::from_entry( $entry );
		$token   = CEFA_Conversion_Tracking_Duplicate_Guard::store_payload( $payload );

		if ( is_array( $confirmation ) && ! empty( $confirmation['redirect'] ) ) {
			$confirmation['redirect'] = add_query_arg(
				array(
					'cefa_tracking'       => '1',
					'cefa_tracking_token' => rawurlencode( $token ),
				),
				(string) $confirmation['redirect']
			);

			return $confirmation;
		}

		if ( is_array( $confirmation ) && 'page' === (string) rgar( $confirmation, 'type' ) ) {
			$confirmation['queryString'] = self::append_tracking_query_string(
				(string) rgar( $confirmation, 'queryString' ),
				$token
			);

			return $confirmation;
		}

		return $confirmation;
	}

	/**
	 * Ensure the saved entry has the same event ID used by the payload.
	 *
	 * @param array $entry Gravity Forms entry.
	 * @return array
	 */
	private static function ensure_entry_event_id( array $entry ): array {
		$event_id = CEFA_Conversion_Tracking_Event_ID::normalize_event_id( (string) rgar( $entry, '32.4' ) );

		if ( '' !== $event_id ) {
			$entry['32.4'] = $event_id;
			return $entry;
		}

		$event_id      = wp_generate_uuid4();
		$entry['32.4'] = $event_id;

		if ( class_exists( 'GFAPI' ) && ! empty( $entry['id'] ) ) {
			GFAPI::update_entry_field( (int) $entry['id'], '32.4', $event_id );
		}

		return $entry;
	}

	/**
	 * Append the one-time token to Gravity Forms page confirmation query args.
	 *
	 * Gravity Forms page confirmations use a raw query-string value instead of
	 * the redirect URL shape, so we preserve existing parameters and add ours.
	 *
	 * @param string $query_string Existing confirmation query string.
	 * @param string $token        One-time payload token.
	 * @return string
	 */
	private static function append_tracking_query_string( string $query_string, string $token ): string {
		$query_string = ltrim( trim( $query_string ), '?' );
		$params       = array();

		if ( '' !== $query_string ) {
			wp_parse_str( $query_string, $params );
		}

		$params['cefa_tracking']       = '1';
		$params['cefa_tracking_token'] = $token;

		return build_query( $params );
	}

}
