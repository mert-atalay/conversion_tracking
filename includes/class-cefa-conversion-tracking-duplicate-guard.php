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
 * Stores short-lived tracking payloads with guarded replay-safe retrieval.
 */
final class CEFA_Conversion_Tracking_Duplicate_Guard {
	/**
	 * Transient key prefix.
	 */
	private const TRANSIENT_PREFIX = 'cefa_conversion_tracking_';

	/**
	 * Payload lifetime in seconds.
	 */
	private const PAYLOAD_TTL = 30 * MINUTE_IN_SECONDS;

	/**
	 * Store a payload behind an opaque legacy or signed V2 token.
	 *
	 * @param array<string, mixed> $payload Tracking payload.
	 * @return string
	 */
	public static function store_payload( array $payload ): string {
		$token = self::v2_ready() ? self::signed_token( $payload ) : wp_generate_uuid4();

		if ( '' === $token ) {
			return '';
		}

		set_transient( self::payload_key( $token ), $payload, self::PAYLOAD_TTL );
		self::store_event_token_alias( $payload, $token );

		return $token;
	}

	/**
	 * Read a payload, retaining signed V2 payloads for safe replay during TTL.
	 *
	 * @param string $token Payload token.
	 * @return array<string, mixed>|null
	 */
	public static function consume_payload( string $token ): ?array {
		$token = self::normalize_token( $token );

		if ( '' === $token ) {
			return null;
		}

		$is_v2 = false !== strpos( $token, '.' );

		if ( $is_v2 && ! self::valid_signed_token( $token ) ) {
			return null;
		}

		$key     = self::payload_key( $token );
		$payload = get_transient( $key );

		if ( false === $payload || ! is_array( $payload ) ) {
			return null;
		}

		if ( ! $is_v2 ) {
			delete_transient( $key );
			self::delete_event_token_alias( $payload );
		}

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

		if ( ! preg_match( '/^[A-Za-z0-9_.-]{8,512}$/', $token ) ) {
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

	/**
	 * Return a bounded transient key for either token generation.
	 *
	 * @param string $token Payload token.
	 * @return string
	 */
	private static function payload_key( string $token ): string {
		if ( false !== strpos( $token, '.' ) ) {
			return self::TRANSIENT_PREFIX . 'payload_' . hash( 'sha256', $token );
		}

		return self::TRANSIENT_PREFIX . $token;
	}

	/**
	 * Confirm V2 is explicitly enabled and has a signing secret.
	 *
	 * @return bool
	 */
	private static function v2_ready(): bool {
		return CEFA_Conversion_Tracking_Config::payload_v2_enabled()
			&& '' !== CEFA_Conversion_Tracking_Config::payload_v2_secret();
	}

	/**
	 * Issue a signed token containing only event identity, context, and expiry.
	 *
	 * @param array<string, mixed> $payload Tracking payload.
	 * @return string
	 */
	private static function signed_token( array $payload ): string {
		$event_id = CEFA_Conversion_Tracking_Event_ID::normalize_event_id( (string) ( $payload['event_id'] ?? '' ) );

		if ( '' === $event_id ) {
			return '';
		}

		$claims = wp_json_encode(
			array(
				'event_id'     => $event_id,
				'site_context' => CEFA_Conversion_Tracking_Config::site_context(),
				'expires_at'   => time() + self::PAYLOAD_TTL,
				'nonce'        => bin2hex( random_bytes( 16 ) ),
			),
			JSON_UNESCAPED_SLASHES
		);

		if ( ! is_string( $claims ) ) {
			return '';
		}

		$encoded   = self::base64url_encode( $claims );
		$signature = self::base64url_encode(
			hash_hmac( 'sha256', $encoded, CEFA_Conversion_Tracking_Config::payload_v2_secret(), true )
		);

		return $encoded . '.' . $signature;
	}

	/**
	 * Verify token signature, expiry, and hostname-scoped context.
	 *
	 * @param string $token Signed token.
	 * @return bool
	 */
	private static function valid_signed_token( string $token ): bool {
		$parts = explode( '.', $token );

		if ( 2 !== count( $parts ) || '' === CEFA_Conversion_Tracking_Config::payload_v2_secret() ) {
			return false;
		}

		$expected = self::base64url_encode(
			hash_hmac( 'sha256', $parts[0], CEFA_Conversion_Tracking_Config::payload_v2_secret(), true )
		);

		if ( ! hash_equals( $expected, $parts[1] ) ) {
			return false;
		}

		$json   = self::base64url_decode( $parts[0] );
		$claims = is_string( $json ) ? json_decode( $json, true ) : null;

		return is_array( $claims )
			&& time() <= (int) ( $claims['expires_at'] ?? 0 )
			&& 0 === strcmp( CEFA_Conversion_Tracking_Config::site_context(), (string) ( $claims['site_context'] ?? '' ) )
			&& '' !== CEFA_Conversion_Tracking_Event_ID::normalize_event_id( (string) ( $claims['event_id'] ?? '' ) );
	}

	/**
	 * Base64url encode token data.
	 *
	 * @param string $value Data.
	 * @return string
	 */
	private static function base64url_encode( string $value ): string {
		return rtrim( strtr( base64_encode( $value ), '+/', '-_' ), '=' ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_encode -- Required for compact signed tokens.
	}

	/**
	 * Base64url decode token data.
	 *
	 * @param string $value Encoded data.
	 * @return string|false
	 */
	private static function base64url_decode( string $value ) {
		$padding = strlen( $value ) % 4;

		if ( $padding ) {
			$value .= str_repeat( '=', 4 - $padding );
		}

		return base64_decode( strtr( $value, '-_', '+/' ), true ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_decode -- Decodes compact signed tokens.
	}
}
