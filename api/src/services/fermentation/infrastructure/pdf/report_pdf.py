import io
import os
from datetime import datetime

from fpdf import FPDF

_ASSETS   = os.path.join(os.path.dirname(__file__), "assets")
_LOGO     = os.path.join(_ASSETS, "logo.svg")
_FONT_REG = os.path.join(_ASSETS, "Poppins-Regular.ttf")
_FONT_SB  = os.path.join(_ASSETS, "Poppins-SemiBold.ttf")

DARK = (24, 24, 27)
GREY = (113, 113, 122)
LINE = (228, 228, 231)

_STATUS_ES = {
    "completed": "Completada",
    "interrupted": "Interrumpida",
    "running": "En curso",
    "scheduled": "Programada",
}

_ROLE_ES = {
    "profesor": "Profesor",
    "admin": "Administrador",
    "estudiante": "Estudiante",
}


def _fmt_dt(dt) -> str:
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "-"


def _num(v, suffix="") -> str:
    return f"{v:.2f}{suffix}" if v is not None else "-"


def _duration(start, end) -> str:
    if not start or not end:
        return "-"
    secs = int((end - start).total_seconds())
    return f"{secs // 3600}h {(secs % 3600) // 60}m"


def _charts_png(report) -> bytes | None:
    """Pastel de eficiencia + barras de etanol (teórico vs detectado) como PNG.
    Import perezoso: si matplotlib no está, devuelve None y el PDF sale sin gráfica."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        eff = max(0.0, min(100.0, report.efficiency or 0.0))
        teo = report.theoretical_ethanol or 0.0
        det = report.ethanol_detected or 0.0

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.2, 2.0), dpi=150)

        # Pastel (donut) de eficiencia
        ax1.pie(
            [max(eff, 0.001), max(100 - eff, 0.001)],
            colors=["#18181b", "#e4e4e7"],
            startangle=90, counterclock=False,
            wedgeprops=dict(width=0.42),
        )
        ax1.text(0, 0, f"{eff:.0f}%", ha="center", va="center",
                 fontsize=15, fontweight="bold", color="#18181b")
        ax1.set_title("Eficiencia", fontsize=11, color="#18181b")

        # Barras de etanol
        bars = ax2.bar(["Teórico", "Detectado"], [teo, det],
                       color=["#a1a1aa", "#18181b"], width=0.55)
        ax2.set_title("Etanol (%)", fontsize=11, color="#18181b")
        ax2.tick_params(labelsize=9, colors="#52525b")
        for b, v in zip(bars, [teo, det]):
            ax2.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}",
                     ha="center", va="bottom", fontsize=9, color="#18181b")
        for s in ("top", "right", "left"):
            ax2.spines[s].set_visible(False)
        ax2.set_yticks([])

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close(fig)
        return buf.getvalue()
    except Exception:
        return None


def build_report_pdf(session, report, owner_name=None, owner_role=None, circuit_code=None) -> bytes:
    """Genera el PDF del reporte de una fermentación. Devuelve los bytes."""
    lote = f"F-{session.id:03d}"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Poppins", "", _FONT_REG)
    pdf.add_font("Poppins", "B", _FONT_SB)
    pdf.add_page()

    # ── Encabezado: logo + marca + título (sin color de fondo) ────────────────
    try:
        pdf.image(_LOGO, x=14, y=12, w=14)
    except Exception:
        pass

    pdf.set_xy(32, 12)
    pdf.set_font("Poppins", "B", 16)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 7, "Nich-Ká", ln=True)

    pdf.set_xy(32, 21)
    pdf.set_font("Poppins", "", 11)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 6, f"Reporte de fermentación · {lote}", ln=True)

    pdf.set_draw_color(*LINE)
    pdf.line(14, 33, 196, 33)
    pdf.set_y(42)

    def section(title: str) -> None:
        pdf.set_font("Poppins", "B", 11.5)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 7, title, ln=True)

    def kv_table(pairs) -> None:
        for label, value in pairs:
            pdf.set_font("Poppins", "B", 9.5)
            pdf.set_text_color(*GREY)
            pdf.cell(55, 6.5, f"  {label}", border="B")
            pdf.set_font("Poppins", "", 9.5)
            pdf.set_text_color(*DARK)
            pdf.cell(127, 6.5, str(value), border="B", ln=True)

    pdf.set_draw_color(*LINE)

    # ── General ───────────────────────────────────────────────────────────────
    section("General")
    _general = [
        ("Código de activación", circuit_code or f"#{session.circuit_id}"),
        ("Estado", _STATUS_ES.get(session.status, session.status)),
        ("Inicio", _fmt_dt(session.actual_start or session.scheduled_start)),
        ("Fin", _fmt_dt(session.actual_end or session.scheduled_end)),
        ("Duración", _duration(session.actual_start, session.actual_end)),
    ]
    if owner_name:
        rol = _ROLE_ES.get(owner_role, owner_role or "")
        _general.insert(1, ("Iniciada por", f"{owner_name} ({rol})" if rol else owner_name))
    kv_table(_general)
    pdf.ln(2)

    # ── Resultados ──────────────────────────────────────────────────────────────
    section("Resultados")
    kv_table([
        ("Azúcar inicial", _num(report.initial_sugar, " g/L")),
        ("Etanol detectado", _num(report.ethanol_detected, " %")),
        ("Etanol teórico", _num(report.theoretical_ethanol, " %")),
        ("Eficiencia", _num(report.efficiency, " %")),
    ])
    pdf.ln(2)

    # ── Gráficas (pastel de eficiencia + barras de etanol) ───────────────────────
    chart = _charts_png(report)
    if chart:
        pdf.image(io.BytesIO(chart), x=40, w=130)
        pdf.ln(3)

    # ── Sensores (tabla) ─────────────────────────────────────────────────────────
    section("Sensores")
    c1, c2, c3 = 70.0, 56.0, 56.0

    pdf.set_font("Poppins", "B", 9)
    pdf.set_text_color(*GREY)
    pdf.set_fill_color(244, 244, 246)
    pdf.cell(c1, 6.5, "  Sensor", fill=True)
    pdf.cell(c2, 6.5, "Inicial", fill=True, align="C")
    pdf.cell(c3, 6.5, "Final", fill=True, align="C", ln=True)

    pdf.set_font("Poppins", "", 9.5)
    for label, ini, fin in [
        ("Temperatura", report.temperature_initial, report.temperature_final),
        ("pH", report.ph_initial, report.ph_final),
        ("Alcohol", report.alcohol_initial, report.alcohol_final),
        ("Densidad", report.density_initial, report.density_final),
        ("Conductividad", report.conductivity_initial, report.conductivity_final),
        ("Turbidez", report.turbidity_initial, report.turbidity_final),
    ]:
        pdf.set_text_color(*DARK)
        pdf.cell(c1, 6.5, f"  {label}", border="B")
        pdf.cell(c2, 6.5, _num(ini), border="B", align="C")
        pdf.cell(c3, 6.5, _num(fin), border="B", align="C", ln=True)

    # ── Pie ─────────────────────────────────────────────────────────────────────
    pdf.set_auto_page_break(False)  # el pie va en el margen sin forzar otra hoja
    pdf.set_y(-13)
    pdf.set_font("Poppins", "", 8.5)
    pdf.set_text_color(*GREY)
    pdf.cell(
        0, 6,
        f"Generado por Nich-Ká · {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        align="C",
    )

    return bytes(pdf.output())
