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
		'cefa_last_utm_source'      => '35',
		'cefa_last_utm_medium'      => '36',
		'cefa_last_utm_campaign'    => '37',
		'cefa_last_utm_term'        => '38',
		'cefa_last_utm_content'     => '39',
		'cefa_last_gclid'           => '40',
		'cefa_last_gbraid'          => '41',
		'cefa_last_wbraid'          => '42',
		'cefa_last_fbclid'          => '43',
		'cefa_last_msclkid'         => '44',
		'cefa_first_landing_page'   => '45',
		'cefa_first_referrer'       => '46',
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
