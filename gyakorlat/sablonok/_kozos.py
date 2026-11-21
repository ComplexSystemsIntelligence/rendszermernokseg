"""Közös stílusok és segédfüggvények a Gyakorlati útmutató Excel-sablonjaihoz.

Minden sablongenerátor (_gen_*.py) ezt a modult használja, így a sablonok
egységes megjelenésűek: Arial betű, sárga hátterű kék betűs bemeneti cellák,
halványkék hátterű képletcellák, PE-kék fejléc.
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.comments import Comment
from openpyxl.drawing.image import Image as XLKep
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.units import pixels_to_EMU
from openpyxl.worksheet.datavalidation import DataValidation

MAPPA = Path(__file__).resolve().parent
PE_LOGO = MAPPA.parents[1] / "_shared" / "logo" / "png" / "PE_cimer_nevjel_fekvo_kek-120.png"
KEK = "285780"
HALVANY = "E6EEF6"
SARGA = "FFF4CC"
BETU = "Arial"

fej_font = Font(name=BETU, bold=True, color="FFFFFF")
fej_fill = PatternFill("solid", fgColor=KEK)
cim_font = Font(name=BETU, bold=True, size=14, color=KEK)
alcim_font = Font(name=BETU, size=10, italic=True, color="555555")
alap_font = Font(name=BETU, size=10)
felkover = Font(name=BETU, size=10, bold=True)
bevitel_font = Font(name=BETU, size=10, color="0000FF")
bevitel_fill = PatternFill("solid", fgColor=SARGA)
keplet_fill = PatternFill("solid", fgColor=HALVANY)
vekony = Side(style="thin", color="C9D6E3")
keret = Border(left=vekony, right=vekony, top=vekony, bottom=vekony)
tord = Alignment(wrap_text=True, vertical="top")
kozep = Alignment(horizontal="center", vertical="center", wrap_text=True)

FORRAS = "Forrás: Abonyi J.: Rendszermérnöki eszköztár – Gyakorlati útmutató (CC BY-NC-SA 4.0)"


def uj_munkafuzet():
    return Workbook()


def fejlec(ws, sor, cimek, szelessegek=None, oszlop=1, magassag=32):
    for i, c in enumerate(cimek):
        cell = ws.cell(row=sor, column=oszlop + i, value=c)
        cell.font, cell.fill, cell.border = fej_font, fej_fill, keret
        cell.alignment = kozep
        if szelessegek:
            ws.column_dimensions[get_column_letter(oszlop + i)].width = szelessegek[i]
    ws.row_dimensions[sor].height = magassag


def cimsor(ws, szoveg, alcim=None):
    ws["A1"] = szoveg
    ws["A1"].font = cim_font
    if alcim:
        ws["A2"] = alcim
        ws["A2"].font = alcim_font


def pe_logo(ws, oszlop_px=775, magassag=38):
    """A Pannon Egyetem fekvő címer- és névjele az első sor jobb szélén."""
    kep = XLKep(str(PE_LOGO))
    szel = round(magassag * 529.31 / 142.17)
    kep.width, kep.height = szel, magassag
    kep.anchor = OneCellAnchor(
        _from=AnchorMarker(col=0, colOff=pixels_to_EMU(oszlop_px - szel - 12), row=0, rowOff=pixels_to_EMU(6)),
        ext=XDRPositiveSize2D(pixels_to_EMU(szel), pixels_to_EMU(magassag)))
    ws.add_image(kep)
    ws.row_dimensions[1].height = 54
    ws["A1"].alignment = Alignment(vertical="bottom")
    # nyomtatásban az útmutató egy oldal széles legyen, a logóval együtt
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0


def utmutato(wb, cim, sorok):
    """Az első lap: rövid használati útmutató, jelmagyarázat és a PE logója."""
    ws = wb.active
    ws.title = "Útmutató"
    ws["A1"] = cim
    ws["A1"].font = cim_font
    pe_logo(ws)
    ws.column_dimensions["A"].width = 110
    for i, s in enumerate(sorok, start=3):
        c = ws.cell(row=i, column=1, value=s)
        c.font = Font(name=BETU, size=10, bold=s.startswith("■"))
        c.alignment = Alignment(wrap_text=True, vertical="top")
    jel = len(sorok) + 4
    ws.cell(row=jel, column=1, value="Jelmagyarázat:").font = felkover
    c = ws.cell(row=jel + 1, column=1, value="Sárga háttér, kék betű: ide írj (bemenet)")
    c.fill, c.font = bevitel_fill, bevitel_font
    c = ws.cell(row=jel + 2, column=1, value="Halványkék háttér: képlet, ne írd felül")
    c.fill, c.font = keplet_fill, alap_font
    ws.cell(row=jel + 4, column=1, value=FORRAS).font = Font(name=BETU, size=9, italic=True, color="777777")
    return ws


def bemenet(cell, ertek=None, fmt=None):
    if ertek is not None:
        cell.value = ertek
    cell.font, cell.fill, cell.border = bevitel_font, bevitel_fill, keret
    cell.alignment = tord
    if fmt:
        cell.number_format = fmt
    return cell


def keplet(cell, kepl, fmt=None, felkov=False):
    cell.value = kepl
    cell.font = felkover if felkov else alap_font
    cell.fill, cell.border = keplet_fill, keret
    cell.alignment = Alignment(vertical="top", wrap_text=True)
    if fmt:
        cell.number_format = fmt
    return cell


def szoveg(cell, ertek, felkov=False):
    cell.value = ertek
    cell.font = felkover if felkov else alap_font
    cell.border = keret
    cell.alignment = tord
    return cell


def megjegyzes(cell, szoveg_):
    cell.comment = Comment(szoveg_, "Rendszermérnöki eszköztár")


def legordulo(ws, tartomany, ertekek, cim=None):
    dv = DataValidation(type="list", formula1='"' + ",".join(ertekek) + '"', allow_blank=True)
    if cim:
        dv.promptTitle, dv.prompt = cim, "Válassz a listából"
    ws.add_data_validation(dv)
    dv.add(tartomany)
    return dv


def tablazat(ws, kezdo_sor, fejlecek, szelessegek, sorok, bemeneti_oszlopok=(), kepletek=None,
             uressor=0, formatumok=None):
    """Általános táblázat: fejléc, adatsorok, opcionális üres bemeneti sorok.

    kepletek: dict oszlopindex(1-alapú) -> függvény(sor) -> képletszöveg
    formatumok: dict oszlopindex -> number_format
    Visszaadja az utolsó adatsor számát.
    """
    kepletek = kepletek or {}
    formatumok = formatumok or {}
    fejlec(ws, kezdo_sor, fejlecek, szelessegek)
    r = kezdo_sor
    for adat in list(sorok) + [[None] * len(fejlecek)] * uressor:
        r += 1
        for j in range(1, len(fejlecek) + 1):
            c = ws.cell(row=r, column=j)
            if j in kepletek:
                keplet(c, kepletek[j](r), formatumok.get(j))
            elif j in bemeneti_oszlopok:
                ertek = adat[j - 1] if j - 1 < len(adat) else None
                bemenet(c, ertek, formatumok.get(j))
            else:
                ertek = adat[j - 1] if j - 1 < len(adat) else None
                szoveg(c, ertek)
                if formatumok.get(j):
                    c.number_format = formatumok[j]
    return r


def diagram_kozos(ch, cim, x_cim=None, y_cim=None, szel=18, mag=9):
    ch.title = cim
    ch.style = 10
    ch.width, ch.height = szel, mag
    ch.roundedCorners = False
    if ch.legend is not None:
        ch.legend.overlay = False
    try:
        if x_cim:
            ch.x_axis.title = x_cim
        if y_cim:
            ch.y_axis.title = y_cim
        ch.x_axis.delete = False
        ch.y_axis.delete = False
    except AttributeError:
        pass
    return ch


def mentes(wb, nev):
    utvonal = MAPPA / nev
    wb.save(utvonal)
    return utvonal


__all__ = [n for n in dir() if not n.startswith("_")] + ["Reference", "BarChart", "LineChart", "ScatterChart",
                                                          "Series", "get_column_letter", "Font", "PatternFill",
                                                          "Alignment", "Border", "Side", "Comment"]
