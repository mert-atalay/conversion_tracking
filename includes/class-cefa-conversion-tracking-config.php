<?php
/**
 * Site/form configuration for CEFA conversion tracking.
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Provides hostname-scoped form contracts.
 */
final class CEFA_Conversion_Tracking_Config {
	/**
	 * Gravity Forms entry meta key used when a form has no event ID field.
	 */
	public const EVENT_ID_META_KEY = 'cefa_conversion_tracking_event_id';

	/**
	 * Return the guarded Attribution Bridge runtime mode.
	 *
	 * The value may be a scalar or a hostname-keyed array/JSON object. Unknown
	 * values fail closed to off.
	 *
	 * @return string
	 */
	public static function attribution_v2_mode(): string {
		$value = self::hostname_config_value( 'CEFA_CT_ATTRIBUTION_V2_MODE' );
		$mode  = strtolower( trim( (string) $value ) );

		return in_array( $mode, array( 'off', 'shadow', 'primary' ), true ) ? $mode : 'off';
	}

	/**
	 * Return the guarded runtime profile for bridge coexistence.
	 *
	 * Full preserves the current conversion lifecycle. Attribution-only captures
	 * shadow evidence without competing with an existing WPCode event bridge.
	 *
	 * @return string
	 */
	public static function runtime_profile(): string {
		$value   = self::hostname_config_value( 'CEFA_CT_RUNTIME_PROFILE' );
		$profile = strtolower( trim( (string) $value ) );

		return 'attribution_only' === $profile ? $profile : 'full';
	}

	/**
	 * Return the guarded server-side attribution ledger mode.
	 *
	 * @return string
	 */
	public static function ledger_mode(): string {
		$value = self::hostname_config_value( 'CEFA_CT_LEDGER_MODE' );
		$mode  = strtolower( trim( (string) $value ) );

		return in_array( $mode, array( 'off', 'shadow', 'primary' ), true ) ? $mode : 'off';
	}

	/**
	 * Return the server-only ledger token signing secret.
	 *
	 * @return string
	 */
	public static function ledger_secret(): string {
		return trim( (string) self::config_value( 'CEFA_CT_LEDGER_SECRET' ) );
	}

	/**
	 * Return the host-only opaque capture cookie name.
	 *
	 * @return string
	 */
	public static function ledger_cookie_name(): string {
		$names = array(
			'parent'       => 'cefa_parent_capture_v2',
			'franchise_ca' => 'cefa_fr_ca_capture_v2',
			'franchise_us' => 'cefa_fr_us_capture_v2',
		);

		return $names[ self::site_context() ] ?? '';
	}

	/**
	 * Return the server-only Attribution Bridge signing secret.
	 *
	 * @return string
	 */
	public static function attribution_v2_secret(): string {
		return trim( (string) self::config_value( 'CEFA_CT_ATTRIBUTION_SECRET' ) );
	}

	/**
	 * Whether canonical attribution may populate approved CRM compatibility fields.
	 *
	 * @return bool
	 */
	public static function crm_identity_enabled(): bool {
		return self::truthy_config_value( self::hostname_config_value( 'CEFA_CT_CRM_IDENTITY_ENABLED' ) );
	}

	/**
	 * Whether verified parent paid clicks may correct Form 4 attribution fields.
	 *
	 * This is intentionally independent from the broad primary cutover so paid
	 * attribution can be corrected without changing event-ID ownership.
	 *
	 * @return bool
	 */
	public static function parent_paid_click_writeback_enabled(): bool {
		return self::truthy_config_value( self::hostname_config_value( 'CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED' ) );
	}

	/**
	 * Whether signed, replay-safe confirmation payloads are enabled.
	 *
	 * @return bool
	 */
	public static function payload_v2_enabled(): bool {
		return self::truthy_config_value( self::hostname_config_value( 'CEFA_CT_PAYLOAD_V2_ENABLED' ) );
	}

	/**
	 * Return the server-only confirmation payload signing secret.
	 *
	 * @return string
	 */
	public static function payload_v2_secret(): string {
		return trim( (string) self::config_value( 'CEFA_CT_PAYLOAD_SECRET' ) );
	}

	/**
	 * Return the current governed site context.
	 *
	 * @return string
	 */
	public static function site_context(): string {
		$context = self::active_context();

		return sanitize_key( (string) ( $context['context_key'] ?? 'unknown' ) );
	}

	/**
	 * Return the host-only attribution cookie name for the current context.
	 *
	 * @return string
	 */
	public static function attribution_cookie_name(): string {
		$names = array(
			'parent'       => 'cefa_parent_attr_v1',
			'franchise_ca' => 'cefa_fr_ca_attr_v1',
			'franchise_us' => 'cefa_fr_us_attr_v1',
		);

		return $names[ self::site_context() ] ?? '';
	}

	/**
	 * Return active form configs for the current hostname.
	 *
	 * @return array<int, array<string, mixed>>
	 */
	public static function active_forms(): array {
		$context = self::active_context();

		return is_array( $context['forms'] ?? null ) ? $context['forms'] : array();
	}

	/**
	 * Return the active form IDs.
	 *
	 * @return int[]
	 */
	public static function active_form_ids(): array {
		return array_map( 'intval', array_keys( self::active_forms() ) );
	}

	/**
	 * Return a single active form config.
	 *
	 * @param int $form_id Gravity Forms form ID.
	 * @return array<string, mixed>
	 */
	public static function form_config( int $form_id ): array {
		$forms = self::active_forms();

		return is_array( $forms[ $form_id ] ?? null ) ? $forms[ $form_id ] : array();
	}

	/**
	 * Build data passed to the browser bridge.
	 *
	 * @return array<string, mixed>
	 */
	public static function browser_config(): array {
		$forms        = self::active_forms();
		$primary_form = self::primary_form( $forms );

		return array(
			'siteContext'         => self::site_context(),
			'runtimeProfile'      => self::runtime_profile(),
			'ledgerMode'          => self::ledger_mode(),
			'ownHosts'            => self::approved_cefa_hosts(),
			'formId'              => (int) ( $primary_form['id'] ?? CEFA_CONVERSION_TRACKING_FORM_ID ),
			'forms'               => array_values( $forms ),
			'finalEvents'         => self::final_event_names( $forms ),
			'eventFieldSelectors' => array(
				'[name="input_32_4"]',
				'[name="input_32.4"]',
				'#input_4_32_4',
				'input[data-cefa-si-meta="4"]',
			),
		);
	}

	/**
	 * Return exact CEFA journey hosts that must not become referral sources.
	 *
	 * @return string[]
	 */
	private static function approved_cefa_hosts(): array {
		$hosts = array();

		foreach ( self::contexts() as $context ) {
			if ( is_array( $context['hostnames'] ?? null ) ) {
				$hosts = array_merge( $hosts, $context['hostnames'] );
			}
		}

		return array_values( array_unique( array_map( 'strtolower', $hosts ) ) );
	}

	/**
	 * Optional server-side collector configuration.
	 *
	 * The collector is disabled unless explicitly enabled through constants or
	 * environment variables. This keeps production behavior unchanged after
	 * deployment until staging validation and explicit enablement happen.
	 *
	 * @return array<string, mixed>
	 */
	public static function collector_config(): array {
		return array(
			'enabled' => self::truthy_config_value( self::config_value( 'CEFA_CT_COLLECTOR_ENABLED' ) ),
			'url'     => esc_url_raw( (string) self::config_value( 'CEFA_CT_COLLECTOR_URL' ) ),
			'secret'  => (string) self::config_value( 'CEFA_CT_COLLECTOR_SECRET' ),
		);
	}

	/**
	 * Read a constant or environment variable without exposing secret values.
	 *
	 * @param string $name Constant/environment variable name.
	 * @return mixed
	 */
	private static function config_value( string $name ) {
		if ( defined( $name ) ) {
			return constant( $name );
		}

		$value = getenv( $name );

		return false === $value ? '' : $value;
	}

	/**
	 * Read a scalar or hostname-keyed configuration value.
	 *
	 * @param string $name Constant/environment variable name.
	 * @return mixed
	 */
	private static function hostname_config_value( string $name ) {
		$value = self::config_value( $name );

		if ( is_string( $value ) && '' !== trim( $value ) && in_array( substr( trim( $value ), 0, 1 ), array( '{', '[' ), true ) ) {
			$decoded = json_decode( $value, true );

			if ( is_array( $decoded ) ) {
				$value = $decoded;
			}
		}

		if ( ! is_array( $value ) ) {
			return $value;
		}

		$host = self::current_host();

		if ( array_key_exists( $host, $value ) ) {
			return $value[ $host ];
		}

		return $value['default'] ?? '';
	}

	/**
	 * Interpret common truthy config strings.
	 *
	 * @param mixed $value Config value.
	 * @return bool
	 */
	private static function truthy_config_value( $value ): bool {
		return in_array( strtolower( trim( (string) $value ) ), array( '1', 'true', 'yes', 'on' ), true );
	}

	/**
	 * Return the active context.
	 *
	 * @return array<string, mixed>
	 */
	private static function active_context(): array {
		$contexts = self::contexts();
		$host     = self::current_host();

		foreach ( $contexts as $context_key => $context ) {
			$hostnames = is_array( $context['hostnames'] ?? null ) ? $context['hostnames'] : array();

			if ( in_array( $host, $hostnames, true ) ) {
				$context['context_key'] = $context_key;
				return $context;
			}
		}

		return array(
			'context_key' => 'unknown',
			'hostnames'   => array(),
			'forms'       => array(),
		);
	}

	/**
	 * Current request hostname.
	 *
	 * @return string
	 */
	private static function current_host(): string {
		$host = '';

		if ( isset( $_SERVER['HTTP_HOST'] ) ) {
			$host = sanitize_text_field( wp_unslash( $_SERVER['HTTP_HOST'] ) );
		}

		if ( '' === $host ) {
			$host = (string) wp_parse_url( home_url(), PHP_URL_HOST );
		}

		return strtolower( preg_replace( '/:\d+$/', '', $host ) );
	}

	/**
	 * Return the first active form, preferring the parent form for legacy JS.
	 *
	 * @param array<int, array<string, mixed>> $forms Active forms.
	 * @return array<string, mixed>
	 */
	private static function primary_form( array $forms ): array {
		if ( isset( $forms[ CEFA_CONVERSION_TRACKING_FORM_ID ] ) ) {
			return $forms[ CEFA_CONVERSION_TRACKING_FORM_ID ];
		}

		$first = reset( $forms );

		return is_array( $first ) ? $first : array();
	}

	/**
	 * Final dataLayer event names for active forms.
	 *
	 * @param array<int, array<string, mixed>> $forms Active forms.
	 * @return string[]
	 */
	private static function final_event_names( array $forms ): array {
		$events = array();

		foreach ( $forms as $form ) {
			if ( ! empty( $form['event_name'] ) ) {
				$events[] = (string) $form['event_name'];
			}
		}

		return array_values( array_unique( $events ) );
	}

	/**
	 * Hostname-scoped form contracts.
	 *
	 * @return array<string, array<string, mixed>>
	 */
	private static function contexts(): array {
		$contexts = array(
			'parent'       => array(
				'hostnames' => array(
					'cefamain.kinsta.cloud',
					'cefa.ca',
					'www.cefa.ca',
				),
				'forms'     => array(
					4 => array(
						'id'                   => 4,
						'event_name'           => 'school_inquiry_submit',
						'event_id_fields'      => array( '32.4' ),
						'event_id_post_keys'   => array( 'input_32_4', 'input_32.4' ),
						'attribution_backfill' => true,
						'attribution_fields'   => self::parent_attribution_fields(),
						'field_map'            => array(
							'school_selected_id'   => '32.1',
							'school_selected_slug' => '32.5',
							'school_selected_name' => '32.6',
							'program_id'           => '32.2',
							'program_name'         => '32.7',
							'days_per_week'        => '32.3',
						),
						'static_payload'       => array(
							'form_id'      => '4',
							'form_family'  => 'parent_inquiry',
							'lead_type'    => 'cefa_lead',
							'lead_intent'  => 'inquire_now',
							'page_context' => 'parent',
						),
					),
				),
			),
			'franchise_ca' => array(
				'hostnames' => array(
					'cefafranchise.kinsta.cloud',
					'franchise.cefa.ca',
				),
				'forms'     => array(
					1 => array(
						'id'                   => 1,
						'event_name'           => 'franchise_inquiry_submit',
						'event_id_fields'      => array(),
						'event_id_post_keys'   => array(),
						'attribution_backfill' => false,
						'attribution_fields'   => self::franchise_attribution_fields(),
						'field_map'            => array(
							'location_interest'   => '32',
							'investment_range'    => '7',
							'opening_timeline'    => '10',
							'school_count_goal'   => '11',
							'ownership_structure' => '12',
						),
						'static_payload'       => array(
							'event_scope'                  => 'primary',
							'site_context'                 => 'franchise_ca',
							'business_unit'                => 'franchise',
							'market'                       => 'canada',
							'country'                      => 'CA',
							'form_id'                      => '1',
							'form_family'                  => 'franchise_inquiry',
							'lead_type'                    => 'franchise_lead',
							'lead_intent'                  => 'franchise_inquiry',
							'location_availability_status' => 'unknown',
						),
					),
					2 => array(
						'id'                   => 2,
						'event_name'           => 'real_estate_site_submit',
						'event_id_fields'      => array(),
						'event_id_post_keys'   => array(),
						'attribution_backfill' => false,
						'attribution_fields'   => self::franchise_attribution_fields(),
						'field_map'            => array(
							'site_offered_by'       => '39',
							'property_square_footage_range' => '34',
							'outdoor_space_range'   => '35',
							'availability_timeline' => '36',
						),
						'static_payload'       => array(
							'event_scope'   => 'primary',
							'site_context'  => 'franchise_ca',
							'business_unit' => 'franchise',
							'market'        => 'canada',
							'country'       => 'CA',
							'form_id'       => '2',
							'form_family'   => 'site_inquiry',
							'lead_type'     => 'real_estate_lead',
							'lead_intent'   => 'submit_a_site',
						),
					),
				),
			),
			'franchise_us' => array(
				'hostnames' => array(
					'cefafranusdev.wpenginepowered.com',
					'franchisecefa.com',
					'www.franchisecefa.com',
				),
				'forms'     => array(
					1 => array(
						'id'                   => 1,
						'event_name'           => 'franchise_inquiry_submit',
						'event_id_fields'      => array(),
						'event_id_post_keys'   => array(),
						'attribution_backfill' => false,
						'attribution_fields'   => self::franchise_attribution_fields(),
						'field_map'            => array(
							'location_interest'   => '32',
							'investment_range'    => '7',
							'opening_timeline'    => '10',
							'school_count_goal'   => '11',
							'ownership_structure' => '12',
						),
						'static_payload'       => array(
							'event_scope'                  => 'primary',
							'site_context'                 => 'franchise_us',
							'business_unit'                => 'franchise',
							'market'                       => 'usa',
							'country'                      => 'US',
							'form_id'                      => '1',
							'form_family'                  => 'franchise_inquiry',
							'lead_type'                    => 'franchise_lead',
							'lead_intent'                  => 'franchise_inquiry',
							'location_availability_status' => 'unknown',
						),
					),
					2 => array(
						'id'                   => 2,
						'event_name'           => 'real_estate_site_submit',
						'event_id_fields'      => array(),
						'event_id_post_keys'   => array(),
						'attribution_backfill' => false,
						'attribution_fields'   => self::franchise_attribution_fields(),
						'field_map'            => array(
							'site_offered_by'       => '39',
							'property_square_footage_range' => '34',
							'outdoor_space_range'   => '35',
							'availability_timeline' => '36',
						),
						'static_payload'       => array(
							'event_scope'   => 'primary',
							'site_context'  => 'franchise_us',
							'business_unit' => 'franchise',
							'market'        => 'usa',
							'country'       => 'US',
							'form_id'       => '2',
							'form_family'   => 'site_inquiry',
							'lead_type'     => 'real_estate_lead',
							'lead_intent'   => 'submit_a_site',
						),
					),
				),
			),
		);

		/**
		 * Filter hostname-scoped conversion tracking contexts.
		 *
		 * @param array<string, array<string, mixed>> $contexts Context contracts.
		 */
		return apply_filters( 'cefa_conversion_tracking_contexts', $contexts );
	}

	/**
	 * Parent Form 4 attribution fields.
	 *
	 * @return array<string, string>
	 */
	private static function parent_attribution_fields(): array {
		return array(
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
	}

	/**
	 * Franchise Canada GAConnector attribution fields.
	 *
	 * @return array<string, string>
	 */
	private static function franchise_attribution_fields(): array {
		return array(
			'lc_source'    => '14',
			'lc_medium'    => '15',
			'lc_campaign'  => '16',
			'lc_content'   => '17',
			'lc_term'      => '18',
			'lc_channel'   => '19',
			'lc_landing'   => '20',
			'lc_referrer'  => '21',
			'fc_source'    => '22',
			'fc_medium'    => '23',
			'fc_campaign'  => '24',
			'fc_content'   => '25',
			'fc_term'      => '26',
			'fc_channel'   => '27',
			'fc_referrer'  => '28',
			'gclid'        => '29',
			'ga_client_id' => '30',
		);
	}
}
