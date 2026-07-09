<?php
/**
 * No-PII legacy versus canonical attribution parity evidence.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Stores match categories without duplicating raw attribution values.
 */
final class CEFA_Conversion_Tracking_Attribution_Parity {
	public const PARITY_META_KEY = 'cefa_conversion_tracking_attribution_parity_v1';

	/**
	 * Compare saved legacy fields with canonical metadata during shadow mode.
	 *
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	public static function persist_after_submission( array $entry, array $form_config ): array {
		$entry_id = (int) rgar( $entry, 'id' );

		if ( 'shadow' !== CEFA_Conversion_Tracking_Config::attribution_v2_mode() || $entry_id < 1 ) {
			return $entry;
		}

		$existing = self::existing_parity( $entry );

		if ( ! empty( $existing ) ) {
			$entry[ self::PARITY_META_KEY ] = wp_json_encode( $existing, JSON_UNESCAPED_SLASHES );
			return $entry;
		}

		$envelope = CEFA_Conversion_Tracking_Entry_Attribution::from_entry( $entry );
		$fields   = is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();
		$expected = CEFA_Conversion_Tracking_Attribution::canonical_compatibility_values( $envelope, $form_config );

		if ( empty( $envelope ) || empty( $fields ) || empty( $expected ) ) {
			return $entry;
		}

		$checked           = 0;
		$matched           = 0;
		$mismatch_keys     = array();
		$legacy_missing    = array();
		$canonical_missing = array();

		foreach ( $fields as $semantic_key => $field_id ) {
			if ( ! array_key_exists( $semantic_key, $expected ) ) {
				continue;
			}

			$legacy    = self::normalize_for_comparison( $semantic_key, (string) rgar( $entry, (string) $field_id ) );
			$canonical = self::normalize_for_comparison( $semantic_key, (string) $expected[ $semantic_key ] );

			if ( '' === $legacy && '' === $canonical ) {
				continue;
			}

			++$checked;

			if ( 0 === strcmp( $legacy, $canonical ) ) {
				++$matched;
			} elseif ( '' === $legacy ) {
				$legacy_missing[] = $semantic_key;
			} elseif ( '' === $canonical ) {
				$canonical_missing[] = $semantic_key;
			} else {
				$mismatch_keys[] = $semantic_key;
			}
		}

		$summary = array(
			'schema_version'          => '1.0',
			'checked_count'           => $checked,
			'matched_count'           => $matched,
			'mismatch_count'          => count( $mismatch_keys ),
			'legacy_missing_count'    => count( $legacy_missing ),
			'canonical_missing_count' => count( $canonical_missing ),
			'parity_rate'             => $checked > 0 ? round( $matched / $checked, 4 ) : 0,
			'mismatch_keys'           => array_values( $mismatch_keys ),
			'legacy_missing_keys'     => array_values( $legacy_missing ),
			'canonical_missing_keys'  => array_values( $canonical_missing ),
		);
		$encoded = wp_json_encode( $summary, JSON_UNESCAPED_SLASHES );

		if ( is_string( $encoded ) && function_exists( 'gform_update_meta' ) ) {
			gform_update_meta( $entry_id, self::PARITY_META_KEY, $encoded, (int) ( $form_config['id'] ?? 0 ) );
			$entry[ self::PARITY_META_KEY ] = $encoded;
		}

		return $entry;
	}

	/**
	 * Read existing parity metadata for idempotency.
	 *
	 * @param array<string, mixed> $entry Entry.
	 * @return array<string, mixed>
	 */
	private static function existing_parity( array $entry ): array {
		$value = (string) rgar( $entry, self::PARITY_META_KEY );

		if ( '' === $value && function_exists( 'gform_get_meta' ) && ! empty( $entry['id'] ) ) {
			$value = (string) gform_get_meta( (int) $entry['id'], self::PARITY_META_KEY );
		}

		$decoded = '' !== $value ? json_decode( $value, true ) : null;

		return is_array( $decoded ) ? $decoded : array();
	}

	/**
	 * Normalize values without retaining or returning raw values in the summary.
	 *
	 * @param string $semantic_key Semantic key.
	 * @param string $value        Value.
	 * @return string
	 */
	private static function normalize_for_comparison( string $semantic_key, string $value ): string {
		$value = trim( sanitize_text_field( $value ) );

		if ( preg_match( '/(?:landing|referrer)/', $semantic_key ) && '' !== $value ) {
			$parts = wp_parse_url( $value );

			if ( is_array( $parts ) && ! empty( $parts['host'] ) ) {
				return strtolower( (string) $parts['host'] ) . '/' . ltrim( (string) ( $parts['path'] ?? '' ), '/' );
			}
		}

		if ( preg_match( '/(?:source|medium|channel)/', $semantic_key ) ) {
			return strtolower( $value );
		}

		return $value;
	}
}
