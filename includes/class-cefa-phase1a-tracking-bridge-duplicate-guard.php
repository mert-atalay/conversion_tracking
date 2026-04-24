<?php
/**
 * Duplicate guard helpers.
 *
 * @package CEFA_Phase1A_Tracking_Bridge
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Stores and consumes short-lived tracking payloads.
 */
final class CEFA_Phase1A_Tracking_Bridge_Duplicate_Guard {
	/**
	 * Transient key prefix.
	 */
	private const TRANSIENT_PREFIX = 'cefa_phase1a_tracking_';

	/**
	 * Payload lifetime in seconds.
	 */
	private const PAYLOAD_TTL = 15 * MINUTE_IN_SECONDS;

	/**
	 * Store a payload behind a one-time token.
	 *
	 * @param array<string, mixed> $payload Tracking payload.
	 * @return string
	 */
	public static function store_payload( array $payload ): string {
		$token = wp_generate_uuid4();

		set_transient( self::TRANSIENT_PREFIX . $token, $payload, self::PAYLOAD_TTL );

		return $token;
	}

	/**
	 * Consume a one-time payload.
	 *
	 * @param string $token Payload token.
	 * @return array<string, mixed>|null
	 */
	public static function consume_payload( string $token ): ?array {
		$token = self::normalize_token( $token );

		if ( '' === $token ) {
			return null;
		}

		$key     = self::TRANSIENT_PREFIX . $token;
		$payload = get_transient( $key );

		if ( false === $payload || ! is_array( $payload ) ) {
			return null;
		}

		delete_transient( $key );

		return $payload;
	}

	/**
	 * Normalize token from request.
	 *
	 * @param string $token Token candidate.
	 * @return string
	 */
	public static function normalize_token( string $token ): string {
		$token = trim( $token );

		if ( ! preg_match( '/^[A-Za-z0-9_-]{8,128}$/', $token ) ) {
			return '';
		}

		return $token;
	}
}
