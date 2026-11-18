"""services/exporter.py — data export + real analysis-report PDF generation."""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import numpy as np
import polars as pl
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# PDF/report dependencies
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import plotly.io as pio


NUMERIC_DTYPES = (
    pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
)


def to_csv(df: pl.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.write_csv(buf)
    return buf.getvalue()


def to_parquet(df: pl.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.write_parquet(buf)
    return buf.getvalue()


def to_json(df: pl.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.write_json(buf, row_oriented=True)
    return buf.getvalue()


def to_excel(df: pl.DataFrame, sheet_name: str = "Data") -> bytes:
    pdf = df.to_pandas()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    hdr_fill = PatternFill("solid", fgColor="00E5A0")
    hdr_font = Font(bold=True, color="0D0F14", name="Calibri", size=11)
    hdr_align = Alignment(horizontal="center", vertical="center")
    hdr_border = Border(bottom=Side(style="medium", color="252A35"))

    for col_idx, col_name in enumerate(pdf.columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = hdr_align
        cell.border = hdr_border

    alt_fill = PatternFill("solid", fgColor="161922")
    for row_idx, row in enumerate(pdf.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = Font(name="Calibri", size=10, color="E8ECF2")
            if row_idx % 2 == 0:
                cell.fill = alt_fill

    for col_idx, col_name in enumerate(pdf.columns, start=1):
        vals = pdf[col_name].astype(str).values[:500]
        max_len = max([len(str(col_name))] + [len(str(v)) for v in vals])
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 40)

    ws.freeze_panes = "A2"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _numeric_cols(df: pl.DataFrame) -> list[str]:
    return [c for c in df.columns if df[c].dtype in NUMERIC_DTYPES]


def _safe_float(v: Any) -> float | None:
    try:
        x = float(v)
        return x if np.isfinite(x) else None
    except Exception:
        return None


def _fmt(v: Any, digits: int = 2) -> str:
    x = _safe_float(v)
    if x is None:
        return "—"
    return f"{x:,.{digits}f}"


def _interpret_numeric(df: pl.DataFrame, col: str) -> str:
    s = df[col].drop_nulls()
    if len(s) == 0:
        return f"No numeric observations were available for {col}."
    arr = s.to_numpy().astype(float)
    mean = float(np.mean(arr))
    med = float(np.median(arr))
    mn = float(np.min(arr))
    mx = float(np.max(arr))
    if mean > med * 1.05:
        shape = "The mean is above the median, suggesting some higher values are pulling the average upward."
    elif med > mean * 1.05:
        shape = "The median is above the mean, suggesting some lower values are pulling the average downward."
    else:
        shape = "The mean and median are relatively close, so the center of the distribution is fairly similar by both measures."
    return (
        f"{col} has {len(arr):,} non-missing observations. "
        f"The average is {_fmt(mean)}, the median is {_fmt(med)}, "
        f"and the observed range is {_fmt(mn)} to {_fmt(mx)}. {shape}"
    )


def _category_interpretation(df: pl.DataFrame, col: str) -> str:
    s = df[col].drop_nulls()
    if len(s) == 0:
        return f"No non-missing values were available for {col}."
    vc = s.value_counts().sort("count", descending=True)
    top = vc.row(0)
    share = float(top[1]) / len(s) * 100
    return (
        f"The most frequent value in {col} is '{top[0]}', occurring "
        f"{int(top[1]):,} times ({share:.1f}% of non-missing observations). "
        f"The column contains {len(vc):,} distinct observed values."
    )


def _plot_png(fig, width=1000, height=560) -> bytes:
    """Convert a Plotly figure to PNG for embedding in the PDF.

    Plotly's current image exporter uses Kaleido 1.x.  Older projects often
    pinned Kaleido 0.2.x, which is incompatible with newer Plotly releases.
    This function also gives a clear installation message instead of silently
    putting an error message into the PDF.
    """
    try:
        return pio.to_image(fig, format="png", width=width, height=height, scale=1)
    except Exception as exc:
        msg = str(exc)
        if "Kaleido" in msg or "kaleido" in msg or "Chrome" in msg or "browser" in msg.lower():
            raise RuntimeError(
                "Plotly chart export needs Kaleido 1.x and a Chrome/Chromium browser. "
                "Run: python -m pip install --upgrade \"kaleido>=1.0.0\" "
                "and then restart Streamlit. If Kaleido reports that Chrome is missing, "
                "run: python -m kaleido.get_chrome"
            ) from exc
        raise


def _auto_figures(df: pl.DataFrame):
    """Build report figures from the actual uploaded data."""
    import plotly.express as px
    import plotly.graph_objects as go

    figs: list[tuple[str, Any, str]] = []
    nums = _numeric_cols(df)
    cats = [c for c in df.columns if df[c].dtype in (pl.Utf8, pl.Categorical, pl.Boolean)]

    # 1. Traffic condition distribution
    traffic_col = next((c for c in ["Traffic_Condition", "Traffic Condition", "traffic_condition"] if c in df.columns), None)
    if traffic_col:
        vc = df[traffic_col].value_counts().sort("count", descending=True)
        pdf = vc.to_pandas()
        fig = px.bar(pdf, x=traffic_col, y="count", title="Traffic Condition Distribution",
                     labels={"count": "Number of observations", traffic_col: "Traffic condition"})
        figs.append(("Traffic Condition Distribution", fig,
                     "This chart shows how frequently each traffic condition occurs in the dataset. "
                     "A larger bar means that condition appears more often in the recorded observations."))

    # 2. Vehicle count distribution
    vehicle_col = next((c for c in ["Vehicle_Count", "Vehicle Count", "vehicle_count"] if c in df.columns), None)
    if vehicle_col:
        fig = px.histogram(df.select(vehicle_col).drop_nulls().to_pandas(), x=vehicle_col, nbins=30,
                           title="Vehicle Count Distribution")
        figs.append(("Vehicle Count Distribution", fig,
                     _interpret_numeric(df, vehicle_col)))

    # 3. Speed distribution
    speed_col = next((c for c in ["Traffic_Speed_kmh", "Traffic Speed", "traffic_speed_kmh"] if c in df.columns), None)
    if speed_col:
        fig = px.histogram(df.select(speed_col).drop_nulls().to_pandas(), x=speed_col, nbins=30,
                           title="Traffic Speed Distribution")
        figs.append(("Traffic Speed Distribution", fig, _interpret_numeric(df, speed_col)))

    # 4. Domain comparison: traffic condition vs selected numeric measures
    if traffic_col:
        candidates = [c for c in [
            vehicle_col,
            speed_col,
            "Road_Occupancy_%",
            "Emission_Levels_g_km",
            "Energy_Consumption_L_h",
            "Ride_Sharing_Demand",
            "Parking_Availability",
        ] if c and c in df.columns and c in nums]
        for c in candidates[:3]:
            pdf = df.select([traffic_col, c]).drop_nulls().to_pandas()
            if len(pdf):
                agg = pdf.groupby(traffic_col, sort=False)[c].mean().reset_index()
                fig = px.bar(agg, x=traffic_col, y=c, title=f"Average {c} by Traffic Condition")
                figs.append((f"Average {c} by Traffic Condition", fig,
                             f"This comparison shows the average {c} recorded for each traffic condition. "
                             f"It helps identify whether the measure changes across low, medium, and high traffic categories."))

    # 5. Weather vs traffic, if both exist
    weather_col = next((c for c in ["Weather_Condition", "Weather Condition", "weather_condition"] if c in df.columns), None)
    if weather_col and traffic_col:
        cross = df.group_by([weather_col, traffic_col]).len().sort("len", descending=True)
        pdf = cross.to_pandas()
        fig = px.bar(pdf, x=weather_col, y="len", color=traffic_col,
                     barmode="group", title="Traffic Conditions Across Weather Conditions",
                     labels={"len": "Number of observations"})
        figs.append(("Traffic Conditions Across Weather Conditions", fig,
                     "This chart compares traffic-condition counts across weather categories. "
                     "It describes the observed combination of weather and traffic conditions; it does not by itself prove that weather causes traffic changes."))

    # 6. Emissions distribution
    emission_col = next((c for c in ["Emission_Levels_g_km", "Emission Levels", "emission_levels_g_km"] if c in df.columns), None)
    if emission_col:
        fig = px.histogram(df.select(emission_col).drop_nulls().to_pandas(), x=emission_col, nbins=30,
                           title="Emission Level Distribution")
        figs.append(("Emission Level Distribution", fig, _interpret_numeric(df, emission_col)))

    # 7. Correlation heatmap (limited to 12 columns for readability)
    if len(nums) >= 2:
        corr_pdf = df.select(nums[:12]).to_pandas().corr()
        fig = go.Figure(go.Heatmap(
            z=corr_pdf.values, x=corr_pdf.columns, y=corr_pdf.columns,
            zmin=-1, zmax=1, zmid=0, colorscale="RdBu",
            text=np.round(corr_pdf.values, 2), texttemplate="%{text}"
        ))
        fig.update_layout(title="Numeric Correlation Matrix", height=700,
                          margin=dict(l=80, r=30, t=60, b=100))
        figs.append(("Numeric Correlation Matrix", fig,
                     "Correlation values range from -1 to +1. Values near +1 indicate that two variables tend to increase together, while values near -1 indicate an inverse linear relationship. Correlation does not establish causation."))

    # 8. Timestamp trend
    time_col = next((c for c in ["Timestamp", "timestamp", "Date", "Datetime"] if c in df.columns), None)
    if time_col and vehicle_col:
        try:
            t = df.select([time_col, vehicle_col]).with_columns(
                pl.col(time_col).str.to_datetime(strict=False)
            ).drop_nulls().sort(time_col)
            if t.height >= 2:
                # Aggregate by hour/day depending on range
                pdf = t.to_pandas()
                pdf[time_col] = __import__("pandas").to_datetime(pdf[time_col])
                if (pdf[time_col].max() - pdf[time_col].min()).days > 3:
                    pdf["period"] = pdf[time_col].dt.date.astype(str)
                else:
                    pdf["period"] = pdf[time_col].dt.strftime("%Y-%m-%d %H:%M")
                agg = pdf.groupby("period", sort=True)[vehicle_col].mean().reset_index()
                # Keep chart readable
                if len(agg) > 80:
                    idx = np.linspace(0, len(agg)-1, 80).astype(int)
                    agg = agg.iloc[idx]
                fig = px.line(agg, x="period", y=vehicle_col, title="Vehicle Count Over Time")
                figs.append(("Vehicle Count Over Time", fig,
                             "This chart shows how average vehicle count changes across the recorded time periods. Peaks represent periods with relatively higher observed vehicle volume.")) 
        except Exception:
            pass

    return figs


def _build_interpretations(df: pl.DataFrame) -> list[str]:
    insights = []
    nums = _numeric_cols(df)

    traffic_col = next((c for c in ["Traffic_Condition", "Traffic Condition", "traffic_condition"] if c in df.columns), None)
    vehicle_col = next((c for c in ["Vehicle_Count", "Vehicle Count", "vehicle_count"] if c in df.columns), None)
    speed_col = next((c for c in ["Traffic_Speed_kmh", "Traffic Speed", "traffic_speed_kmh"] if c in df.columns), None)
    emission_col = next((c for c in ["Emission_Levels_g_km", "Emission Levels", "emission_levels_g_km"] if c in df.columns), None)

    if traffic_col and vehicle_col:
        try:
            a = df.group_by(traffic_col).agg(pl.col(vehicle_col).mean().alias("avg")).sort("avg", descending=True)
            r = a.row(0)
            insights.append(f"The highest average vehicle count is observed in the '{r[0]}' traffic category ({_fmt(r[1])} vehicles per observation).")
        except Exception:
            pass

    if traffic_col and speed_col:
        try:
            a = df.group_by(traffic_col).agg(pl.col(speed_col).mean().alias("avg")).sort("avg")
            r = a.row(0)
            insights.append(f"The lowest average traffic speed is observed in the '{r[0]}' traffic category ({_fmt(r[1])} km/h).")
        except Exception:
            pass

    if emission_col:
        insights.append(_interpret_numeric(df, emission_col))

    # Missing-data insight
    total_nulls = sum(df[c].null_count() for c in df.columns)
    if total_nulls == 0:
        insights.append("No missing values were detected in the uploaded dataset.")
    else:
        insights.append(f"The dataset contains {total_nulls:,} missing cells. Columns with missing values should be reviewed before using affected measures for decision-making.")

    if not insights:
        insights.append("The report summarizes the uploaded dataset using descriptive statistics and visual patterns.")
    return insights


def analysis_report_pdf(
    df: pl.DataFrame,
    filename: str = "dataset.csv",
    saved_figures: list[tuple[str, Any, str]] | None = None,
) -> bytes:
    """Create a real PDF report: tables + chart images + interpretations.

    The input DataFrame is read only. Nothing is added to or removed from it.
    """
    figs = _auto_figures(df)
    if saved_figures:
        # Add user-created dashboard charts after automatic report charts.
        existing_titles = {x[0] for x in figs}
        for item in saved_figures:
            if item[0] not in existing_titles:
                figs.append(item)

    nums = _numeric_cols(df)
    cats = [c for c in df.columns if c not in nums]
    total_nulls = sum(df[c].null_count() for c in df.columns)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=42, bottomMargin=42,
        title=f"DataLens Analysis Report - {filename}",
        author="DataLens",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle("DLTitle", parent=styles["Title"], fontSize=25, leading=30,
                           textColor=colors.HexColor("#123B35"), alignment=TA_CENTER, spaceAfter=10)
    subtitle = ParagraphStyle("DLSub", parent=styles["Normal"], fontSize=10, leading=15,
                              textColor=colors.HexColor("#5B6573"), alignment=TA_CENTER, spaceAfter=20)
    h1 = ParagraphStyle("DLH1", parent=styles["Heading1"], fontSize=17, leading=21,
                        textColor=colors.HexColor("#123B35"), spaceBefore=16, spaceAfter=10)
    h2 = ParagraphStyle("DLH2", parent=styles["Heading2"], fontSize=13, leading=17,
                        textColor=colors.HexColor("#234E49"), spaceBefore=12, spaceAfter=7)
    body = ParagraphStyle("DLBody", parent=styles["BodyText"], fontSize=9.5, leading=14,
                          textColor=colors.HexColor("#27313B"), spaceAfter=7)
    small = ParagraphStyle("DLSmall", parent=body, fontSize=8, leading=11,
                           textColor=colors.HexColor("#65717D"))
    bullet = ParagraphStyle("DLBullet", parent=body, leftIndent=14, firstLineIndent=-7)

    story = []
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("DataLens", title))
    story.append(Paragraph("Smart Data Analysis Report", h1))
    story.append(Paragraph(
        f"<b>Source file:</b> {filename}<br/>"
        f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}<br/>"
        "The original uploaded dataset is not modified by this report.",
        subtitle
    ))

    story.append(Paragraph("1. Dataset Overview", h1))
    overview = [
        ["Metric", "Value"],
        ["Rows", f"{df.height:,}"],
        ["Columns", f"{df.width:,}"],
        ["Numeric columns", f"{len(nums):,}"],
        ["Other columns", f"{len(cats):,}"],
        ["Missing cells", f"{total_nulls:,}"],
    ]
    t = Table(overview, colWidths=[2.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B35")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D8DEE5")),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#F7F9FB")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F3F6F8")]),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("PADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(t)

    story.append(Paragraph("2. Data Quality", h1))
    if total_nulls == 0:
        story.append(Paragraph("No missing values were detected. The uploaded table is complete with respect to null cells.", body))
    else:
        null_rows = [["Column", "Missing", "Missing %"]]
        for c in df.columns:
            n = df[c].null_count()
            if n:
                null_rows.append([c, f"{n:,}", f"{n/df.height*100:.2f}%"])
        nt = Table(null_rows, repeatRows=1, colWidths=[2.8*inch, 1.1*inch, 1.1*inch])
        nt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7A2630")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D8DEE5")),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("PADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(nt)

    story.append(Paragraph("3. Statistical Summary", h1))
    if nums:
        data = [["Variable", "Count", "Mean", "Median", "Min", "Max", "Std. Dev."]]
        for c in nums:
            s = df[c].drop_nulls()
            arr = s.to_numpy().astype(float)
            data.append([
                c, f"{len(arr):,}",
                _fmt(np.mean(arr)), _fmt(np.median(arr)),
                _fmt(np.min(arr)), _fmt(np.max(arr)),
                _fmt(np.std(arr, ddof=1) if len(arr)>1 else 0),
            ])
        stbl = Table(data, repeatRows=1, colWidths=[1.55*inch, .55*inch, .75*inch, .75*inch, .65*inch, .65*inch, .75*inch])
        stbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B35")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#D8DEE5")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F7F9")]),
            ("FONTSIZE", (0,0), (-1,-1), 7),
            ("PADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(stbl)
    else:
        story.append(Paragraph("No numeric columns were detected.", body))

    story.append(PageBreak())
    story.append(Paragraph("4. Easy-to-Understand Interpretations", h1))
    for c in nums[:8]:
        story.append(Paragraph(f"<b>{c}</b>", h2))
        story.append(Paragraph(_interpret_numeric(df, c), body))

    for c in cats[:5]:
        story.append(Paragraph(f"<b>{c}</b>", h2))
        story.append(Paragraph(_category_interpretation(df, c), body))

    story.append(Paragraph("5. Key Findings", h1))
    for item in _build_interpretations(df):
        story.append(Paragraph("• " + item, bullet))

    story.append(PageBreak())
    story.append(Paragraph("6. Visual Analysis", h1))
    if not figs:
        story.append(Paragraph("No suitable charts could be generated from this dataset.", body))
    else:
        for idx, (fig_title, fig, interpretation) in enumerate(figs):
            story.append(Paragraph(fig_title, h2))
            try:
                png = _plot_png(fig)
                img = Image(io.BytesIO(png), width=6.8*inch, height=3.8*inch)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Paragraph(f"<b>Interpretation:</b> {interpretation}", body))
            except Exception as e:
                story.append(Paragraph(
                    f"Chart could not be embedded. Install the required chart-export package and retry. Details: {e}",
                    small
                ))
            story.append(Spacer(1, 0.12*inch))
            if idx < len(figs) - 1 and idx % 2 == 1:
                story.append(PageBreak())

    story.append(PageBreak())
    story.append(Paragraph("7. Report Notes", h1))
    story.append(Paragraph(
        "This report is an analytical summary of the uploaded data. "
        "Charts may use a visual sample for performance, while the descriptive statistics are calculated from the available observations. "
        "Relationships shown by correlation or grouped comparisons should be interpreted as associations, not proof of causation.",
        body
    ))
    story.append(Paragraph(
        "The report is a separate output. The source CSV/dataframe is not altered to add interpretations, chart data, or report columns.",
        body
    ))

    doc.build(story)
    return buf.getvalue()
