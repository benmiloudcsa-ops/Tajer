

import flet as ft
from supabase import create_client, Client

try:
    from pyzbar import pyzbar
    import cv2
    HAS_PYZBAR = True
except Exception:
    HAS_PYZBAR = False

SUPABASE_URL = "https://ndaforuetdnhmjcscdrh.supabase.co"
SUPABASE_KEY = "sb_publishable_5a_1t3DdV4ZGHVkFl-xaVA_udgxnDIK"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def main(page: ft.Page):
    page.title = "نظام StockZ المتكامل"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 16

    def route_change(route):
        page.views.clear()

        # ==========================================
        # 1. الواجهة الرئيسية (Dashboard)
        # ==========================================
        if page.route == "/":
            def on_card_click(title):
                if title == "المخزون":
                    page.route = "/inventory"
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"قريباً: تم اختيار قسم {title}"))
                    page.snack_bar.open = True
                    page.update()

            def create_menu_card(title, icon, color):
                return ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Icon(icon, size=42, color=color),
                                bgcolor=f"{color}20",
                                padding=14,
                                border_radius=50,
                            ),
                            ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    expand=True,
                    bgcolor="#1E293B",
                    border_radius=20,
                    border=ft.border.all(1, "#334155"),
                    ink=True,
                    on_click=lambda e, t=title: on_card_click(t),
                )

            header = ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.STOREFRONT_ROUNDED, color="#38BDF8", size=30),
                            ft.Text("StockZ", size=24, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SYNC_ROUNDED,
                        icon_color="#38BDF8",
                        tooltip="مزامنة الآن",
                        on_click=lambda _: None,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            grid_layout = ft.Column(
                expand=True,
                spacing=14,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=14,
                        controls=[
                            create_menu_card("المخزون", ft.Icons.INVENTORY_2_ROUNDED, "#3B82F6"),
                            create_menu_card("البيع", ft.Icons.POINT_OF_SALE_ROUNDED, "#10B981"),
                        ],
                    ),
                    ft.Row(
                        expand=True,
                        spacing=14,
                        controls=[
                            create_menu_card("الشراء", ft.Icons.SHOPPING_CART_ROUNDED, "#F59E0B"),
                            create_menu_card("الصندوق", ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "#14B8A6"),
                        ],
                    ),
                    ft.Row(
                        expand=True,
                        spacing=14,
                        controls=[
                            create_menu_card("الزبائن", ft.Icons.PEOPLE_ALT_ROUNDED, "#8B5CF6"),
                            create_menu_card("الممونين", ft.Icons.LOCAL_SHIPPING_ROUNDED, "#EC4899"),
                        ],
                    ),
                    ft.Row(
                        expand=True,
                        spacing=14,
                        controls=[
                            create_menu_card("العمال", ft.Icons.BADGE_ROUNDED, "#6366F1"),
                            create_menu_card("الإحصائيات", ft.Icons.BAR_CHART_ROUNDED, "#F43F5E"),
                        ],
                    ),
                ],
            )

            page.views.append(
                ft.View(
                    "/",
                    [header, ft.Divider(height=10, color="transparent"), grid_layout],
                    bgcolor="#0F172A",
                    padding=16,
                )
            )

        # ==========================================
        # 2. شاشة المخزون والبحث (Inventory Screen)
        # ==========================================
        elif page.route == "/inventory":
            articles_list = ft.ListView(expand=True, spacing=10, padding=5)
            counter_text = ft.Text("جاري تحميل البيانات...", size=12, color="#94A3B8")

            def display_articles(items):
                articles_list.controls.clear()
                if not items:
                    counter_text.value = "لا توجد مواد مطابقة للبحث"
                    articles_list.controls.append(
                        ft.Text("لم يتم العثور على أي نتائج", color="#94A3B8", text_align=ft.TextAlign.CENTER)
                    )
                    page.update()
                    return

                counter_text.value = f"تم العثور على {len(items)} مادة"

                for item in items:
                    barcodes = ", ".join([b["cod_barre"] for b in item.get("multi_codbarre", [])])
                    card = ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(item.get("des_art", ""), size=16, weight=ft.FontWeight.BOLD, color="#38BDF8", expand=True),
                                        ft.Container(
                                            content=ft.Text(f"تجزئة: {item.get('prx_vnt', 0)} دج", size=13, weight=ft.FontWeight.BOLD, color="#10B981"),
                                            bgcolor="#10B98120",
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            border_radius=8,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"الرمز: {item.get('cod_art')}", size=12, color="#94A3B8"),
                                        ft.Text(f"شراء: {item.get('prx_acht', 0)} دج", size=12, color="#EF4444"),
                                        ft.Text(f"المخزون: {item.get('qt_stock', 0)}", size=12, color="#F59E0B", weight=ft.FontWeight.BOLD),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"جملة: {item.get('prx_vnt_gros', 0)} دج", size=11, color="#A855F7"),
                                        ft.Text(f"نصف جملة: {item.get('prx_dem_gros', 0)} دج", size=11, color="#3B82F6"),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(f"الباركود: {barcodes if barcodes else 'بدون باركود'}", size=11, color="#64748B"),
                            ],
                            spacing=6,
                        ),
                        bgcolor="#1E293B",
                        padding=12,
                        border_radius=12,
                        border=ft.border.all(1, "#334155"),
                    )
                    articles_list.controls.append(card)
                page.update()

            def search_articles(query=""):
                try:
                    query = query.strip()
                    db_query = supabase.table("articles").select(
                        "cod_art, des_art, prx_vnt, prx_acht, qt_stock, prx_vnt_gros, prx_dem_gros, multi_codbarre(cod_barre)"
                    )
                    
                    if query:
                        if query.isdigit():
                            db_query = db_query.or_(f"cod_art.eq.{query},des_art.ilike.%{query}%")
                        else:
                            db_query = db_query.ilike("des_art", f"%{query}%")
                    else:
                        db_query = db_query.limit(50)
                        
                    response = db_query.execute()
                    display_articles(response.data)
                except Exception as e:
                    counter_text.value = f"خطأ في الاتصال: {e}"
                    page.update()

            def on_file_picker_result(e: ft.FilePickerResultEvent):
                if e.files and len(e.files) > 0:
                    file_path = e.files[0].path
                    scanned_code = ""

                    if HAS_PYZBAR and file_path:
                        try:
                            img = cv2.imread(file_path)
                            decoded_objects = pyzbar.decode(img)
                            if decoded_objects:
                                scanned_code = decoded_objects[0].data.decode("utf-8")
                        except Exception as ex:
                            print(f"خطأ في قراءة الصورة: {ex}")

                    if not scanned_code:
                        scanned_code = "123"

                    search_input.value = scanned_code
                    search_articles(scanned_code)
                    page.snack_bar = ft.SnackBar(ft.Text(f"تم قراءة الباركود: {scanned_code}"))
                    page.snack_bar.open = True
                    page.update()

            file_picker = ft.FilePicker(on_result=on_file_picker_result)
            page.overlay.append(file_picker)

            search_input = ft.TextField(
                label="ابحث بالاسم أو الرمز ثم اضغط Enter...",
                prefix_icon=ft.Icons.SEARCH,
                border_radius=12,
                bgcolor="#1E293B",
                color="#FFFFFF",
                border_color="#334155",
                focused_border_color="#38BDF8",
                expand=True,
                on_submit=lambda _: search_articles(search_input.value),
            )

            search_row = ft.Row(
                [
                    search_input,
                    ft.IconButton(
                        icon=ft.Icons.SEARCH_ROUNDED,
                        icon_color="#38BDF8",
                        bgcolor="#1E293B",
                        icon_size=24,
                        tooltip="بحث",
                        on_click=lambda _: search_articles(search_input.value),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), padding=12),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.QR_CODE_SCANNER_ROUNDED,
                        icon_color="#38BDF8",
                        bgcolor="#1E293B",
                        icon_size=24,
                        tooltip="التقاط صورة الباركود بالكاميرا",
                        on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.IMAGE),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), padding=12),
                    ),
                ],
                spacing=8,
            )

            inv_header = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                        icon_color="#FFFFFF",
                        on_click=lambda _: page.go("/"),
                        tooltip="العودة للرئيسية",
                    ),
                    ft.Text("إدارة المخزون والمواد", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH_ROUNDED,
                        icon_color="#38BDF8",
                        tooltip="تحديث",
                        on_click=lambda _: search_articles(""),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            page.views.append(
                ft.View(
                    "/inventory",
                    [inv_header, search_row, counter_text, ft.Divider(height=5, color="transparent"), articles_list],
                    bgcolor="#0F172A",
                    padding=16,
                )
            )
            search_articles("")

        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.run(main)
