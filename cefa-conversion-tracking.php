<?php
/**
 * Plugin Name: CEFA Conversion Tracking
 * Plugin URI: https://github.com/mert-atalay/conversion_tracking
 * Description: Emits one clean school_inquiry_submit dataLayer event after confirmed Gravity Form 4 success.
 * Version: 0.1.0
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

define( 'CEFA_CONVERSION_TRACKING_VERSION', '0.1.0' );
define( 'CEFA_CONVERSION_TRACKING_FILE', __FILE__ );
define( 'CEFA_CONVERSION_TRACKING_DIR', plugin_dir_path( __FILE__ ) );
define( 'CEFA_CONVERSION_TRACKING_URL', plugin_dir_url( __FILE__ ) );
define( 'CEFA_CONVERSION_TRACKING_FORM_ID', 4 );

require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-event-id.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-datalayer-payload.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-duplicate-guard.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-confirmation-payload.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking-rest-controller.php';
require_once CEFA_CONVERSION_TRACKING_DIR . 'includes/class-cefa-conversion-tracking.php';

CEFA_Conversion_Tracking::init();
