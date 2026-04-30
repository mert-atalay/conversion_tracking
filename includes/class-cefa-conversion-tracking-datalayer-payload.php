<?php
/**
 * DataLayer payload builder.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Builds clean tracking payloads from saved Gravity Forms entries.
 */
final class CEFA_Conversion_Tracking_DataLayer_Payload {
	/**
	 * Build the canonical payload.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	public static function from_entry( array $entry, array $form_config = array() ): array {
		$form_config = self::form_config_from_entry( $entry, $form_config );
		$event_id    = CEFA_Conversion_Tracking_Event_ID::get_entry_event_id( $entry, $form_config );

		if ( '' === $event_id ) {
			$event_id = wp_generate_uuid4();
		}

		$payload = array_merge(
			array(
				'event'               => (string) ( $form_config['event_name'] ?? 'school_inquiry_submit' ),
				'event_id'            => $event_id,
				'form_id'             => (string) ( $form_config['id'] ?? rgar( $entry, 'form_id' ) ),
				'inquiry_success'     => true,
				'event_source_url'    => esc_url_raw( (string) rgar( $entry, 'source_url' ) ),
				'inquiry_success_url' => '',
				'tracking_source'     => 'helper_plugin',
			),
			is_array( $form_config['static_payload'] ?? null ) ? $form_config['static_payload'] : array()
		);

		foreach ( self::field_map( $form_config ) as $key => $field_id ) {
			$payload[ $key ] = self::entry_value( $entry, $field_id );
		}

		foreach ( self::attribution_fields( $form_config ) as $key => $field_id ) {
			$payload[ $key ] = self::entry_value( $entry, $field_id );
		}

		return $payload;
	}

	/**
	 * Resolve form config from entry if one was not passed.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	private static function form_config_from_entry( array $entry, array $form_config ): array {
		if ( ! empty( $form_config ) ) {
			return $form_config;
		}

		return CEFA_Conversion_Tracking_Config::form_config( (int) rgar( $entry, 'form_id' ) );
	}

	/**
	 * Non-PII field map for the active form.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, string>
	 */
	private static function field_map( array $form_config ): array {
		return is_array( $form_config['field_map'] ?? null ) ? $form_config['field_map'] : array();
	}

	/**
	 * Attribution field map for the active form.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, string>
	 */
	private static function attribution_fields( array $form_config ): array {
		return is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();
	}

	/**
	 * Read a sanitized Gravity Forms entry value.
	 *
	 * @param array  $entry    Gravity Forms entry.
	 * @param string $field_id Field ID.
	 * @return string
	 */
	private static function entry_value( array $entry, string $field_id ): string {
		$max_length = in_array( $field_id, array( '20', '21', '28', '45', '46' ), true ) ? 1000 : 220;

		return substr( sanitize_text_field( (string) rgar( $entry, $field_id ) ), 0, $max_length );
	}
}
