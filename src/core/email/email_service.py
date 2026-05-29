import logging

import resend

from src.core.config import settings

logger = logging.getLogger(__name__)


def _welcome_html(name: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Bienvenido a Nich-Ká</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
        rel="stylesheet"/>
  <style>
    @media only screen and (max-width: 600px) {{
      .email-wrapper {{ padding: 24px 12px !important; }}
      .email-body {{ padding: 24px 20px !important; }}
      .email-header {{ padding: 28px 20px 22px !important; }}
      .email-title {{ font-size: 19px !important; }}
      .btn-cta {{ display: block !important; text-align: center !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0B;font-family:'Poppins',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" class="email-wrapper"
         style="background-color:#0A0A0B;padding:48px 16px;">
    <tr>
      <td align="center">
        <table cellpadding="0" cellspacing="0"
               style="max-width:560px;width:100%;">

          <!-- Logo + nombre -->
          <tr>
            <td align="left" style="padding-bottom:32px;">
              <a href="https://www.nich-ka.space/" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="vertical-align:middle;padding-right:10px;">
                      <img src="https://www.nich-ka.space/assets/logo.svg"
                           alt="Nich-Ká" width="40" height="40"
                           style="display:block;border:0;width:40px;height:40px;"/>
                    </td>
                    <td style="vertical-align:middle;">
                      <span style="color:#f4f4f5;font-size:20px;font-weight:700;
                                   letter-spacing:-0.5px;font-family:'Poppins',sans-serif;">
                        Nich-Ká
                      </span>
                    </td>
                  </tr>
                </table>
              </a>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background-color:#111113;border:1px solid #2a2a2d;
                        border-radius:14px;overflow:hidden;">

              <!-- Header -->
              <tr>
                <td class="email-header"
                    style="padding:36px 40px 28px;border-bottom:1px solid #2a2a2d;">
                  <h1 class="email-title"
                      style="margin:0 0 8px;color:#f4f4f5;font-size:22px;font-weight:600;
                              letter-spacing:-0.3px;font-family:'Poppins',sans-serif;">
                    Bienvenido, {name} 👋
                  </h1>
                  <p style="margin:0;color:#a1a1aa;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Tu cuenta en <strong style="color:#f4f4f5;">Nich-Ká</strong>
                    fue creada exitosamente.
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td class="email-body" style="padding:32px 40px;">

                  <!-- Features -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:middle;padding-right:10px;width:24px;">
                              <img src="https://img.icons8.com/color/20/combo-chart--v1.png"
                                   width="18" height="18" alt=""
                                   style="display:block;border:0;width:18px;height:18px;"/>
                            </td>
                            <td style="vertical-align:middle;">
                              <span style="color:#a1a1aa;font-size:13px;
                                           font-family:'Poppins',sans-serif;">
                                Monitoreo de sensores en tiempo real
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:middle;padding-right:10px;width:24px;">
                              <img src="https://img.icons8.com/color/20/thermometer.png"
                                   width="18" height="18" alt=""
                                   style="display:block;border:0;width:18px;height:18px;"/>
                            </td>
                            <td style="vertical-align:middle;">
                              <span style="color:#a1a1aa;font-size:13px;
                                           font-family:'Poppins',sans-serif;">
                                Alertas de temperatura y parámetros críticos
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:middle;padding-right:10px;width:24px;">
                              <img src="https://img.icons8.com/color/20/activity-feed.png"
                                   width="18" height="18" alt=""
                                   style="display:block;border:0;width:18px;height:18px;"/>
                            </td>
                            <td style="vertical-align:middle;">
                              <span style="color:#a1a1aa;font-size:13px;
                                           font-family:'Poppins',sans-serif;">
                                Reportes y análisis de sesiones de fermentación
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- Aviso activación -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="background-color:rgba(34,197,94,0.06);
                                  border:1px solid rgba(34,197,94,0.2);
                                  border-radius:10px;padding:16px 18px;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:10px;
                                        padding-top:2px;width:22px;">
                              <img src="https://img.icons8.com/color/20/info.png"
                                   width="16" height="16" alt=""
                                   style="display:block;border:0;width:16px;height:16px;"/>
                            </td>
                            <td>
                              <p style="margin:0;color:#a1a1aa;font-size:13px;line-height:1.7;
                                         font-family:'Poppins',sans-serif;">
                                No olvides vincular tu
                                <strong style="color:#4ade80;">código de activación</strong>
                                en el apartado de tu
                                <strong style="color:#f4f4f5;">Perfil</strong>.
                                Tienes <strong style="color:#f4f4f5;">30 días</strong>
                                para hacerlo antes de que tu cuenta sea desactivada.
                              </p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- CTA -->
                  <table cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                      <td>
                        <a href="{settings.FRONTEND_URL}" class="btn-cta"
                           style="display:inline-block;background-color:#ffffff;
                                  color:#0A0A0B;text-decoration:none;padding:12px 28px;
                                  border-radius:8px;font-size:14px;font-weight:600;
                                  font-family:'Poppins',sans-serif;letter-spacing:-0.1px;">
                          Ir a la plataforma →
                        </a>
                      </td>
                    </tr>
                  </table>

                </td>
              </tr>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:28px 0;text-align:center;">
              <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                          font-family:'Poppins',sans-serif;">
                Este correo fue enviado automáticamente por Nich-Ká.<br/>
                Si no creaste esta cuenta, puedes ignorar este mensaje.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_welcome_email(to_email: str, name: str) -> None:
    if not settings.RESEND_API_KEY or not settings.MAIL_FROM:
        logger.warning("[Email] RESEND_API_KEY o MAIL_FROM no configurados, omitiendo envío")
        return

    try:
        resend.api_key = settings.RESEND_API_KEY
        from_address = (
            f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            if settings.MAIL_FROM_NAME
            else settings.MAIL_FROM
        )
        params: resend.Emails.SendParams = {
            "from": from_address,
            "to": [to_email],
            "subject": f"¡Bienvenido a Nich-ká, {name}!",
            "html": _welcome_html(name),
        }
        resend.Emails.send(params)
        logger.info(f"[Email] Correo de bienvenida enviado a {to_email}")
    except Exception as e:
        logger.error(f"[Email] Error al enviar correo de bienvenida a {to_email}: {e}")


def _warning_email_html(name: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Tu cuenta está próxima a desactivarse - Nich-Ká</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
        rel="stylesheet"/>
  <style>
    @media only screen and (max-width: 600px) {{
      .email-wrapper {{ padding: 24px 12px !important; }}
      .email-body {{ padding: 24px 20px !important; }}
      .email-header {{ padding: 28px 20px 22px !important; }}
      .email-title {{ font-size: 19px !important; }}
      .warning-box {{ padding: 16px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0B;font-family:'Poppins',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" class="email-wrapper"
         style="background-color:#0A0A0B;padding:48px 16px;">
    <tr>
      <td align="center">
        <table cellpadding="0" cellspacing="0"
               style="max-width:560px;width:100%;">

          <!-- Logo + nombre -->
          <tr>
            <td align="left" style="padding-bottom:32px;">
              <a href="https://www.nich-ka.space/" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="vertical-align:middle;padding-right:10px;">
                      <img src="https://www.nich-ka.space/assets/logo.svg"
                           alt="Nich-Ká" width="40" height="40"
                           style="display:block;border:0;width:40px;height:40px;"/>
                    </td>
                    <td style="vertical-align:middle;">
                      <span style="color:#f4f4f5;font-size:20px;font-weight:700;
                                   letter-spacing:-0.5px;font-family:'Poppins',sans-serif;">
                        Nich-Ká
                      </span>
                    </td>
                  </tr>
                </table>
              </a>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background-color:#111113;border:1px solid #2a2a2d;
                        border-radius:14px;overflow:hidden;">

              <!-- Header -->
              <tr>
                <td class="email-header"
                    style="padding:36px 40px 28px;border-bottom:1px solid #2a2a2d;">
                  <h1 class="email-title"
                      style="margin:0 0 8px;color:#fbbf24;font-size:22px;font-weight:600;
                              letter-spacing:-0.3px;font-family:'Poppins',sans-serif;">
                    Atención, {name} ⏰
                  </h1>
                  <p style="margin:0;color:#a1a1aa;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Tu cuenta será desactivada en <strong style="color:#fbbf24;">2 días</strong>
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td class="email-body" style="padding:32px 40px;">

                  <!-- Advertencia -->
                  <div class="warning-box"
                       style="background-color:#3f2f2f;border-left:4px solid #fbbf24;
                               border-radius:4px;padding:20px;margin-bottom:28px;">
                    <p style="margin:0 0 8px;color:#fbbf24;font-size:14px;font-weight:600;
                              font-family:'Poppins',sans-serif;">
                      ⚠️ ACCIÓN REQUERIDA
                    </p>
                    <p style="margin:0;color:#e4e4e7;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                      Tu cuenta no tiene un circuito vinculado. Si no activas tu código de activación
                      en los próximos 2 días, tu cuenta será desactivada temporalmente.
                    </p>
                  </div>

                  <!-- Pasos -->
                  <p style="margin:0 0 16px;color:#f4f4f5;font-size:14px;font-weight:600;
                              font-family:'Poppins',sans-serif;">
                    ¿Qué debes hacer?
                  </p>

                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#fbbf24;font-size:18px;font-weight:700;">1</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Ingresa a tu cuenta en <strong style="color:#f4f4f5;">Nich-Ká</strong>
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#fbbf24;font-size:18px;font-weight:700;">2</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Registra tu código de activación del circuito
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#fbbf24;font-size:18px;font-weight:700;">3</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Disfruta de todas las funcionalidades de Nich-Ká
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- CTA Button -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td align="center">
                        <a href="https://www.nich-ka.space/"
                           style="display:inline-block;background-color:#fbbf24;
                                  color:#000;text-decoration:none;padding:11px 24px;
                                  border-radius:8px;font-size:14px;font-weight:600;
                                  font-family:'Poppins',sans-serif;
                                  border:0;cursor:pointer;">
                          Activar circuito ahora
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Info adicional -->
                  <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                              font-family:'Poppins',sans-serif;text-align:center;">
                    Si tienes dudas, contacta a nuestro equipo de soporte.
                  </p>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="padding:28px 40px;border-top:1px solid #2a2a2d;text-align:center;">
                  <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Este correo fue enviado automáticamente por Nich-Ká.
                  </p>
                </td>
              </tr>

            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_warning_email(to_email: str, name: str) -> None:
    if not settings.RESEND_API_KEY or not settings.MAIL_FROM:
        logger.warning("[Email] RESEND_API_KEY o MAIL_FROM no configurados, omitiendo envío")
        return

    try:
        resend.api_key = settings.RESEND_API_KEY
        from_address = (
            f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            if settings.MAIL_FROM_NAME
            else settings.MAIL_FROM
        )
        params: resend.Emails.SendParams = {
            "from": from_address,
            "to": [to_email],
            "subject": "Tu cuenta será desactivada en 2 días - Nich-Ká",
            "html": _warning_email_html(name),
        }
        resend.Emails.send(params)
        logger.info(f"[Email] Correo de advertencia enviado a {to_email}")
    except Exception as e:
        logger.error(f"[Email] Error al enviar correo de advertencia a {to_email}: {e}")


def _reactivation_email_html(name: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Tu cuenta ha sido reactivada - Nich-Ká</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
        rel="stylesheet"/>
  <style>
    @media only screen and (max-width: 600px) {{
      .email-wrapper {{ padding: 24px 12px !important; }}
      .email-body {{ padding: 24px 20px !important; }}
      .email-header {{ padding: 28px 20px 22px !important; }}
      .email-title {{ font-size: 19px !important; }}
      .info-box {{ padding: 16px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0B;font-family:'Poppins',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" class="email-wrapper"
         style="background-color:#0A0A0B;padding:48px 16px;">
    <tr>
      <td align="center">
        <table cellpadding="0" cellspacing="0"
               style="max-width:560px;width:100%;">

          <!-- Logo + nombre -->
          <tr>
            <td align="left" style="padding-bottom:32px;">
              <a href="https://www.nich-ka.space/" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="vertical-align:middle;padding-right:10px;">
                      <img src="https://www.nich-ka.space/assets/logo.svg"
                           alt="Nich-Ká" width="40" height="40"
                           style="display:block;border:0;width:40px;height:40px;"/>
                    </td>
                    <td style="vertical-align:middle;">
                      <span style="color:#f4f4f5;font-size:20px;font-weight:700;
                                   letter-spacing:-0.5px;font-family:'Poppins',sans-serif;">
                        Nich-Ká
                      </span>
                    </td>
                  </tr>
                </table>
              </a>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background-color:#111113;border:1px solid #2a2a2d;
                        border-radius:14px;overflow:hidden;">

              <!-- Header -->
              <tr>
                <td class="email-header"
                    style="padding:36px 40px 28px;border-bottom:1px solid #2a2a2d;">
                  <h1 class="email-title"
                      style="margin:0 0 8px;color:#10b981;font-size:22px;font-weight:600;
                              letter-spacing:-0.3px;font-family:'Poppins',sans-serif;">
                    ¡Bienvenido de vuelta, {name}! 👋
                  </h1>
                  <p style="margin:0;color:#a1a1aa;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Tu cuenta fue reactivada exitosamente.
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td class="email-body" style="padding:32px 40px;">

                  <!-- Info importante -->
                  <div class="info-box"
                       style="background-color:#2f3f2f;border-left:4px solid #10b981;
                               border-radius:4px;padding:20px;margin-bottom:28px;">
                    <p style="margin:0 0 8px;color:#10b981;font-size:14px;font-weight:600;
                              font-family:'Poppins',sans-serif;">
                      ⏱️ INFORMACIÓN IMPORTANTE
                    </p>
                    <p style="margin:0;color:#e4e4e7;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                      Dispones de <strong style="color:#10b981;">5 días</strong> para ingresar tu código
                      de activación. Si no lo haces, tu cuenta será desactivada nuevamente.
                    </p>
                  </div>

                  <!-- Pasos -->
                  <p style="margin:0 0 16px;color:#f4f4f5;font-size:14px;font-weight:600;
                              font-family:'Poppins',sans-serif;">
                    ¿Qué debes hacer?
                  </p>

                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#10b981;font-size:18px;font-weight:700;">1</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Abre la aplicación de Nich-Ká
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#10b981;font-size:18px;font-weight:700;">2</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Ve a la sección de "Perfil"
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;border-bottom:1px solid #2a2a2d;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#10b981;font-size:18px;font-weight:700;">3</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Ingresa tu código de activación
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:12px;width:24px;
                                       padding-top:2px;">
                              <span style="color:#10b981;font-size:18px;font-weight:700;">4</span>
                            </td>
                            <td style="vertical-align:top;">
                              <span style="color:#a1a1aa;font-size:13px;line-height:1.5;
                                           font-family:'Poppins',sans-serif;">
                                Disfruta nuevamente de todas nuestras funcionalidades
                              </span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- CTA Button -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td align="center">
                        <a href="https://www.nich-ka.space/"
                           style="display:inline-block;background-color:#10b981;
                                  color:#fff;text-decoration:none;padding:11px 24px;
                                  border-radius:8px;font-size:14px;font-weight:600;
                                  font-family:'Poppins',sans-serif;
                                  border:0;cursor:pointer;">
                          Activar circuito ahora
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Info adicional -->
                  <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                              font-family:'Poppins',sans-serif;text-align:center;">
                    ¿Preguntas? Nuestro equipo de soporte está aquí para ayudarte.
                  </p>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="padding:28px 40px;border-top:1px solid #2a2a2d;text-align:center;">
                  <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Este correo fue enviado automáticamente por Nich-Ká.
                  </p>
                </td>
              </tr>

            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_reactivation_email(to_email: str, name: str) -> None:
    if not settings.RESEND_API_KEY or not settings.MAIL_FROM:
        logger.warning("[Email] RESEND_API_KEY o MAIL_FROM no configurados, omitiendo envío")
        return

    try:
        resend.api_key = settings.RESEND_API_KEY
        from_address = (
            f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            if settings.MAIL_FROM_NAME
            else settings.MAIL_FROM
        )
        params: resend.Emails.SendParams = {
            "from": from_address,
            "to": [to_email],
            "subject": "Tu cuenta ha sido reactivada - Nich-Ká",
            "html": _reactivation_email_html(name),
        }
        resend.Emails.send(params)
        logger.info(f"[Email] Correo de reactivación enviado a {to_email}")
    except Exception as e:
        logger.error(f"[Email] Error al enviar correo de reactivación a {to_email}: {e}")


def _reset_password_html(name: str, code: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Recupera tu contraseña - Nich-Ká</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
        rel="stylesheet"/>
  <style>
    @media only screen and (max-width: 600px) {{
      .email-wrapper {{ padding: 24px 12px !important; }}
      .email-header  {{ padding: 28px 20px 22px !important; }}
      .email-body    {{ padding: 24px 20px !important; }}
      .email-title   {{ font-size: 19px !important; }}
      .code-box      {{ font-size: 32px !important; letter-spacing: 10px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0B;font-family:'Poppins',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" class="email-wrapper"
         style="background-color:#0A0A0B;padding:48px 16px;">
    <tr>
      <td align="center">
        <table cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

          <!-- Logo -->
          <tr>
            <td align="left" style="padding-bottom:32px;">
              <a href="https://www.nich-ka.space/" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="vertical-align:middle;padding-right:10px;">
                      <img src="https://www.nich-ka.space/assets/logo.svg"
                           alt="Nich-Ká" width="40" height="40"
                           style="display:block;border:0;width:40px;height:40px;"/>
                    </td>
                    <td style="vertical-align:middle;">
                      <span style="color:#f4f4f5;font-size:20px;font-weight:700;
                                   letter-spacing:-0.5px;font-family:'Poppins',sans-serif;">
                        Nich-Ká
                      </span>
                    </td>
                  </tr>
                </table>
              </a>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background-color:#111113;border:1px solid #2a2a2d;
                        border-radius:14px;overflow:hidden;">

              <!-- Header -->
              <tr>
                <td class="email-header"
                    style="padding:36px 40px 28px;border-bottom:1px solid #2a2a2d;">
                  <h1 class="email-title"
                      style="margin:0 0 8px;color:#f4f4f5;font-size:22px;font-weight:600;
                              letter-spacing:-0.3px;font-family:'Poppins',sans-serif;">
                    Recupera tu contraseña
                  </h1>
                  <p style="margin:0;color:#a1a1aa;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Hola, <strong style="color:#f4f4f5;">{name}</strong>. Recibimos una
                    solicitud para restablecer la contraseña de tu cuenta.
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td class="email-body" style="padding:32px 40px;">

                  <!-- Código -->
                  <p style="margin:0 0 12px;color:#a1a1aa;font-size:13px;
                              font-family:'Poppins',sans-serif;">
                    Ingresa el siguiente código de verificación en la aplicación:
                  </p>

                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td align="center"
                          style="background-color:#1a1a1d;border:1px solid #2a2a2d;
                                  border-radius:12px;padding:24px 0;">
                        <span class="code-box"
                              style="color:#f4f4f5;font-size:38px;font-weight:700;
                                     letter-spacing:14px;font-family:'Poppins',sans-serif;">
                          {code}
                        </span>
                      </td>
                    </tr>
                  </table>

                  <!-- Aviso expiración -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="background-color:rgba(234,179,8,0.06);
                                  border:1px solid rgba(234,179,8,0.2);
                                  border-radius:10px;padding:16px 18px;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:10px;
                                        padding-top:2px;width:22px;">
                              <img src="https://img.icons8.com/color/20/error--v1.png"
                                   width="16" height="16" alt=""
                                   style="display:block;border:0;width:16px;height:16px;"/>
                            </td>
                            <td>
                              <p style="margin:0;color:#a1a1aa;font-size:13px;line-height:1.7;
                                         font-family:'Poppins',sans-serif;">
                                Este código expira en
                                <strong style="color:#f4f4f5;">15 minutos</strong>.
                                Si no solicitaste este cambio, puedes ignorar este correo.
                              </p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- Nota seguridad -->
                  <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Por seguridad, nunca compartas este código con nadie.
                    Nich-Ká jamás te lo pedirá.
                  </p>

                </td>
              </tr>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:28px 0;text-align:center;">
              <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                          font-family:'Poppins',sans-serif;">
                Este correo fue enviado automáticamente por Nich-Ká.<br/>
                Si no solicitaste este cambio, ignora este mensaje.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_reset_password_email(to_email: str, name: str, code: str) -> None:
    if not settings.RESEND_API_KEY or not settings.MAIL_FROM:
        logger.warning("[Email] RESEND_API_KEY o MAIL_FROM no configurados, omitiendo envío")
        return

    try:
        resend.api_key = settings.RESEND_API_KEY
        from_address = (
            f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            if settings.MAIL_FROM_NAME
            else settings.MAIL_FROM
        )
        params: resend.Emails.SendParams = {
            "from": from_address,
            "to": [to_email],
            "subject": "Código de recuperación de contraseña - Nich-Ká",
            "html": _reset_password_html(name, code),
        }
        resend.Emails.send(params)
        logger.info(f"[Email] Código de recuperación enviado a {to_email}")
    except Exception as e:
        logger.error(f"[Email] Error al enviar código de recuperación a {to_email}: {e}")


def _password_changed_html(name: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Contraseña actualizada - Nich-Ká</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
        rel="stylesheet"/>
  <style>
    @media only screen and (max-width: 600px) {{
      .email-wrapper {{ padding: 24px 12px !important; }}
      .email-header  {{ padding: 28px 20px 22px !important; }}
      .email-body    {{ padding: 24px 20px !important; }}
      .email-title   {{ font-size: 19px !important; }}
      .btn-cta       {{ display: block !important; text-align: center !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#0A0A0B;font-family:'Poppins',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" class="email-wrapper"
         style="background-color:#0A0A0B;padding:48px 16px;">
    <tr>
      <td align="center">
        <table cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

          <!-- Logo -->
          <tr>
            <td align="left" style="padding-bottom:32px;">
              <a href="https://www.nich-ka.space/" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="vertical-align:middle;padding-right:10px;">
                      <img src="https://www.nich-ka.space/assets/logo.svg"
                           alt="Nich-Ká" width="40" height="40"
                           style="display:block;border:0;width:40px;height:40px;"/>
                    </td>
                    <td style="vertical-align:middle;">
                      <span style="color:#f4f4f5;font-size:20px;font-weight:700;
                                   letter-spacing:-0.5px;font-family:'Poppins',sans-serif;">
                        Nich-Ká
                      </span>
                    </td>
                  </tr>
                </table>
              </a>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background-color:#111113;border:1px solid #2a2a2d;
                        border-radius:14px;overflow:hidden;">

              <!-- Header -->
              <tr>
                <td class="email-header"
                    style="padding:36px 40px 28px;border-bottom:1px solid #2a2a2d;">
                  <h1 class="email-title"
                      style="margin:0 0 8px;color:#f4f4f5;font-size:22px;font-weight:600;
                              letter-spacing:-0.3px;font-family:'Poppins',sans-serif;">
                    Contraseña actualizada ✓
                  </h1>
                  <p style="margin:0;color:#a1a1aa;font-size:14px;line-height:1.6;
                              font-family:'Poppins',sans-serif;">
                    Hola, <strong style="color:#f4f4f5;">{name}</strong>. Tu contraseña
                    fue restablecida exitosamente.
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td class="email-body" style="padding:32px 40px;">

                  <!-- Aviso seguridad -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                    <tr>
                      <td style="background-color:rgba(234,179,8,0.06);
                                  border:1px solid rgba(234,179,8,0.2);
                                  border-radius:10px;padding:16px 18px;">
                        <table cellpadding="0" cellspacing="0" width="100%">
                          <tr>
                            <td style="vertical-align:top;padding-right:10px;
                                        padding-top:2px;width:22px;">
                              <img src="https://img.icons8.com/color/20/error--v1.png"
                                   width="16" height="16" alt=""
                                   style="display:block;border:0;width:16px;height:16px;"/>
                            </td>
                            <td>
                              <p style="margin:0;color:#a1a1aa;font-size:13px;line-height:1.7;
                                         font-family:'Poppins',sans-serif;">
                                Si tú realizaste este cambio, puedes ignorar este mensaje.<br/>
                                Si <strong style="color:#f4f4f5;">no fuiste tú</strong>,
                                contacta a soporte de inmediato ya que alguien más pudo
                                haber accedido a tu cuenta.
                              </p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- CTA -->
                  <table cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                      <td>
                        <a href="{settings.FRONTEND_URL}" class="btn-cta"
                           style="display:inline-block;background-color:#ffffff;
                                  color:#0A0A0B;text-decoration:none;padding:12px 28px;
                                  border-radius:8px;font-size:14px;font-weight:600;
                                  font-family:'Poppins',sans-serif;letter-spacing:-0.1px;">
                          Ir a la plataforma →
                        </a>
                      </td>
                    </tr>
                  </table>

                </td>
              </tr>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:28px 0;text-align:center;">
              <p style="margin:0;color:#52525b;font-size:12px;line-height:1.6;
                          font-family:'Poppins',sans-serif;">
                Este correo fue enviado automáticamente por Nich-Ká.<br/>
                Si no realizaste este cambio, comunícate con soporte.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_password_changed_email(to_email: str, name: str) -> None:
    if not settings.RESEND_API_KEY or not settings.MAIL_FROM:
        logger.warning("[Email] RESEND_API_KEY o MAIL_FROM no configurados, omitiendo envío")
        return

    try:
        resend.api_key = settings.RESEND_API_KEY
        from_address = (
            f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            if settings.MAIL_FROM_NAME
            else settings.MAIL_FROM
        )
        params: resend.Emails.SendParams = {
            "from": from_address,
            "to": [to_email],
            "subject": "Tu contraseña fue actualizada - Nich-Ká",
            "html": _password_changed_html(name),
        }
        resend.Emails.send(params)
        logger.info(f"[Email] Aviso de cambio de contraseña enviado a {to_email}")
    except Exception as e:
        logger.error(f"[Email] Error al enviar aviso de cambio de contraseña a {to_email}: {e}")
