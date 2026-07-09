<?php
/**
 * Attribution capture and optional form writeback.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Backfills approved attribution fields from first-party cookies.
 */
final class CEFA_Conversion_Tracking_Attribution {
	/**
	 * Parent Form 4 attribution map.
	 */
	private const COOKIE_TO_FIELD = array(
		'cefa_last_utm_source'    => '35',
		'cefa_last_utm_medium'    => '36',
		'cefa_last_utm_campaign'  => '37',
		'cefa_last_utm_term'      => '38',
		'cefa_last_utm_content'   => '39',
		'cefa_last_gclid'         => '40',
		'cefa_last_gbraid'        => '41',
		'cefa_last_wbraid'        => '42',
		'cefa_last_fbclid'        => '43',
		'cefa_last_msclkid'       => '44',
		'cefa_first_landing_page' => '45',
		'cefa_first_referrer'     => '46',
	);

	/**
	 * Maximum field lengths by target field.
	 */
	private const FIELD_LENGTHS = array(
		'45' => 1000,
		'46' => 1000,
	);

	/**
	 * Fill missing attribution POST fields before Gravity Forms saves the entry.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function backfill_posted_fields( array $form_config = array() ): void {
		if ( isset( $form_config['attribution_backfill'] ) && ! $form_config['attribution_backfill'] ) {
			return;
		}

		$cookie_to_field = is_array( $form_config['cookie_to_field'] ?? null )
			? $form_config['cookie_to_field']
			: self::COOKIE_TO_FIELD;

		foreach ( $cookie_to_field as $cookie_name => $field_id ) {
			$post_key = 'input_' . $field_id;

			if ( ! self::should_write_post_field( $post_key ) ) {
				continue;
			}

			$value = self::read_cookie( $cookie_name, self::field_max_length( $field_id ) );

			if ( '' === $value ) {
				continue;
			}

			$_POST[ $post_key ] = $value; // phpcs:ignore WordPress.Security.NonceVerification.Missing
		}
	}

	/**
	 * Populate approved legacy/CRM attribution fields from the canonical envelope.
	 *
	 * This adapter is deliberately gated by both primary mode and the separate
	 * CRM identity flag. Shadow mode never writes these fields.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function apply_primary_compatibility_fields( array $form_config ): void {
		if ( 'primary' !== CEFA_Conversion_Tracking_Config::attribution_v2_mode() || ! CEFA_Conversion_Tracking_Config::crm_identity_enabled() ) {
			return;
		}

		$envelope = CEFA_Conversion_Tracking_Entry_Attribution::current_verified_envelope();

		if ( empty( $envelope ) ) {
			return;
		}

		$form_id = (int) ( $form_config['id'] ?? 0 );
		$values  = self::canonical_compatibility_values( $envelope, $form_config );
		$fields  = is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();

		foreach ( $fields as $semantic_key => $field_id ) {
			if ( ! array_key_exists( $semantic_key, $values ) ) {
				continue;
			}

			self::write_approved_post_field( $form_id, (string) $field_id, (string) $values[ $semantic_key ] );
		}
	}

	/**
	 * Convert canonical entry attribution to an existing form compatibility map.
	 *
	 * @param array<string, mixed> $envelope    Canonical envelope.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, string>
	 */
	public static function canonical_compatibility_values( array $envelope, array $form_config ): array {
		$first       = is_array( $envelope['first_touch'] ?? null ) ? $envelope['first_touch'] : array();
		$last        = is_array( $envelope['last_non_direct_touch'] ?? null ) ? $envelope['last_non_direct_touch'] : array();
		$click_ids   = is_array( $envelope['click_ids'] ?? null ) ? $envelope['click_ids'] : array();
		$browser_ids = is_array( $envelope['browser_ids'] ?? null ) ? $envelope['browser_ids'] : array();
		$fields      = is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();

		if ( isset( $fields['utm_source'] ) ) {
			return array(
				'utm_source'         => self::touch_value( $last, 'source' ),
				'utm_medium'         => self::touch_value( $last, 'medium' ),
				'utm_campaign'       => self::touch_value( $last, 'campaign' ),
				'utm_term'           => self::touch_value( $last, 'term' ),
				'utm_content'        => self::touch_value( $last, 'content' ),
				'gclid'              => self::map_value( $click_ids, 'gclid' ),
				'gbraid'             => self::map_value( $click_ids, 'gbraid' ),
				'wbraid'             => self::map_value( $click_ids, 'wbraid' ),
				'fbclid'             => self::map_value( $click_ids, 'fbclid' ),
				'msclkid'            => self::map_value( $click_ids, 'msclkid' ),
				'first_landing_page' => self::touch_url( $first, 'landing' ),
				'first_referrer'     => self::touch_url( $first, 'referrer' ),
			);
		}

		return array(
			'lc_source'    => self::touch_value( $last, 'source' ),
			'lc_medium'    => self::touch_value( $last, 'medium' ),
			'lc_campaign'  => self::touch_value( $last, 'campaign' ),
			'lc_content'   => self::touch_value( $last, 'content' ),
			'lc_term'      => self::touch_value( $last, 'term' ),
			'lc_channel'   => self::touch_value( $last, 'channel' ),
			'lc_landing'   => self::touch_url( $last, 'landing' ),
			'lc_referrer'  => self::touch_url( $last, 'referrer' ),
			'fc_source'    => self::touch_value( $first, 'source' ),
			'fc_medium'    => self::touch_value( $first, 'medium' ),
			'fc_campaign'  => self::touch_value( $first, 'campaign' ),
			'fc_content'   => self::touch_value( $first, 'content' ),
			'fc_term'      => self::touch_value( $first, 'term' ),
			'fc_channel'   => self::touch_value( $first, 'channel' ),
			'fc_referrer'  => self::touch_url( $first, 'referrer' ),
			'gclid'        => self::map_value( $click_ids, 'gclid' ),
			'ga_client_id' => self::map_value( $browser_ids, 'ga_client_id' ),
		);
	}

	/**
	 * Read one bounded canonical map value.
	 *
	 * @param array<string, mixed> $map Map.
	 * @param string               $key Key.
	 * @return string
	 */
	private static function map_value( array $map, string $key ): string {
		return substr( sanitize_text_field( (string) ( $map[ $key ] ?? '' ) ), 0, 220 );
	}

	/**
	 * Read one bounded touch value.
	 *
	 * @param array<string, mixed> $touch Touch.
	 * @param string               $key   Key.
	 * @return string
	 */
	private static function touch_value( array $touch, string $key ): string {
		return self::map_value( $touch, $key );
	}

	/**
	 * Rebuild a normalized host/path URL for legacy field compatibility.
	 *
	 * @param array<string, mixed> $touch  Touch.
	 * @param string               $prefix Landing or referrer.
	 * @return string
	 */
	private static function touch_url( array $touch, string $prefix ): string {
		$host = self::map_value( $touch, $prefix . '_host' );
		$path = self::map_value( $touch, $prefix . '_path' );

		return '' !== $host ? esc_url_raw( 'https://' . $host . ( '' !== $path ? $path : '/' ) ) : '';
	}

	/**
	 * Write only a configured attribution field and all common POST aliases.
	 *
	 * @param int    $form_id  Form ID.
	 * @param string $field_id Field ID.
	 * @param string $value    Canonical value, including an intentional blank.
	 * @return void
	 */
	private static function write_approved_post_field( int $form_id, string $field_id, string $value ): void {
		$max_length = in_array( $field_id, array( '20', '21', '28', '45', '46' ), true ) ? 1000 : 220;
		$value      = substr( sanitize_text_field( $value ), 0, $max_length );

		foreach ( array( 'input_' . $field_id, 'input_' . str_replace( '.', '_', $field_id ) ) as $post_key ) {
			$_POST[ $post_key ] = $value; // phpcs:ignore WordPress.Security.NonceVerification.Missing
		}

		$_POST[ 'cefa_ct_primary_form_' . $form_id ] = '1'; // phpcs:ignore WordPress.Security.NonceVerification.Missing
	}

	/**
	 * Determine whether a posted tracking field is missing or placeholder-like.
	 *
	 * @param string $post_key POST key.
	 * @return bool
	 */
	private static function should_write_post_field( string $post_key ): bool {
		if ( ! isset( $_POST[ $post_key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing
			return true;
		}

		$value = strtolower( trim( sanitize_text_field( wp_unslash( $_POST[ $post_key ] ) ) ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing

		if ( '' === $value ) {
			return true;
		}

		if ( in_array( $value, array( 'undefined', 'null', '(not set)', 'not set' ), true ) ) {
			return true;
		}

		return 1 === preg_match( '/^\{\{[^}]+\}\}$/', $value );
	}

	/**
	 * Read a first-party attribution cookie.
	 *
	 * @param string $cookie_name Cookie name.
	 * @param int    $max_length  Maximum value length.
	 * @return string
	 */
	private static function read_cookie( string $cookie_name, int $max_length ): string {
		if ( ! isset( $_COOKIE[ $cookie_name ] ) ) {
			return '';
		}

		$value = sanitize_text_field( wp_unslash( $_COOKIE[ $cookie_name ] ) );

		return substr( $value, 0, $max_length );
	}

	/**
	 * Return the allowed length for a target field.
	 *
	 * @param string $field_id Field ID.
	 * @return int
	 */
	private static function field_max_length( string $field_id ): int {
		return self::FIELD_LENGTHS[ $field_id ] ?? 220;
	}
}
