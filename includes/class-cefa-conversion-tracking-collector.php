<?php
/**
 * Optional Form 4 server-side collector dispatch.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Sends no-PII Form 4 audit payloads to the CEFA Cloud Run collector.
 */
final class CEFA_Conversion_Tracking_Collector {
	/**
	 * Send a Form 4 audit payload when enabled.
	 *
	 * @param array<string, mixed> $payload     DataLayer-safe payload.
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function send_form4_event( array $payload, array $entry, array $form_config ): void {
		$config = CEFA_Conversion_Tracking_Config::collector_config();

		if ( empty( $config['enabled'] ) || empty( $config['url'] ) || empty( $config['secret'] ) ) {
			return;
		}

		if ( '4' !== (string) ( $payload['form_id'] ?? '' ) ) {
			return;
		}

		if ( 'school_inquiry_submit' !== (string) ( $payload['event'] ?? '' ) ) {
			return;
		}

		if ( 'spam' === (string) rgar( $entry, 'status' ) ) {
			return;
		}

		$collector_payload = self::collector_payload( $payload, $entry, $form_config );
		$body              = wp_json_encode( $collector_payload );

		if ( ! is_string( $body ) || '' === $body ) {
			return;
		}

		$timestamp = (string) time();
		$signature = hash_hmac( 'sha256', $timestamp . '.' . $body, (string) $config['secret'] );

		wp_remote_post(
			(string) $config['url'],
			array(
				'timeout'   => 2,
				'blocking'  => false,
				'headers'   => array(
					'Content-Type'     => 'application/json',
					'X-CEFA-Timestamp' => $timestamp,
					'X-CEFA-Signature' => 'sha256=' . $signature,
				),
				'body'      => $body,
				'sslverify' => true,
			)
		);
	}

	/**
	 * Build an allowlisted collector payload.
	 *
	 * @param array<string, mixed> $payload     DataLayer-safe payload.
	 * @param array<string, mixed> $entry       Gravity Forms entry.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, mixed>
	 */
	private static function collector_payload( array $payload, array $entry, array $form_config ): array {
		unset( $form_config );

		$allowed_keys = array(
			'event',
			'event_id',
			'form_id',
			'form_family',
			'lead_type',
			'lead_intent',
			'school_selected_id',
			'school_selected_slug',
			'school_selected_name',
			'program_id',
			'program_name',
			'days_per_week',
			'utm_source',
			'utm_medium',
			'utm_campaign',
			'utm_term',
			'utm_content',
			'gclid',
			'gbraid',
			'wbraid',
			'fbclid',
			'msclkid',
			'first_landing_page',
			'first_referrer',
			'event_source_url',
			'inquiry_success_url',
			'tracking_source',
			'page_context',
			'inquiry_success',
		);

		$collector_payload = array();

		foreach ( $allowed_keys as $key ) {
			if ( array_key_exists( $key, $payload ) ) {
				$collector_payload[ $key ] = $payload[ $key ];
			}
		}

		$submitted_at = (string) rgar( $entry, 'date_created' );

		if ( '' !== $submitted_at ) {
			$collector_payload['submitted_at'] = $submitted_at;
		}

		$collector_payload['event_timestamp'] = gmdate( 'c' );

		return $collector_payload;
	}
}
