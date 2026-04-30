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
							'form_id'       => '4',
							'form_family'   => 'parent_inquiry',
							'lead_type'     => 'cefa_lead',
							'lead_intent'   => 'inquire_now',
							'page_context'  => 'parent',
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
							'location_interest'     => '32',
							'investment_range'      => '7',
							'opening_timeline'      => '10',
							'school_count_goal'     => '11',
							'ownership_structure'   => '12',
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
							'site_offered_by'               => '39',
							'property_square_footage_range' => '34',
							'outdoor_space_range'           => '35',
							'availability_timeline'         => '36',
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
