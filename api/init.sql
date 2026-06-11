-- ─────────────────────────────────────────────────────────────────────────────
-- Esquema PostgreSQL — sensor_db
-- La base de datos la crea el contenedor (POSTGRES_DB); aquí solo el esquema.
-- ─────────────────────────────────────────────────────────────────────────────

-- Trigger genérico para updated_at (PostgreSQL no tiene ON UPDATE CURRENT_TIMESTAMP)
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE,
    description VARCHAR(150) DEFAULT NULL
);

INSERT INTO roles (id, name, description) VALUES
(1, 'admin',      'Acceso total, puede crear cualquier tipo de cuenta'),
(2, 'profesor',   'Puede crear cuentas de estudiante y ver sus usuarios'),
(3, 'estudiante', 'Solo puede ver gráficas, historial, cálculos y reportes'),
(4, 'soporte',    'Soporte tecnico de nich-ká');
-- Reajustar la secuencia tras insertar ids explícitos
SELECT setval(pg_get_serial_sequence('roles', 'id'), (SELECT MAX(id) FROM roles));

CREATE TABLE circuits (
    id                      SERIAL PRIMARY KEY,
    activation_code         VARCHAR(64) NOT NULL UNIQUE,
    activated_at            TIMESTAMP   DEFAULT NULL,
    is_active               BOOLEAN     NOT NULL DEFAULT FALSE,
    motor_on                BOOLEAN     NOT NULL DEFAULT FALSE,
    pump_on                 BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_alcohol_on       BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_density_on       BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_conductivity_on  BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_ph_on            BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_temperature_on   BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_turbidity_on     BOOLEAN     NOT NULL DEFAULT FALSE,
    sensor_rpm_on           BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    password                VARCHAR(255) DEFAULT NULL,
    email                   VARCHAR(150) NOT NULL UNIQUE,
    role_id                 INT          NOT NULL DEFAULT 3,
    profile_image           TEXT         DEFAULT NULL,
    circuit_id              INT          DEFAULT NULL,
    created_by              INT          DEFAULT NULL,
    created_at              TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dial_code               VARCHAR(10)  DEFAULT NULL,
    phone_number            VARCHAR(15)  DEFAULT NULL,
    oauth_google_id         VARCHAR(100) DEFAULT NULL,
    oauth_github_id         VARCHAR(100) DEFAULT NULL,
    tour_completed          BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active               BOOLEAN      NOT NULL DEFAULT TRUE,
    warning_email_sent_at   TIMESTAMP    DEFAULT NULL,
    reactivated_at          TIMESTAMP    DEFAULT NULL,
    last_oauth_login_at     TIMESTAMP    DEFAULT NULL,
    active_session_id       VARCHAR(64)  DEFAULT NULL,
    CONSTRAINT fk_user_role    FOREIGN KEY (role_id)    REFERENCES roles(id)    ON DELETE RESTRICT,
    CONSTRAINT fk_user_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id) ON DELETE SET NULL,
    CONSTRAINT fk_user_creator FOREIGN KEY (created_by) REFERENCES users(id)    ON DELETE SET NULL
);

CREATE TABLE efficiency_formula (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100)     NOT NULL,
    conversion_factor   DOUBLE PRECISION NOT NULL DEFAULT 0.51,
    description         TEXT             DEFAULT NULL,
    is_active           BOOLEAN          NOT NULL DEFAULT TRUE,
    updated_by          INT              DEFAULT NULL,
    updated_at          TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at          TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_formula_user FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);
CREATE TRIGGER trg_formula_updated BEFORE UPDATE ON efficiency_formula
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

INSERT INTO efficiency_formula (name, conversion_factor, description, is_active) VALUES
('Fórmula estándar Gay-Lussac', 0.51,
 'eficiencia = (etanol_sensor / (azucar_inicial * factor)) * 100', TRUE);

CREATE TABLE fermentation_sessions (
    id               SERIAL PRIMARY KEY,
    circuit_id       INT       NOT NULL,
    user_id          INT       NOT NULL,
    formula_id       INT       NOT NULL,
    scheduled_start  TIMESTAMP NOT NULL,
    scheduled_end    TIMESTAMP NOT NULL,
    actual_start     TIMESTAMP DEFAULT NULL,
    actual_end       TIMESTAMP DEFAULT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                       CHECK (status IN ('scheduled','running','completed','interrupted')),
    interrupted_by   INT       DEFAULT NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_circuit   FOREIGN KEY (circuit_id)     REFERENCES circuits(id)           ON DELETE CASCADE,
    CONSTRAINT fk_session_user      FOREIGN KEY (user_id)        REFERENCES users(id)              ON DELETE CASCADE,
    CONSTRAINT fk_session_formula   FOREIGN KEY (formula_id)     REFERENCES efficiency_formula(id) ON DELETE RESTRICT,
    CONSTRAINT fk_session_interrupt FOREIGN KEY (interrupted_by) REFERENCES users(id)              ON DELETE SET NULL
);

CREATE TABLE fermentation_reports (
    id                          SERIAL PRIMARY KEY,
    session_id                  INT     NOT NULL UNIQUE,
    initial_sugar               DOUBLE PRECISION NOT NULL,
    final_sugar                 DOUBLE PRECISION DEFAULT NULL,
    ethanol_detected            DOUBLE PRECISION DEFAULT NULL,
    theoretical_ethanol         DOUBLE PRECISION DEFAULT NULL,
    efficiency                  DOUBLE PRECISION DEFAULT NULL,
    alcohol_initial             DOUBLE PRECISION DEFAULT NULL,
    alcohol_final               DOUBLE PRECISION DEFAULT NULL,
    alcohol_deactivated_at      TIMESTAMP        DEFAULT NULL,
    alcohol_last_reading        DOUBLE PRECISION DEFAULT NULL,
    density_initial             DOUBLE PRECISION DEFAULT NULL,
    density_final               DOUBLE PRECISION DEFAULT NULL,
    density_deactivated_at      TIMESTAMP        DEFAULT NULL,
    density_last_reading        DOUBLE PRECISION DEFAULT NULL,
    conductivity_initial        DOUBLE PRECISION DEFAULT NULL,
    conductivity_final          DOUBLE PRECISION DEFAULT NULL,
    conductivity_deactivated_at TIMESTAMP        DEFAULT NULL,
    conductivity_last_reading   DOUBLE PRECISION DEFAULT NULL,
    ph_initial                  DOUBLE PRECISION DEFAULT NULL,
    ph_final                    DOUBLE PRECISION DEFAULT NULL,
    ph_deactivated_at           TIMESTAMP        DEFAULT NULL,
    ph_last_reading             DOUBLE PRECISION DEFAULT NULL,
    temperature_initial         DOUBLE PRECISION DEFAULT NULL,
    temperature_final           DOUBLE PRECISION DEFAULT NULL,
    temperature_deactivated_at  TIMESTAMP        DEFAULT NULL,
    temperature_last_reading    DOUBLE PRECISION DEFAULT NULL,
    turbidity_initial           DOUBLE PRECISION DEFAULT NULL,
    turbidity_final             DOUBLE PRECISION DEFAULT NULL,
    turbidity_deactivated_at    TIMESTAMP        DEFAULT NULL,
    turbidity_last_reading      DOUBLE PRECISION DEFAULT NULL,
    rpm_initial                 DOUBLE PRECISION DEFAULT NULL,
    rpm_final                   DOUBLE PRECISION DEFAULT NULL,
    rpm_deactivated_at          TIMESTAMP        DEFAULT NULL,
    rpm_last_reading            DOUBLE PRECISION DEFAULT NULL,
    notes                       TEXT             DEFAULT NULL,
    generated_at                TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE CASCADE
);

CREATE TABLE report_history (
    id          BIGSERIAL PRIMARY KEY,
    report_id   INT       NOT NULL,
    user_id     INT       NOT NULL,
    action      VARCHAR(20) NOT NULL DEFAULT 'generated'
                  CHECK (action IN ('generated','downloaded','viewed')),
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_report FOREIGN KEY (report_id) REFERENCES fermentation_reports(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_user   FOREIGN KEY (user_id)   REFERENCES users(id)                ON DELETE CASCADE
);

CREATE TABLE sensor_events (
    id           BIGSERIAL PRIMARY KEY,
    circuit_id   INT       NOT NULL,
    session_id   INT       DEFAULT NULL,
    sensor_type  VARCHAR(20) NOT NULL
                   CHECK (sensor_type IN ('alcohol','density','conductivity','ph','temperature','turbidity','rpm')),
    event_type   VARCHAR(20) NOT NULL
                   CHECK (event_type IN ('activated','deactivated')),
    last_reading DOUBLE PRECISION DEFAULT NULL,
    triggered_by INT       DEFAULT NULL,
    occurred_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_event_circuit  FOREIGN KEY (circuit_id)   REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_event_session  FOREIGN KEY (session_id)   REFERENCES fermentation_sessions(id) ON DELETE SET NULL,
    CONSTRAINT fk_event_user     FOREIGN KEY (triggered_by) REFERENCES users(id)                 ON DELETE SET NULL
);

CREATE TABLE alcohol_sensor (
    measurement_id        SERIAL PRIMARY KEY,
    circuit_id            INT       NOT NULL,
    session_id            INT       DEFAULT NULL,
    timestamp             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alcohol_concentration DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_alcohol_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_alcohol_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE density_sensor (
    measurement_id  SERIAL PRIMARY KEY,
    circuit_id      INT       NOT NULL,
    session_id      INT       DEFAULT NULL,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    density         DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_density_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_density_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE conductivity_sensor (
    measurement_id  SERIAL PRIMARY KEY,
    circuit_id      INT       NOT NULL,
    session_id      INT       DEFAULT NULL,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conductivity    DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_conductivity_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_conductivity_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE ph_sensor (
    measurement_id  SERIAL PRIMARY KEY,
    circuit_id      INT       NOT NULL,
    session_id      INT       DEFAULT NULL,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ph_value        DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_ph_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_ph_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE temperature_sensor (
    measurement_id  SERIAL PRIMARY KEY,
    circuit_id      INT       NOT NULL,
    session_id      INT       DEFAULT NULL,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature     DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_temp_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_temp_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE turbidity_sensor (
    measurement_id  SERIAL PRIMARY KEY,
    circuit_id      INT       NOT NULL,
    session_id      INT       DEFAULT NULL,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    turbidity       DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_turbidity_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_turbidity_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE motor_rpm_sensor (
    measurement_id  SERIAL PRIMARY KEY,
    circuit_id      INT       NOT NULL,
    session_id      INT       DEFAULT NULL,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rpm             DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_rpm_circuit FOREIGN KEY (circuit_id) REFERENCES circuits(id)              ON DELETE CASCADE,
    CONSTRAINT fk_rpm_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE notifications (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INT       NOT NULL,
    session_id  INT       DEFAULT NULL,
    type        VARCHAR(50) NOT NULL DEFAULT 'general'
                  CHECK (type IN ('fermentation_complete','fermentation_interrupted','high_temperature',
                                  'sensor_failure','new_announcement','member_added','member_removed',
                                  'user_registered','experiment_complete','general')),
    message     TEXT      NOT NULL,
    status      VARCHAR(10) NOT NULL DEFAULT 'unread'
                  CHECK (status IN ('unread','read')),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user    FOREIGN KEY (user_id)    REFERENCES users(id)                 ON DELETE CASCADE,
    CONSTRAINT fk_notif_session FOREIGN KEY (session_id) REFERENCES fermentation_sessions(id) ON DELETE SET NULL
);

CREATE TABLE announcements (
    id           SERIAL PRIMARY KEY,
    label        VARCHAR(50)  NOT NULL,
    version      VARCHAR(20)  NOT NULL,
    date         VARCHAR(20)  NOT NULL,
    title        VARCHAR(150) NOT NULL,
    description  TEXT         NOT NULL,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_pinned    BOOLEAN      NOT NULL DEFAULT FALSE,
    pinned_until TIMESTAMP    NULL
);

CREATE TABLE classrooms (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    subject      VARCHAR(100) NOT NULL,
    cover_image  TEXT         DEFAULT NULL,
    professor_id INT          NOT NULL,
    code         VARCHAR(20)  NOT NULL UNIQUE,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_classroom_professor FOREIGN KEY (professor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE group_members (
    id         SERIAL PRIMARY KEY,
    group_id   INT       NOT NULL,
    student_id INT       NOT NULL,
    joined_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_one_group  UNIQUE (student_id),
    CONSTRAINT fk_member_group   FOREIGN KEY (group_id)   REFERENCES classrooms(id) ON DELETE CASCADE,
    CONSTRAINT fk_member_student FOREIGN KEY (student_id) REFERENCES users(id)       ON DELETE CASCADE
);

CREATE TABLE password_reset_codes (
    id         SERIAL PRIMARY KEY,
    user_id    INT        NOT NULL,
    code       VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP  NOT NULL,
    used       BOOLEAN    NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reset_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(150)     NOT NULL,
    description TEXT             NOT NULL,
    price       DOUBLE PRECISION NOT NULL,
    sku         VARCHAR(50)      NOT NULL UNIQUE,
    stock       INT              NOT NULL DEFAULT 0,
    rating      INT              NOT NULL DEFAULT 1,
    created_at  TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_product_price  CHECK (price > 0),
    CONSTRAINT chk_product_stock  CHECK (stock >= 0),
    CONSTRAINT chk_product_rating CHECK (rating >= 1 AND rating <= 5)
);

CREATE TABLE subscriptions (
    id                      SERIAL PRIMARY KEY,
    user_id                 INT          NOT NULL UNIQUE,
    stripe_customer_id      VARCHAR(100) UNIQUE,
    stripe_subscription_id  VARCHAR(100) UNIQUE,
    paypal_subscription_id  VARCHAR(100) UNIQUE,
    payment_provider        VARCHAR(20)  NOT NULL DEFAULT 'stripe'
                              CHECK (payment_provider IN ('stripe','paypal')),
    plan                    VARCHAR(20)  NOT NULL
                              CHECK (plan IN ('starter','academic','enterprise')),
    billing_cycle           VARCHAR(20)  NOT NULL DEFAULT 'monthly'
                              CHECK (billing_cycle IN ('monthly','annual')),
    status                  VARCHAR(20)  NOT NULL DEFAULT 'incomplete'
                              CHECK (status IN ('active','past_due','canceled','incomplete')),
    current_period_end      TIMESTAMP    NULL,
    cancel_at_period_end    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sub_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TRIGGER trg_subscriptions_updated BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Chat ──────────────────────────────────────────────────────────────────────

CREATE TABLE chat_conversations (
    id          SERIAL PRIMARY KEY,
    type        VARCHAR(20)   NOT NULL CHECK (type IN ('personal','group')),
    name        VARCHAR(150)  NULL,
    description VARCHAR(500)  NULL,
    avatar      VARCHAR(2048) NULL,
    created_by  INT           NOT NULL,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_conv_creator FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE TRIGGER trg_chat_conv_updated BEFORE UPDATE ON chat_conversations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE chat_conversation_members (
    id              SERIAL PRIMARY KEY,
    conversation_id INT       NOT NULL,
    user_id         INT       NOT NULL,
    joined_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_read_at    TIMESTAMP NULL,
    CONSTRAINT uq_conversation_member UNIQUE (conversation_id, user_id),
    CONSTRAINT fk_chat_member_conv FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_member_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE chat_messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INT       NOT NULL,
    sender_id       INT       NOT NULL,
    content         TEXT      NULL,
    reply_to_id     INT       NULL,
    priority        VARCHAR(20) NOT NULL DEFAULT 'normal'
                      CHECK (priority IN ('normal','important','urgent')),
    pinned          BOOLEAN   NOT NULL DEFAULT FALSE,
    edited          BOOLEAN   NOT NULL DEFAULT FALSE,
    edited_at       TIMESTAMP NULL,
    deleted         BOOLEAN   NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_msg_conv   FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_msg_sender FOREIGN KEY (sender_id)       REFERENCES users(id),
    CONSTRAINT fk_chat_msg_reply  FOREIGN KEY (reply_to_id)     REFERENCES chat_messages(id)
);

CREATE TABLE chat_message_attachments (
    id         SERIAL PRIMARY KEY,
    message_id INT          NOT NULL,
    type       VARCHAR(20)  NOT NULL CHECK (type IN ('image','video','document','file')),
    name       VARCHAR(255) NOT NULL,
    url        VARCHAR(2048) NOT NULL,
    size       INT          NOT NULL DEFAULT 0,
    CONSTRAINT fk_chat_att_msg FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE
);

CREATE TABLE chat_message_reactions (
    id         SERIAL PRIMARY KEY,
    message_id INT         NOT NULL,
    user_id    INT         NOT NULL,
    emoji      VARCHAR(16) NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_message_user_emoji UNIQUE (message_id, user_id, emoji),
    CONSTRAINT fk_chat_react_msg  FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_react_user FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- ── Chat de soporte (admin ↔ soporte) ──────────────────────────────────────────

CREATE TABLE support_conversations (
    id                   SERIAL PRIMARY KEY,
    admin_id             INT       NOT NULL UNIQUE,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_read_admin_at   TIMESTAMP NULL,
    last_read_support_at TIMESTAMP NULL,
    CONSTRAINT fk_support_conv_admin FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TRIGGER trg_support_conv_updated BEFORE UPDATE ON support_conversations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE support_messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INT       NOT NULL,
    sender_id       INT       NOT NULL,
    sender_role     VARCHAR(20) NOT NULL CHECK (sender_role IN ('admin','soporte')),
    content         TEXT      NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_support_msg_conv   FOREIGN KEY (conversation_id) REFERENCES support_conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_support_msg_sender FOREIGN KEY (sender_id)       REFERENCES users(id)
);

CREATE TABLE support_message_attachments (
    id         SERIAL PRIMARY KEY,
    message_id INT          NOT NULL,
    type       VARCHAR(20)  NOT NULL CHECK (type IN ('image','video','document','file')),
    name       VARCHAR(255) NOT NULL,
    url        VARCHAR(2048) NOT NULL,
    size       INT          NOT NULL DEFAULT 0,
    CONSTRAINT fk_support_att_msg FOREIGN KEY (message_id) REFERENCES support_messages(id) ON DELETE CASCADE
);

-- ── Índices ────────────────────────────────────────────────────────────────────
CREATE INDEX idx_support_msg_conv_created  ON support_messages(conversation_id, created_at);
CREATE INDEX idx_users_circuit             ON users(circuit_id);
CREATE INDEX idx_users_created_by          ON users(created_by);
CREATE INDEX idx_users_oauth_google        ON users(oauth_google_id);
CREATE INDEX idx_users_oauth_github        ON users(oauth_github_id);
CREATE INDEX idx_announcements_created_at  ON announcements(created_at);
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
CREATE INDEX idx_chat_msg_conv_created     ON chat_messages(conversation_id, created_at);
