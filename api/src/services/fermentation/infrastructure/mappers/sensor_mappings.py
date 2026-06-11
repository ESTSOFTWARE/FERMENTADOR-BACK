SENSOR_TABLE_MAP = {
    "alcohol":      ("alcohol_sensor",      "alcohol_concentration"),
    "density":      ("density_sensor",      "density"),
    "conductivity": ("conductivity_sensor", "conductivity"),
    "ph":           ("ph_sensor",           "ph_value"),
    "temperature":  ("temperature_sensor",  "temperature"),
    "turbidity":    ("turbidity_sensor",    "turbidity"),
    "rpm":          ("motor_rpm_sensor",    "rpm"),
}

SENSOR_REPORT_MAP = {
    "alcohol":      ("alcohol_initial",      "alcohol_final",      "alcohol_deactivated_at",      "alcohol_last_reading"),
    "density":      ("density_initial",      "density_final",      "density_deactivated_at",      "density_last_reading"),
    "conductivity": ("conductivity_initial", "conductivity_final", "conductivity_deactivated_at", "conductivity_last_reading"),
    "ph":           ("ph_initial",           "ph_final",           "ph_deactivated_at",           "ph_last_reading"),
    "temperature":  ("temperature_initial",  "temperature_final",  "temperature_deactivated_at",  "temperature_last_reading"),
    "turbidity":    ("turbidity_initial",    "turbidity_final",    "turbidity_deactivated_at",    "turbidity_last_reading"),
    "rpm":          ("rpm_initial",          "rpm_final",          "rpm_deactivated_at",          "rpm_last_reading"),
}
