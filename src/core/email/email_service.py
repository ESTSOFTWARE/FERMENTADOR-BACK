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
