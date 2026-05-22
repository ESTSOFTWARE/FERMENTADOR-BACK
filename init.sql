CREATE DATABASE IF NOT EXISTS sensor_db;
USE sensor_db;

CREATE TABLE roles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)     NOT NULL UNIQUE,
    description VARCHAR(150)    DEFAULT NULL
);

INSERT INTO roles (id, name, description) VALUES
(1, 'admin',      'Acceso total, puede crear cualquier tipo de cuenta'),
(2, 'profesor',   'Puede crear cuentas de estudiante y ver sus usuarios'),
(3, 'estudiante', 'Solo puede ver gráficas, historial, cálculos y reportes'),
(4, 'soporte',    'Soporte tecnico de nich-ká');

CREATE TABLE circuits (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    activation_code         VARCHAR(64)  NOT NULL UNIQUE,
    activated_at            DATETIME     DEFAULT NULL,
    is_active               BOOLEAN      NOT NULL DEFAULT FALSE,
    motor_on                BOOLEAN      NOT NULL DEFAULT FALSE,
    pump_on                 BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_alcohol_on       BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_density_on       BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_conductivity_on  BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_ph_on            BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_temperature_on   BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_turbidity_on     BOOLEAN      NOT NULL DEFAULT FALSE,
    sensor_rpm_on           BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100)  NOT NULL,
    last_name        VARCHAR(100)  NOT NULL,
    password         VARCHAR(255)  NULL DEFAULT NULL,
    email            VARCHAR(150)  NOT NULL UNIQUE,
    role_id          INT           NOT NULL DEFAULT 3,
    profile_image    LONGTEXT      NULL DEFAULT NULL,
    circuit_id       INT           DEFAULT NULL,
    created_by       INT           DEFAULT NULL,
    created_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dial_code        VARCHAR(10)   NULL DEFAULT NULL,
    phone_number     VARCHAR(15)   NULL DEFAULT NULL,
    oauth_google_id  VARCHAR(100)  NULL DEFAULT NULL,
    oauth_github_id  VARCHAR(100)  NULL DEFAULT NULL,
    tour_completed   TINYINT(1)    NOT NULL DEFAULT 0,
    is_active        TINYINT(1)    NOT NULL DEFAULT 1,
    CONSTRAINT fk_user_role    FOREIGN KEY (role_id)    REFERENCES roles(id)    ON DELETE RESTRICT,
    CONSTRAINT fk_user_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id) ON DELETE SET NULL,
    CONSTRAINT fk_user_creator FOREIGN KEY (created_by) REFERENCES users(id)   ON DELETE SET NULL
);

CREATE TABLE efficiency_formula (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(100)    NOT NULL,
    conversion_factor   DOUBLE          NOT NULL DEFAULT 0.51,
    description         TEXT            DEFAULT NULL,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    updated_by          INT             DEFAULT NULL,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_formula_user FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

INSERT INTO efficiency_formula (name, conversion_factor, description, is_active) VALUES
('Fórmula estándar Gay-Lussac', 0.51,
 'eficiencia = (etanol_sensor / (azucar_inicial * factor)) * 100', TRUE);

CREATE TABLE fermentation_sessions (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id       INT      NOT NULL,
    user_id          INT      NOT NULL,
    formula_id       INT      NOT NULL,
    scheduled_start  DATETIME NOT NULL,
    scheduled_end    DATETIME NOT NULL,
    actual_start     DATETIME DEFAULT NULL,
    actual_end       DATETIME DEFAULT NULL,
    status           ENUM('scheduled','running','completed','interrupted') NOT NULL DEFAULT 'scheduled',
    interrupted_by   INT      DEFAULT NULL,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_circuit   FOREIGN KEY (circuit_id)     REFERENCES circuits(id)           ON DELETE CASCADE,
    CONSTRAINT fk_session_user      FOREIGN KEY (user_id)        REFERENCES users(id)              ON DELETE CASCADE,
    CONSTRAINT fk_session_formula   FOREIGN KEY (formula_id)     REFERENCES efficiency_formula(id) ON DELETE RESTRICT,
    CONSTRAINT fk_session_interrupt FOREIGN KEY (interrupted_by) REFERENCES users(id)              ON DELETE SET NULL
);

CREATE TABLE fermentation_reports (
    id                          INT AUTO_INCREMENT PRIMARY KEY,
    session_id                  INT     NOT NULL UNIQUE,
    initial_sugar               DOUBLE  NOT NULL,
    final_sugar                 DOUBLE  DEFAULT NULL,
    ethanol_detected            DOUBLE  DEFAULT NULL,
    theoretical_ethanol         DOUBLE  DEFAULT NULL,
    efficiency                  DOUBLE  DEFAULT NULL,
    alcohol_initial             DOUBLE  DEFAULT NULL,
    alcohol_final               DOUBLE  DEFAULT NULL,
    alcohol_deactivated_at      DATETIME DEFAULT NULL,
    alcohol_last_reading        DOUBLE  DEFAULT NULL,
    density_initial             DOUBLE  DEFAULT NULL,
    density_final               DOUBLE  DEFAULT NULL,
    density_deactivated_at      DATETIME DEFAULT NULL,
    density_last_reading        DOUBLE  DEFAULT NULL,
    conductivity_initial        DOUBLE  DEFAULT NULL,
    conductivity_final          DOUBLE  DEFAULT NULL,
    conductivity_deactivated_at DATETIME DEFAULT NULL,
    conductivity_last_reading   DOUBLE  DEFAULT NULL,
    ph_initial                  DOUBLE  DEFAULT NULL,
    ph_final                    DOUBLE  DEFAULT NULL,
    ph_deactivated_at           DATETIME DEFAULT NULL,
    ph_last_reading             DOUBLE  DEFAULT NULL,
    temperature_initial         DOUBLE  DEFAULT NULL,
    temperature_final           DOUBLE  DEFAULT NULL,
    temperature_deactivated_at  DATETIME DEFAULT NULL,
    temperature_last_reading    DOUBLE  DEFAULT NULL,
    turbidity_initial           DOUBLE  DEFAULT NULL,
    turbidity_final             DOUBLE  DEFAULT NULL,
    turbidity_deactivated_at    DATETIME DEFAULT NULL,
    turbidity_last_reading      DOUBLE  DEFAULT NULL,
    rpm_initial                 DOUBLE  DEFAULT NULL,
    rpm_final                   DOUBLE  DEFAULT NULL,
    rpm_deactivated_at          DATETIME DEFAULT NULL,
    rpm_last_reading            DOUBLE  DEFAULT NULL,
    notes                       TEXT    DEFAULT NULL,
    generated_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE CASCADE
);

CREATE TABLE report_history (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_id   INT     NOT NULL,
    user_id     INT     NOT NULL,
    action      ENUM('generated','downloaded','viewed') NOT NULL DEFAULT 'generated',
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_report FOREIGN KEY (report_id) REFERENCES fermentation_reports(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_user   FOREIGN KEY (user_id)   REFERENCES users(id)                ON DELETE CASCADE
);

CREATE TABLE sensor_events (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    circuit_id   INT     NOT NULL,
    session_id   INT     DEFAULT NULL,
    sensor_type  ENUM('alcohol','density','conductivity','ph','temperature','turbidity','rpm') NOT NULL,
    event_type   ENUM('activated','deactivated') NOT NULL,
    last_reading DOUBLE  DEFAULT NULL,
    triggered_by INT     DEFAULT NULL,
    occurred_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_event_circuit  FOREIGN KEY (circuit_id)   REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_event_session  FOREIGN KEY (session_id)   REFERENCES fermentation_sessions(id) ON DELETE SET NULL,
    CONSTRAINT fk_event_user     FOREIGN KEY (triggered_by) REFERENCES users(id)                 ON DELETE SET NULL
);

CREATE TABLE alcohol_sensor (
    measurement_id        INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id            INT      NOT NULL,
    session_id            INT      DEFAULT NULL,
    timestamp             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alcohol_concentration DOUBLE   NOT NULL,
    CONSTRAINT fk_alcohol_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_alcohol_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE density_sensor (
    measurement_id  INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id      INT      NOT NULL,
    session_id      INT      DEFAULT NULL,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    density         DOUBLE   NOT NULL,
    CONSTRAINT fk_density_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_density_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE conductivity_sensor (
    measurement_id  INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id      INT      NOT NULL,
    session_id      INT      DEFAULT NULL,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conductivity    DOUBLE   NOT NULL,
    CONSTRAINT fk_conductivity_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_conductivity_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE ph_sensor (
    measurement_id  INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id      INT      NOT NULL,
    session_id      INT      DEFAULT NULL,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ph_value        DOUBLE   NOT NULL,
    CONSTRAINT fk_ph_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_ph_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE temperature_sensor (
    measurement_id  INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id      INT      NOT NULL,
    session_id      INT      DEFAULT NULL,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature     DOUBLE   NOT NULL,
    CONSTRAINT fk_temp_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_temp_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE turbidity_sensor (
    measurement_id  INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id      INT      NOT NULL,
    session_id      INT      DEFAULT NULL,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    turbidity       DOUBLE   NOT NULL,
    CONSTRAINT fk_turbidity_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_turbidity_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE motor_rpm_sensor (
    measurement_id  INT AUTO_INCREMENT PRIMARY KEY,
    circuit_id      INT      NOT NULL,
    session_id      INT      DEFAULT NULL,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rpm             DOUBLE   NOT NULL,
    CONSTRAINT fk_rpm_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_rpm_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE notifications (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT     NOT NULL,
    session_id  INT     DEFAULT NULL,
    type        ENUM('fermentation_complete','fermentation_interrupted','high_temperature','sensor_failure','general') NOT NULL DEFAULT 'general',
    message     TEXT    NOT NULL,
    status      ENUM('unread','read') NOT NULL DEFAULT 'unread',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user    FOREIGN KEY (user_id)    REFERENCES users(id)                  ON DELETE CASCADE,
    CONSTRAINT fk_notif_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id)  ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS announcements (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    label        VARCHAR(50)  NOT NULL,
    version      VARCHAR(20)  NOT NULL,
    date         VARCHAR(20)  NOT NULL,
    title        VARCHAR(150) NOT NULL,
    description  TEXT         NOT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_pinned    BOOLEAN      NOT NULL DEFAULT FALSE,
    pinned_until DATETIME     NULL
);

CREATE TABLE classrooms (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    professor_id INT          NOT NULL,
    code         VARCHAR(20)  NOT NULL UNIQUE,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_classroom_professor FOREIGN KEY (professor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE group_members (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    group_id   INT      NOT NULL,
    student_id INT      NOT NULL,
    joined_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_one_group  UNIQUE (student_id),
    CONSTRAINT fk_member_group   FOREIGN KEY (group_id)   REFERENCES classrooms(id) ON DELETE CASCADE,
    CONSTRAINT fk_member_student FOREIGN KEY (student_id) REFERENCES users(id)       ON DELETE CASCADE
);

-- Índices
CREATE INDEX idx_users_circuit            ON users(circuit_id);
CREATE INDEX idx_users_created_by         ON users(created_by);
CREATE INDEX idx_users_oauth_google       ON users(oauth_google_id);
CREATE INDEX idx_announcements_created_at ON announcements(created_at);
CREATE INDEX idx_users_oauth_github       ON users(oauth_github_id);
CREATE INDEX idx_alcohol_session_time      ON alcohol_sensor(session_id, timestamp);
CREATE INDEX idx_density_session_time      ON density_sensor(session_id, timestamp);
CREATE INDEX idx_conductivity_session_time ON conductivity_sensor(session_id, timestamp);
CREATE INDEX idx_ph_session_time           ON ph_sensor(session_id, timestamp);
CREATE INDEX idx_temperature_session_time  ON temperature_sensor(session_id, timestamp);
CREATE INDEX idx_turbidity_session_time    ON turbidity_sensor(session_id, timestamp);
CREATE INDEX idx_rpm_session_time          ON motor_rpm_sensor(session_id, timestamp);
CREATE INDEX idx_sessions_circuit          ON fermentation_sessions(circuit_id, status);
CREATE INDEX idx_sessions_user             ON fermentation_sessions(user_id, status);
CREATE INDEX idx_notifications_user        ON notifications(user_id, status);
CREATE INDEX idx_sensor_events_session     ON sensor_events(session_id, sensor_type, occurred_at);
CREATE INDEX idx_sensor_events_circuit     ON sensor_events(circuit_id, occurred_at);
CREATE INDEX idx_report_history_report     ON report_history(report_id, occurred_at);
CREATE INDEX idx_report_history_user       ON report_history(user_id, occurred_at);