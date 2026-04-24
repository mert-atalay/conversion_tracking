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

		if ( is_string( $confirmation ) ) {
			$confirmation .= self::inline_datalayer_script( $payload );
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
	 * Create inline script for non-redirect confirmations.
	 *
	 * @param array<string, mixed> $payload Tracking payload.
	 * @return string
	 */
	private static function inline_datalayer_script( array $payload ): string {
		$json = wp_json_encode( $payload );

		if ( false === $json ) {
			return '';
		}

		return wp_get_inline_script_tag( 'window.dataLayer=window.dataLayer||[];window.dataLayer.push(' . $json . ');' );
	}
}
