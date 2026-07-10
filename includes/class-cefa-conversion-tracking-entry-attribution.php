<?php
/**
 * Canonical Gravity Forms entry attribution persistence.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Saves verified attribution beside legacy hidden fields during shadow mode.
 */
final class CEFA_Conversion_Tracking_Entry_Attribution {
	public const ATTRIBUTION_META_KEY = 'cefa_conversion_tracking_attribution_v1';
	public const SCHEMA_META_KEY      = 'cefa_conversion_tracking_schema_version';
	public const STATUS_META_KEY      = 'cefa_conversion_tracking_delivery_status';
	public const PROVENANCE_META_KEY  = 'cefa_conversion_tracking_attribution_provenance';

	/**
	 * Persist the verified request envelope after Gravity Forms saves an entry.
	 *
	 * Shadow mode writes entry meta only. It never overwrites Gravity Forms
	 * fields, GAConnector values, School Manager data, or CRM feed inputs.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	public static function persist_after_submission( array $entry, array $form_config ): array {
		$mode = CEFA_Conversion_Tracking_Config::attribution_v2_mode();

		if ( 'off' === $mode || empty( $entry['id'] ) || 'spam' === (string) rgar( $entry, 'status' ) ) {
			return $entry;
		}

		$ledger   = CEFA_Conversion_Tracking_Attribution_Ledger::resolve( $_COOKIE, $_POST ); // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Signed ledger token is verified before use.
		$envelope = self::current_verified_envelope();

		if ( empty( $envelope ) ) {
			return $entry;
		}

		$envelope = CEFA_Conversion_Tracking_Attribution_Envelope::with_browser_ids( $envelope, $_COOKIE );

		$encoded = wp_json_encode( $envelope, JSON_UNESCAPED_SLASHES );

		if ( ! is_string( $encoded ) || '' === $encoded ) {
			return $entry;
		}

		$form_id    = (int) ( $form_config['id'] ?? rgar( $entry, 'form_id' ) );
		$entry_id   = (int) $entry['id'];
		$provenance = wp_json_encode(
			array(
				'attribution'   => 'signed_envelope',
				'ledger'        => ! empty( $ledger ) ? sanitize_key( (string) ( $ledger['source'] ?? '' ) ) : 'not_resolved',
				'legacy_fields' => 'preserved',
				'mode'          => $mode,
			),
			JSON_UNESCAPED_SLASHES
		);
		$values     = array(
			self::ATTRIBUTION_META_KEY => $encoded,
			self::SCHEMA_META_KEY      => (string) ( $envelope['schema_version'] ?? '' ),
			self::STATUS_META_KEY      => 'attribution_' . $mode,
			self::PROVENANCE_META_KEY  => is_string( $provenance ) ? $provenance : '',
		);

		foreach ( $values as $meta_key => $value ) {
			if ( '' === $value ) {
				continue;
			}

			self::update_meta_if_changed( $entry_id, $form_id, $meta_key, $value );
			$entry[ $meta_key ] = $value;
		}

		CEFA_Conversion_Tracking_Attribution_Ledger::persist_entry_reference( $entry_id, $form_id, $ledger );

		return $entry;
	}

	/**
	 * Read canonical attribution already saved for an entry.
	 *
	 * @param array<string, mixed> $entry Gravity Forms entry.
	 * @return array<string, mixed>
	 */
	public static function from_entry( array $entry ): array {
		$encoded = (string) rgar( $entry, self::ATTRIBUTION_META_KEY );

		if ( '' === $encoded && function_exists( 'gform_get_meta' ) && ! empty( $entry['id'] ) ) {
			$encoded = (string) gform_get_meta( (int) $entry['id'], self::ATTRIBUTION_META_KEY );
		}

		$data = '' !== $encoded ? json_decode( $encoded, true ) : null;

		return is_array( $data ) ? $data : array();
	}

	/**
	 * Decode the host-scoped cookie using the server-only secret.
	 *
	 * @return array<string, mixed>
	 */
	public static function current_verified_envelope(): array {
		$secret       = CEFA_Conversion_Tracking_Config::attribution_v2_secret();
		$site_context = CEFA_Conversion_Tracking_Config::site_context();
		$cookie_name  = CEFA_Conversion_Tracking_Config::attribution_cookie_name();

		$envelope = array();

		if ( '' !== $secret && 'unknown' !== $site_context && '' !== $cookie_name && isset( $_COOKIE[ $cookie_name ] ) ) {
			$token    = sanitize_text_field( wp_unslash( $_COOKIE[ $cookie_name ] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
			$envelope = CEFA_Conversion_Tracking_Attribution_Envelope::decode( $token, $secret, $site_context );
		}

		if ( empty( $envelope ) ) {
			$resolved = CEFA_Conversion_Tracking_Attribution_Ledger::resolve( $_COOKIE, $_POST ); // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Signed fallback token is verified before use.
			$envelope = is_array( $resolved['envelope'] ?? null ) ? $resolved['envelope'] : array();
		}

		return CEFA_Conversion_Tracking_Attribution_Envelope::with_browser_ids( $envelope, $_COOKIE );
	}

	/**
	 * Keep repeated after-submission/confirmation hooks idempotent.
	 *
	 * @param int    $entry_id Entry ID.
	 * @param int    $form_id  Form ID.
	 * @param string $meta_key Meta key.
	 * @param string $value    Meta value.
	 * @return void
	 */
	private static function update_meta_if_changed( int $entry_id, int $form_id, string $meta_key, string $value ): void {
		if ( function_exists( 'gform_get_meta' ) && 0 === strcmp( $value, (string) gform_get_meta( $entry_id, $meta_key ) ) ) {
			return;
		}

		if ( function_exists( 'gform_update_meta' ) ) {
			gform_update_meta( $entry_id, $meta_key, $value, $form_id );
		}
	}
}
