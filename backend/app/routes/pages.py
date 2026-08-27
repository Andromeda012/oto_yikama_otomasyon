from flask import Blueprint, redirect, render_template, url_for

pages_bp = Blueprint("pages", __name__)


def render_page(template_name, nav, title, sub=None):
    return render_template(
        template_name,
        current_nav=nav,
        current_sub=sub,
        page_title=title,
    )


@pages_bp.get("/")
def dashboard():
    return render_page("dashboard.html", "dashboard", "Dashboard")


@pages_bp.get("/hesabim")
def account():
    return render_page("account.html", "account", "Hesabım")


@pages_bp.get("/ayarlar")
def settings_index():
    return redirect(url_for("pages.settings", subsection="randevu"))


@pages_bp.get("/ayarlar/<subsection>")
def settings(subsection):
    templates = {
        "randevu": ("settings/appointments.html", "Randevu Ayarları"),
        "sms": ("settings/sms.html", "SMS Ayarları"),
        "whatsapp": ("settings/whatsapp.html", "WhatsApp Ayarları"),
        "bildirim": ("settings/notifications.html", "Bildirim Ayarları"),
        "genel": ("settings/general.html", "Genel Sistem Ayarları"),
    }
    if subsection not in templates:
        return redirect(url_for("pages.settings", subsection="randevu"))
    template_name, title = templates[subsection]
    return render_page(template_name, "settings", title, sub=subsection)


@pages_bp.get("/tanimlar")
def definitions_index():
    return redirect(url_for("pages.definitions", subsection="hizmet"))


@pages_bp.get("/tanimlar/<subsection>")
def definitions(subsection):
    templates = {
        "hizmet": ("definitions/services.html", "Hizmet Tanımları"),
        "stok": ("definitions/stock.html", "Stok / Ürün Tanımları"),
        "cari": ("definitions/accounts.html", "Cari Tanımları"),
        "personel": ("definitions/staff.html", "Personel Tanımları"),
        "arac": ("definitions/vehicles.html", "Araç Tanımları"),
    }
    if subsection not in templates:
        return redirect(url_for("pages.definitions", subsection="hizmet"))
    template_name, title = templates[subsection]
    return render_page(template_name, "definitions", title, sub=subsection)


@pages_bp.get("/yonetim")
def management_index():
    return redirect(url_for("pages.management", subsection="market"))


@pages_bp.get("/yonetim/<subsection>")
def management(subsection):
    templates = {
        "market": ("management/market.html", "Market Satış"),
        "arac-takip": ("management/operations.html", "Araç / İşlem Takibi"),
        "randevu": ("management/appointments.html", "Randevu Yönetimi"),
    }
    if subsection not in templates:
        return redirect(url_for("pages.management", subsection="market"))
    template_name, title = templates[subsection]
    return render_page(template_name, "management", title, sub=subsection)


@pages_bp.get("/istatistikler")
def statistics_index():
    return redirect(url_for("pages.statistics", subsection="finansal"))


@pages_bp.get("/istatistikler/<subsection>")
def statistics(subsection):
    templates = {
        "finansal": ("statistics/financial.html", "Finansal"),
        "hizmet": ("statistics/services.html", "Hizmet Analizi"),
        "market": ("statistics/products.html", "Market / Ürün Analizi"),
        "cari": ("statistics/accounts.html", "Cari Analizi"),
        "operasyon": ("statistics/operations.html", "Operasyon Analizi"),
    }
    if subsection not in templates:
        return redirect(url_for("pages.statistics", subsection="finansal"))
    template_name, title = templates[subsection]
    return render_page(template_name, "statistics", title, sub=subsection)
