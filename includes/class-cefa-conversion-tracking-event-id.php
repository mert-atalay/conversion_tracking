<?php
/**
 * Event ID handling.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Ensures Form 4 has a submission-scoped event ID.
 */
final class CEFA_Conversion_Tracking_Event_ID {
	/**
	 * Field 32.4 POST keys observed across Gravity Forms compound inputs.
	 */
	private const EVENT_ID_POST_KEYS = array(
		'input_32_4',
		'input_32.4',
	);

	/**
	 * Ensure event ID exists before Gravity Forms saves the entry.
	 *
	 * @return void
	 */
	public static function ensure_event_id_before_submission(): void {
		$current = self::get_posted_event_id();

		if ( '' !== $current ) {
			self::write_event_id_to_post( $current );
			return;
		}

		self::write_event_id_to_post( wp_generate_uuid4() );
	}

	/**
	 * Read and normalize an event ID from POST data.
	 *
	 * @return string
	 */
	public static function get_posted_event_id(): string {
		foreach ( self::EVENT_ID_POST_KEYS as $key ) {
			if ( isset( $_POST[ $key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing
				$value = sanitize_text_field( wp_unslash( $_POST[ $key ] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing
				$value = self::normalize_event_id( $value );

				if ( '' !== $value ) {
					return $value;
				}
			}
		}

		return '';
	}

	/**
	 * Normalize a browser/server event ID.
	 *
	 * @param string $event_id Event ID candidate.
	 * @return string
	 */
	public static function normalize_event_id( string $event_id ): string {
		$event_id = trim( $event_id );

		if ( '' === $event_id ) {
			return '';
		}

		if ( strlen( $event_id ) > 128 ) {
			return '';
		}

		if ( ! preg_match( '/^[A-Za-z0-9._:-]+$/', $event_id ) ) {
			return '';
		}

		return $event_id;
	}

	/**
	 * Write event ID to every likely POST key so Gravity Forms can persist it.
	 *
	 * @param string $event_id Event ID.
	 * @return void
	 */
	private static function write_event_id_to_post( string $event_id ): void {
		foreach ( self::EVENT_ID_POST_KEYS as $key ) {
			$_POST[ $key ] = $event_id; // phpcs:ignore WordPress.Security.NonceVerification.Missing
		}
	}
}
