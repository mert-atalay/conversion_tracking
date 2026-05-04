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
 * Ensures supported forms have a submission-scoped event ID.
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
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function ensure_event_id_before_submission( array $form_config = array() ): void {
		$current = self::get_posted_event_id( $form_config );

		if ( '' !== $current ) {
			self::write_event_id_to_post( $current, $form_config );
			return;
		}

		self::write_event_id_to_post( wp_generate_uuid4(), $form_config );
	}

	/**
	 * Read and normalize an event ID from POST data.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return string
	 */
	public static function get_posted_event_id( array $form_config = array() ): string {
		foreach ( self::event_id_post_keys( $form_config ) as $key ) {
			if ( isset( $_POST[ $key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing
				$value = sanitize_text_field( wp_unslash( $_POST[ $key ] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing
				$value = self::normalize_event_id( $value );

				if ( '' !== $value && ! self::event_id_conflicts_with_posted_values( $value, $form_config ) ) {
					return $value;
				}
			}
		}

		return '';
	}

	/**
	 * Ensure a saved entry has an event ID, either in a field or entry meta.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	public static function ensure_entry_event_id( array $entry, array $form_config = array() ): array {
		$event_id = self::get_entry_event_id( $entry, $form_config );

		if ( '' === $event_id ) {
			$event_id = self::get_posted_event_id( $form_config );
		}

		if ( '' === $event_id ) {
			$event_id = wp_generate_uuid4();
		}

		self::persist_entry_event_id( $entry, $form_config, $event_id );

		$entry[ self::event_id_entry_key( $form_config ) ] = $event_id;

		foreach ( self::event_id_entry_fields( $form_config ) as $field_id ) {
			$entry[ $field_id ] = $event_id;
		}

		return $entry;
	}

	/**
	 * Read an event ID from entry fields or entry meta.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return string
	 */
	public static function get_entry_event_id( array $entry, array $form_config = array() ): string {
		foreach ( self::event_id_entry_fields( $form_config ) as $field_id ) {
			$event_id = self::normalize_event_id( (string) rgar( $entry, $field_id ) );

			if ( '' !== $event_id && ! self::event_id_conflicts_with_entry_values( $event_id, $entry, $form_config ) ) {
				return $event_id;
			}
		}

		$entry_key = self::event_id_entry_key( $form_config );
		$event_id  = self::normalize_event_id( (string) rgar( $entry, $entry_key ) );

		if ( '' !== $event_id && ! self::event_id_conflicts_with_entry_values( $event_id, $entry, $form_config ) ) {
			return $event_id;
		}

		if ( ! function_exists( 'gform_get_meta' ) || empty( $entry['id'] ) ) {
			return '';
		}

		$event_id = self::normalize_event_id( (string) gform_get_meta( (int) $entry['id'], $entry_key ) );

		if ( '' !== $event_id && ! self::event_id_conflicts_with_entry_values( $event_id, $entry, $form_config ) ) {
			return $event_id;
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
	 * @param string               $event_id    Event ID.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	private static function write_event_id_to_post( string $event_id, array $form_config = array() ): void {
		foreach ( self::event_id_post_keys( $form_config ) as $key ) {
			$_POST[ $key ] = $event_id; // phpcs:ignore WordPress.Security.NonceVerification.Missing
		}
	}

	/**
	 * Event ID POST keys for a form.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return string[]
	 */
	private static function event_id_post_keys( array $form_config = array() ): array {
		$form_id = (int) ( $form_config['id'] ?? CEFA_CONVERSION_TRACKING_FORM_ID );
		$keys    = is_array( $form_config['event_id_post_keys'] ?? null )
			? $form_config['event_id_post_keys']
			: self::EVENT_ID_POST_KEYS;

		$keys[] = 'cefa_ct_event_id';
		$keys[] = 'cefa_ct_event_id_' . $form_id;

		return array_values( array_unique( array_filter( array_map( 'strval', $keys ) ) ) );
	}

	/**
	 * Event ID entry fields for a form.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return string[]
	 */
	private static function event_id_entry_fields( array $form_config = array() ): array {
		$fields = is_array( $form_config['event_id_fields'] ?? null )
			? $form_config['event_id_fields']
			: array( '32.4' );

		return array_values( array_unique( array_filter( array_map( 'strval', $fields ) ) ) );
	}

	/**
	 * Entry meta/local key for event ID storage.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return string
	 */
	private static function event_id_entry_key( array $form_config = array() ): string {
		return isset( $form_config['event_id_meta_key'] )
			? sanitize_key( (string) $form_config['event_id_meta_key'] )
			: CEFA_Conversion_Tracking_Config::EVENT_ID_META_KEY;
	}

	/**
	 * Check whether an event ID candidate is actually one of the form metadata values.
	 *
	 * @param string               $event_id    Event ID candidate.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return bool
	 */
	private static function event_id_conflicts_with_posted_values( string $event_id, array $form_config = array() ): bool {
		foreach ( self::metadata_field_ids( $form_config ) as $field_id ) {
			foreach ( self::field_post_keys( $field_id ) as $key ) {
				if ( ! isset( $_POST[ $key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing
					continue;
				}

				$value = sanitize_text_field( wp_unslash( $_POST[ $key ] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing

				if ( self::same_token( $event_id, $value ) ) {
					return true;
				}
			}
		}

		return false;
	}

	/**
	 * Check whether an entry event ID candidate is actually one of the entry metadata values.
	 *
	 * @param string               $event_id    Event ID candidate.
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return bool
	 */
	private static function event_id_conflicts_with_entry_values( string $event_id, array $entry, array $form_config = array() ): bool {
		foreach ( self::metadata_field_ids( $form_config ) as $field_id ) {
			if ( in_array( $field_id, self::event_id_entry_fields( $form_config ), true ) ) {
				continue;
			}

			if ( self::same_token( $event_id, (string) rgar( $entry, $field_id ) ) ) {
				return true;
			}
		}

		return false;
	}

	/**
	 * Metadata field IDs whose values must never be reused as event IDs.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return string[]
	 */
	private static function metadata_field_ids( array $form_config = array() ): array {
		$field_map = is_array( $form_config['field_map'] ?? null ) ? $form_config['field_map'] : array();

		return array_values( array_unique( array_filter( array_map( 'strval', $field_map ) ) ) );
	}

	/**
	 * POST key variants for a Gravity Forms field ID.
	 *
	 * @param string $field_id Gravity Forms field ID.
	 * @return string[]
	 */
	private static function field_post_keys( string $field_id ): array {
		return array_values(
			array_unique(
				array(
					'input_' . $field_id,
					'input_' . str_replace( '.', '_', $field_id ),
				)
			)
		);
	}

	/**
	 * Compare normalized scalar tracking tokens.
	 *
	 * @param string $left  First token.
	 * @param string $right Second token.
	 * @return bool
	 */
	private static function same_token( string $left, string $right ): bool {
		$left  = trim( $left );
		$right = trim( $right );

		return '' !== $left && '' !== $right && $left === $right;
	}

	/**
	 * Persist event ID to configured fields and/or entry meta.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @param string               $event_id    Event ID.
	 * @return void
	 */
	private static function persist_entry_event_id( array $entry, array $form_config, string $event_id ): void {
		if ( empty( $entry['id'] ) ) {
			return;
		}

		foreach ( self::event_id_entry_fields( $form_config ) as $field_id ) {
			if ( class_exists( 'GFAPI' ) ) {
				GFAPI::update_entry_field( (int) $entry['id'], $field_id, $event_id );
			}
		}

		if ( function_exists( 'gform_update_meta' ) ) {
			gform_update_meta(
				(int) $entry['id'],
				self::event_id_entry_key( $form_config ),
				$event_id,
				(int) ( $form_config['id'] ?? 0 )
			);
		}
	}
}
