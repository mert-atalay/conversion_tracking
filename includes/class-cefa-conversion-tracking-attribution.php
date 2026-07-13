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
	 * Correct parent Form 4 attribution when the current touch has a paid click.
	 *
	 * This adapter does not require broad primary mode and never touches field
	 * 32 or event identity. First-touch fields are written only when canonical
	 * evidence is present, while stale last-touch and click-ID fields are cleared
	 * as part of the proven paid-touch replacement.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function apply_parent_paid_click_fields( array $form_config ): void {
		if (
			! CEFA_Conversion_Tracking_Config::parent_paid_click_writeback_enabled() ||
			CEFA_Conversion_Tracking_Config::parent_canonical_writeback_enabled() ||
			'parent' !== CEFA_Conversion_Tracking_Config::site_context() ||
			'off' === CEFA_Conversion_Tracking_Config::attribution_v2_mode() ||
			4 !== (int) ( $form_config['id'] ?? 0 )
		) {
			return;
		}

		$envelope = CEFA_Conversion_Tracking_Entry_Attribution::current_verified_envelope();
		$last     = is_array( $envelope['last_non_direct_touch'] ?? null ) ? $envelope['last_non_direct_touch'] : array();
		$clicks   = is_array( $envelope['click_ids'] ?? null ) ? $envelope['click_ids'] : array();
		$type     = sanitize_key( (string) ( $last['click_id_type'] ?? '' ) );

		if (
			! in_array( $type, array( 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid' ), true ) ||
			'' === self::map_value( $clicks, $type ) ||
			( 'fbclid' === $type && ! self::has_meta_paid_context( $envelope, $last ) )
		) {
			return;
		}

		$fields = is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();
		$values = self::canonical_compatibility_values( $envelope, $form_config );

		foreach ( array( 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid' ) as $click_key ) {
			$values[ $click_key ] = $type === $click_key ? self::map_value( $clicks, $type ) : '';
		}

		foreach ( array( 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid' ) as $semantic_key ) {
			if ( ! isset( $fields[ $semantic_key ] ) || ! array_key_exists( $semantic_key, $values ) ) {
				continue;
			}

			self::write_approved_post_field(
				(int) $form_config['id'],
				(string) $fields[ $semantic_key ],
				(string) $values[ $semantic_key ],
				'cefa_ct_parent_paid_click_form_'
			);
		}

		foreach ( array( 'first_landing_page', 'first_referrer' ) as $semantic_key ) {
			if ( ! isset( $fields[ $semantic_key ] ) || empty( $values[ $semantic_key ] ) ) {
				continue;
			}

			self::write_approved_post_field(
				(int) $form_config['id'],
				(string) $fields[ $semantic_key ],
				(string) $values[ $semantic_key ],
				'cefa_ct_parent_paid_click_form_'
			);
		}
	}

	/**
	 * Populate parent Form 4 attribution fields from canonical current evidence.
	 *
	 * This adapter remains independent from broad primary mode and event-ID
	 * ownership. It replaces last-touch fields only when the verified canonical
	 * envelope has a meaningful non-direct touch. A bare fbclid is downgraded
	 * to referral unless governed campaign evidence proves that it was paid.
	 *
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return void
	 */
	public static function apply_parent_canonical_fields( array $form_config ): void {
		if (
			! CEFA_Conversion_Tracking_Config::parent_canonical_writeback_enabled() ||
			'parent' !== CEFA_Conversion_Tracking_Config::site_context() ||
			'off' === CEFA_Conversion_Tracking_Config::attribution_v2_mode() ||
			4 !== (int) ( $form_config['id'] ?? 0 )
		) {
			return;
		}

		$envelope = CEFA_Conversion_Tracking_Entry_Attribution::current_verified_envelope();
		$values   = self::parent_canonical_writeback_values( $envelope, $form_config );

		if ( empty( $values ) ) {
			return;
		}

		$fields = is_array( $form_config['attribution_fields'] ?? null ) ? $form_config['attribution_fields'] : array();

		foreach ( array( 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid' ) as $semantic_key ) {
			if ( ! isset( $fields[ $semantic_key ] ) || ! array_key_exists( $semantic_key, $values ) ) {
				continue;
			}

			self::write_approved_post_field(
				(int) $form_config['id'],
				(string) $fields[ $semantic_key ],
				(string) $values[ $semantic_key ],
				'cefa_ct_parent_canonical_form_'
			);
		}

		foreach ( array( 'first_landing_page', 'first_referrer' ) as $semantic_key ) {
			if ( ! isset( $fields[ $semantic_key ] ) || empty( $values[ $semantic_key ] ) ) {
				continue;
			}

			self::write_approved_post_field(
				(int) $form_config['id'],
				(string) $fields[ $semantic_key ],
				(string) $values[ $semantic_key ],
				'cefa_ct_parent_canonical_form_'
			);
		}
	}

	/**
	 * Build the safe parent Form 4 compatibility values for one envelope.
	 *
	 * Historical click IDs remain useful in the canonical audit envelope, but
	 * the CRM fields represent only the current last non-direct touch. Therefore
	 * every competing click-ID family is intentionally blanked here.
	 *
	 * @param array<string, mixed> $envelope    Verified canonical envelope.
	 * @param array<string, mixed> $form_config Active form configuration.
	 * @return array<string, string>
	 */
	public static function parent_canonical_writeback_values( array $envelope, array $form_config ): array {
		$last      = is_array( $envelope['last_non_direct_touch'] ?? null ) ? $envelope['last_non_direct_touch'] : array();
		$clicks    = is_array( $envelope['click_ids'] ?? null ) ? $envelope['click_ids'] : array();
		$type      = sanitize_key( (string) ( $last['click_id_type'] ?? '' ) );
		$types     = array( 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid' );
		$bare_meta = 'fbclid' === $type && ! self::has_meta_paid_context( $envelope, $last );

		if (
			empty( $last ) ||
			'' === self::touch_value( $last, 'source' ) ||
			'' === self::touch_value( $last, 'medium' ) ||
			( '' !== $type && ! in_array( $type, $types, true ) ) ||
			( '' !== $type && '' === self::map_value( $clicks, $type ) )
		) {
			return array();
		}

		$values = self::canonical_compatibility_values( $envelope, $form_config );

		if ( $bare_meta ) {
			$values['utm_source']   = in_array( self::touch_value( $last, 'source' ), array( 'facebook', 'instagram', 'meta' ), true ) ? self::touch_value( $last, 'source' ) : 'facebook';
			$values['utm_medium']   = 'referral';
			$values['utm_campaign'] = '';
			$values['utm_term']     = '';
			$values['utm_content']  = '';
		}

		foreach ( $types as $click_type ) {
			$values[ $click_type ] = ! $bare_meta && $type === $click_type ? self::map_value( $clicks, $type ) : '';
		}

		return $values;
	}

	/**
	 * Return the compatibility writeback applied to the current request.
	 *
	 * @param int $form_id Gravity Forms form ID.
	 * @return string
	 */
	public static function compatibility_writeback_status( int $form_id ): string {
		if ( isset( $_POST[ 'cefa_ct_parent_canonical_form_' . $form_id ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Internal same-request marker only.
			return 'parent_canonical';
		}

		if ( isset( $_POST[ 'cefa_ct_parent_paid_click_form_' . $form_id ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Internal same-request marker only.
			return 'parent_paid_click';
		}

		if ( isset( $_POST[ 'cefa_ct_primary_form_' . $form_id ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Internal same-request marker only.
			return 'primary';
		}

		return 'none';
	}

	/**
	 * Require governed campaign evidence before treating fbclid as paid.
	 *
	 * Facebook appends fbclid to organic outbound links too. CEFA paid URLs add
	 * campaign metadata, and may also add governed Meta platform IDs.
	 *
	 * @param array<string, mixed> $envelope Canonical attribution envelope.
	 * @param array<string, mixed> $last     Current last non-direct touch.
	 * @return bool
	 */
	private static function has_meta_paid_context( array $envelope, array $last ): bool {
		$platform_ids = is_array( $envelope['platform_ids'] ?? null ) ? $envelope['platform_ids'] : array();

		foreach ( array( 'meta_campaign_id', 'meta_adset_id', 'meta_ad_id' ) as $key ) {
			if ( '' !== self::map_value( $platform_ids, $key ) ) {
				return true;
			}
		}

		return in_array( self::touch_value( $last, 'source' ), array( 'facebook', 'instagram', 'meta' ), true )
			&& 'paid_social' === self::touch_value( $last, 'medium' )
			&& (
				'' !== self::touch_value( $last, 'campaign' ) ||
				'' !== self::touch_value( $last, 'content' ) ||
				'' !== self::touch_value( $last, 'term' )
			);
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
	 * @param string $marker   Internal request marker prefix.
	 * @return void
	 */
	private static function write_approved_post_field( int $form_id, string $field_id, string $value, string $marker = 'cefa_ct_primary_form_' ): void {
		$max_length = in_array( $field_id, array( '20', '21', '28', '45', '46' ), true ) ? 1000 : 220;
		$value      = substr( sanitize_text_field( $value ), 0, $max_length );

		foreach ( array( 'input_' . $field_id, 'input_' . str_replace( '.', '_', $field_id ) ) as $post_key ) {
			$_POST[ $post_key ] = $value; // phpcs:ignore WordPress.Security.NonceVerification.Missing
		}

		$_POST[ $marker . $form_id ] = '1'; // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Internal same-request marker only.
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
