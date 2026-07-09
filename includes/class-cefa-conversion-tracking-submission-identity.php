<?php
/**
 * Dual legacy/server submission identity handling.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Preserves legacy IDs in shadow and promotes reserved IDs only in primary.
 */
final class CEFA_Conversion_Tracking_Submission_Identity {
	public const SERVER_EVENT_ID_META_KEY = 'cefa_conversion_tracking_server_event_id';
	public const ATTEMPT_ID_META_KEY      = 'cefa_conversion_tracking_submission_attempt_id';
	public const IDENTITY_STATUS_META_KEY = 'cefa_conversion_tracking_identity_status';

	/**
	 * Request-local browser attempt IDs keyed by form ID.
	 *
	 * @var array<int, string>
	 */
	private static $attempt_ids = array();

	/**
	 * Request-local pre-reserved server IDs keyed by form ID.
	 *
	 * @var array<int, string>
	 */
	private static $server_ids = array();

	/**
	 * Preserve the browser attempt ID and reserve primary identity when enabled.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function prepare_before_submission( array $form_config ): void {
		$mode    = CEFA_Conversion_Tracking_Config::attribution_v2_mode();
		$form_id = (int) ( $form_config['id'] ?? 0 );

		if ( 'off' === $mode || $form_id < 1 ) {
			return;
		}

		$attempt_id = CEFA_Conversion_Tracking_Event_ID::get_posted_event_id( $form_config );

		if ( '' !== $attempt_id ) {
			self::$attempt_ids[ $form_id ] = $attempt_id;
		}

		if ( 'primary' !== $mode ) {
			return;
		}

		$server_id = CEFA_Conversion_Tracking_Event_ID_Registry::generate_and_reserve(
			CEFA_Conversion_Tracking_Config::site_context(),
			$form_id
		);

		if ( '' === $server_id ) {
			return;
		}

		self::$server_ids[ $form_id ] = $server_id;
		CEFA_Conversion_Tracking_Event_ID::replace_posted_event_id( $server_id, $form_config );
	}

	/**
	 * Finalize immutable identity after Gravity Forms saves an entry.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	public static function finalize_after_submission( array $entry, array $form_config ): array {
		$mode     = CEFA_Conversion_Tracking_Config::attribution_v2_mode();
		$form_id  = (int) ( $form_config['id'] ?? rgar( $entry, 'form_id' ) );
		$entry_id = (int) rgar( $entry, 'id' );

		if ( 'off' === $mode || $form_id < 1 || $entry_id < 1 || 'spam' === (string) rgar( $entry, 'status' ) ) {
			return $entry;
		}

		$existing = self::entry_meta( $entry, self::SERVER_EVENT_ID_META_KEY );

		if ( '' !== $existing ) {
			$entry[ self::SERVER_EVENT_ID_META_KEY ] = $existing;
			return $entry;
		}

		$attempt_id = self::$attempt_ids[ $form_id ] ?? CEFA_Conversion_Tracking_Event_ID::get_posted_event_id( $form_config );
		$server_id  = '';

		if ( 'primary' === $mode ) {
			$server_id = self::$server_ids[ $form_id ] ?? CEFA_Conversion_Tracking_Event_ID::get_entry_event_id( $entry, $form_config );

			if ( '' !== $server_id && ! CEFA_Conversion_Tracking_Event_ID_Registry::attach_entry( $server_id, $entry_id ) ) {
				$server_id = CEFA_Conversion_Tracking_Event_ID_Registry::reserve(
					$server_id,
					CEFA_Conversion_Tracking_Config::site_context(),
					$form_id,
					$entry_id
				) ? $server_id : '';
			}
		} else {
			$server_id = CEFA_Conversion_Tracking_Event_ID_Registry::generate_and_reserve(
				CEFA_Conversion_Tracking_Config::site_context(),
				$form_id,
				$entry_id
			);
		}

		if ( '' === $server_id ) {
			self::save_meta( $entry_id, $form_id, self::IDENTITY_STATUS_META_KEY, 'reservation_failed_' . $mode );
			return $entry;
		}

		$values = array(
			self::SERVER_EVENT_ID_META_KEY => $server_id,
			self::ATTEMPT_ID_META_KEY      => $attempt_id,
			self::IDENTITY_STATUS_META_KEY => 'reserved_' . $mode,
		);

		foreach ( $values as $key => $value ) {
			if ( '' !== $value ) {
				self::save_meta( $entry_id, $form_id, $key, $value );
				$entry[ $key ] = $value;
			}
		}

		return $entry;
	}

	/**
	 * Read entry-local or persisted metadata.
	 *
	 * @param array<string, mixed> $entry Entry.
	 * @param string               $key   Meta key.
	 * @return string
	 */
	private static function entry_meta( array $entry, string $key ): string {
		$value = sanitize_text_field( (string) rgar( $entry, $key ) );

		if ( '' === $value && function_exists( 'gform_get_meta' ) && ! empty( $entry['id'] ) ) {
			$value = sanitize_text_field( (string) gform_get_meta( (int) $entry['id'], $key ) );
		}

		return $value;
	}

	/**
	 * Persist identity metadata.
	 *
	 * @param int    $entry_id Entry ID.
	 * @param int    $form_id  Form ID.
	 * @param string $key      Meta key.
	 * @param string $value    Meta value.
	 * @return void
	 */
	private static function save_meta( int $entry_id, int $form_id, string $key, string $value ): void {
		if ( function_exists( 'gform_update_meta' ) ) {
			gform_update_meta( $entry_id, $key, $value, $form_id );
		}
	}
}
