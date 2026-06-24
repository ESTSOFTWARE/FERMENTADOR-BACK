from datetime import datetime

from fpdf import FPDF

GREEN = (34, 197, 94)
DARK = (24, 24, 27)
GREY = (113, 113, 122)

_STATUS_ES = {
    "completed": "Completada",
    "interrupted": "Interrumpida",
    "running": "En curso",
    "scheduled": "Programada",
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


def build_report_pdf(session, report) -> bytes:
    """Genera el PDF del reporte de una fermentación. Devuelve los bytes."""
    lote = f"F-{session.id:03d}"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Encabezado ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*GREEN)
    pdf.rect(0, 0, 210, 26, style="F")
    pdf.set_xy(14, 8)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Nich-Ká", ln=True)

    pdf.set_xy(14, 34)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, f"Reporte de fermentación {lote}", ln=True)
    pdf.ln(4)

    def section(title: str) -> None:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*GREEN)
        pdf.cell(0, 9, title, ln=True)

    def row(label: str, value) -> None:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*GREY)
        pdf.cell(58, 8, label)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 8, str(value), ln=True)

    # ── General ─────────────────────────────────────────────────────────────
    section("General")
    row("Circuito", f"#{session.circuit_id}")
    row("Estado", _STATUS_ES.get(session.status, session.status))
    row("Inicio", _fmt_dt(session.actual_start or session.scheduled_start))
    row("Fin", _fmt_dt(session.actual_end or session.scheduled_end))
    row("Duración", _duration(session.actual_start, session.actual_end))
    pdf.ln(3)

    # ── Resultados ──────────────────────────────────────────────────────────
    section("Resultados")
    row("Azúcar inicial", _num(report.initial_sugar, " g/L"))
    row("Etanol detectado", _num(report.ethanol_detected, " %"))
    row("Etanol teórico", _num(report.theoretical_ethanol, " %"))
    row("Eficiencia", _num(report.efficiency, " %"))
    pdf.ln(3)

    # ── Sensores (inicial -> final) ─────────────────────────────────────────
    section("Sensores (inicial -> final)")

    def sensor(label: str, ini, fin) -> None:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*GREY)
        pdf.cell(58, 8, label)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 8, f"{_num(ini)}  ->  {_num(fin)}", ln=True)

    sensor("Temperatura", report.temperature_initial, report.temperature_final)
    sensor("pH", report.ph_initial, report.ph_final)
    sensor("Alcohol", report.alcohol_initial, report.alcohol_final)
    sensor("Densidad", report.density_initial, report.density_final)
    sensor("Conductividad", report.conductivity_initial, report.conductivity_final)
    sensor("Turbidez", report.turbidity_initial, report.turbidity_final)

    # ── Pie ─────────────────────────────────────────────────────────────────
    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GREY)
    pdf.cell(
        0, 8,
        f"Generado por Nich-Ká · {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        align="C",
    )

    return bytes(pdf.output())
