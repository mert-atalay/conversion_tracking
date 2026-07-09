<?php
/**
 * Plugin Name: CEFA Conversion Tracking
 * Description: Emits clean CEFA conversion, micro-conversion, and attribution dataLayer events.
 * Version: 0.5.0
 * Requires at least: 6.3
 * Requires PHP: 7.4
 * Author: CEFA
 * License: GPL-2.0-or-later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Update URI: https://github.com/mert-atalay/conversion_tracking
 * Text Domain: cefa-conversion-tracking
 *
 * @package CEFA_Conversion_Tracking
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'CEFA_CONVERSION_TRACKING_VERSION', '0.5.0' );
define( 'CEFA_CONVERSION_TRACKING_FILE', __FILE__ );
define( 'CEFA_CONVERSION_TRACKING_DIR', plugin_dir_path( __FILE__ ) );
define( 'CEFA_CONVERSION_TRACKING_URL', plugin_dir_url( __FILE__ ) );
define( 'CEFA_CONVERSION_TRACKING_FORM_ID', 4 );

require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-config.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-attribution-envelope.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-entry-attribution.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-attribution-parity.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-event-id.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-event-id-registry.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-submission-identity.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-attribution.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-datalayer-payload.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-duplicate-guard.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-collector.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-confirmation-payload.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-rest-controller.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking.php';

register_activation_hook( CEFA_CONVERSION_TRACKING_FILE, array( 'CEFA_Conversion_Tracking_Event_ID_Registry', 'activate' ) );

CEFA_Conversion_Tracking::init();
