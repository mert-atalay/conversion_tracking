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
	 * Attribution fields in the redesign Form 4.
	 */
	private const ATTRIBUTION_FIELDS = array(
		'utm_source'         => '35',
		'utm_medium'         => '36',
		'utm_campaign'       => '37',
		'utm_term'           => '38',
		'utm_content'        => '39',
		'gclid'              => '40',
		'gbraid'             => '41',
		'wbraid'             => '42',
		'fbclid'             => '43',
		'msclkid'            => '44',
		'first_landing_page' => '45',
		'first_referrer'     => '46',
	);

	/**
	 * Build the canonical Phase 1A payload.
	 *
	 * @param array $entry Gravity Forms entry.
	 * @return array<string, mixed>
	 */
	public static function from_entry( array $entry ): array {
		$event_id = CEFA_Conversion_Tracking_Event_ID::normalize_event_id( (string) rgar( $entry, '32.4' ) );

		if ( '' === $event_id ) {
			$event_id = wp_generate_uuid4();
		}

		$payload = array(
			'event'                => 'school_inquiry_submit',
			'event_id'             => $event_id,
			'form_id'              => '4',
			'form_family'          => 'parent_inquiry',
			'lead_type'            => 'cefa_lead',
			'lead_intent'          => 'inquire_now',
			'school_selected_id'   => sanitize_text_field( (string) rgar( $entry, '32.1' ) ),
			'school_selected_slug' => sanitize_text_field( (string) rgar( $entry, '32.5' ) ),
			'school_selected_name' => sanitize_text_field( (string) rgar( $entry, '32.6' ) ),
			'program_id'           => sanitize_text_field( (string) rgar( $entry, '32.2' ) ),
			'program_name'         => sanitize_text_field( (string) rgar( $entry, '32.7' ) ),
			'days_per_week'        => sanitize_text_field( (string) rgar( $entry, '32.3' ) ),
			'inquiry_success'      => true,
			'inquiry_success_url'  => '',
			'page_context'         => 'parent',
			'tracking_source'      => 'helper_plugin',
		);

		foreach ( self::ATTRIBUTION_FIELDS as $key => $field_id ) {
			$payload[ $key ] = self::entry_value( $entry, $field_id );
		}

		return $payload;
	}

	/**
	 * Read a sanitized Gravity Forms entry value.
	 *
	 * @param array  $entry    Gravity Forms entry.
	 * @param string $field_id Field ID.
	 * @return string
	 */
	private static function entry_value( array $entry, string $field_id ): string {
		$max_length = in_array( $field_id, array( '45', '46' ), true ) ? 1000 : 220;

		return substr( sanitize_text_field( (string) rgar( $entry, $field_id ) ), 0, $max_length );
	}
}
