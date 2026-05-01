<?php
/**
 * Duplicate guard helpers.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Stores and consumes short-lived tracking payloads.
 */
final class CEFA_Conversion_Tracking_Duplicate_Guard {
	/**
	 * Transient key prefix.
	 */
	private const TRANSIENT_PREFIX = 'cefa_conversion_tracking_';

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
		self::store_event_token_alias( $payload, $token );

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
		self::delete_event_token_alias( $payload );

		return $payload;
	}

	/**
	 * Consume a payload by its server-confirmed event ID.
	 *
	 * This is a fallback for confirmation flows where another plugin rewrites
	 * the thank-you query string after the helper token is appended.
	 *
	 * @param string $event_id Event ID from the submitted form field or entry meta.
	 * @return array<string, mixed>|null
	 */
	public static function consume_payload_by_event_id( string $event_id ): ?array {
		$event_id = CEFA_Conversion_Tracking_Event_ID::normalize_event_id( $event_id );

		if ( '' === $event_id ) {
			return null;
		}

		$token = get_transient( self::event_token_key( $event_id ) );

		if ( ! is_string( $token ) || '' === self::normalize_token( $token ) ) {
			return null;
		}

		return self::consume_payload( $token );
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

	/**
	 * Store event ID to token alias for thank-you fallback lookups.
	 *
	 * @param array<string, mixed> $payload Tracking payload.
	 * @param string               $token   One-time token.
	 * @return void
	 */
	private static function store_event_token_alias( array $payload, string $token ): void {
		$event_id = CEFA_Conversion_Tracking_Event_ID::normalize_event_id( (string) ( $payload['event_id'] ?? '' ) );

		if ( '' === $event_id ) {
			return;
		}

		set_transient( self::event_token_key( $event_id ), $token, self::PAYLOAD_TTL );
	}

	/**
	 * Delete event ID alias after payload consumption.
	 *
	 * @param array<string, mixed> $payload Tracking payload.
	 * @return void
	 */
	private static function delete_event_token_alias( array $payload ): void {
		$event_id = CEFA_Conversion_Tracking_Event_ID::normalize_event_id( (string) ( $payload['event_id'] ?? '' ) );

		if ( '' === $event_id ) {
			return;
		}

		delete_transient( self::event_token_key( $event_id ) );
	}

	/**
	 * Build a bounded transient key for event ID aliases.
	 *
	 * @param string $event_id Event ID.
	 * @return string
	 */
	private static function event_token_key( string $event_id ): string {
		return self::TRANSIENT_PREFIX . 'event_' . hash( 'sha256', $event_id );
	}
}
