import tkinter as tk
from tkinter import ttk, messagebox
from ui.adds.add_umrah_screen import AddUmrahScreen
from ui.edits.edit_umrah_screen import EditUmrahScreen
from services.umrah_service import UmrahService

class UmrahScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master
        self.service = UmrahService(self)  # إنشاء كائن من UmrahService

        # جعل الإطار الرئيسي يتكيف مع حجم النافذة
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # إطار الجزء العلوي (الأزرار وشريط البحث)
        self.top_frame = tk.Frame(self, bg="white")
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=10)

        # جعل أعمدة top_frame تتكيف مع العرض
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=1)
        self.top_frame.grid_columnconfigure(3, weight=1)

        # إنشاء الأزرار والجدول
        self.create_buttons()
        self.create_table_section()

        # واجهة الإضافة (مخفية في البداية)
        self.add_umrah_screen = AddUmrahScreen(self, self.show_main_screen, self.service)
        self.add_umrah_screen.grid(row=1, column=0, sticky="nsew")
        self.add_umrah_screen.grid_remove()

        # واجهة التعديل (سيتم إنشاؤها لاحقًا)
        self.edit_umrah_screen = None

    def create_buttons(self):
        """إنشاء الأزرار وشريط البحث."""
        # زر البحث
        self.search_label = tk.Label(self.top_frame, text="بحث:", font=("Arial", 12), bg="white")
        self.search_label.grid(row=0, column=0, padx=(0, 5), sticky="w")

        # حقل البحث
        self.search_entry = tk.Entry(
            self.top_frame,
            font=("Arial", 12),
            width=30,
            highlightbackground="cyan",  # لون الحواف الخارجية
            highlightthickness=2,       # سماكة الحواف
            relief=tk.FLAT              # إزالة الحواف الداخلية
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)  # ربط حقل البحث بدالة البحث

        # أزرار التعديل والحذف (مخفية بشكل افتراضي)
        self.edit_button = tk.Button(self.top_frame, text="تعديل", bg="blue", fg="white", font=("Arial", 12), width=20, command=self.edit_row)
        self.edit_button.grid(row=0, column=2, padx=10, sticky="e")
        self.edit_button.grid_remove()  # إخفاء الزر

        self.delete_button = tk.Button(self.top_frame, text="حذف", bg="red", fg="white", font=("Arial", 12), width=20, command=self.delete_row)
        self.delete_button.grid(row=0, column=3, padx=10, sticky="e")
        self.delete_button.grid_remove()  # إخفاء الزر

        # زر إضافة جديد
        self.add_button = tk.Button(self.top_frame, text="إضافة معتمر جديد", bg="blue", fg="white", font=("Arial", 12), width=20, command=self.show_add_screen)
        self.add_button.grid(row=0, column=4, padx=(20, 10), sticky="e")

        # زر تصدير إلى Excel
        self.export_excel_button = tk.Button(self.top_frame, text="تصدير إلى Excel", bg="green", fg="white", font=("Arial", 12), width=20, command=self.service.export_to_excel)
        self.export_excel_button.grid(row=0, column=5, padx=(10, 20), sticky="e")

    def create_table_section(self):
        """إنشاء الجدول لعرض البيانات."""
        table_frame = tk.Frame(self, bg="white")
        table_frame.grid(row=1, column=0, sticky="nsew")

        # جعل الجدول يتكيف مع حجم النافذة
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # شريط التمرير
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)

        # الجدول
        self.table = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Passport Number", "Phone Number", "Sponsor Name", "Sponsor Number", "Cost", "Paid", "Remaining", "Entry Date", "Exit Date", "Status", "Days Left"),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
            show="headings"
        )

        # تكوين شريط التمرير
        scroll_x.config(command=self.table.xview)
        scroll_y.config(command=self.table.yview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # تعريف الأعمدة
        self.table.heading("ID", text="ID")
        self.table.heading("Name", text="اسم المعتمر")
        self.table.heading("Passport Number", text="رقم الجواز")
        self.table.heading("Phone Number", text="رقم الهاتف")
        self.table.heading("Sponsor Name", text="اسم الضمين")
        self.table.heading("Sponsor Number", text="رقم الضمين")
        self.table.heading("Cost", text="التكلفة")
        self.table.heading("Paid", text="الواصل")
        self.table.heading("Remaining", text="الباقي")
        self.table.heading("Entry Date", text="تاريخ الدخول")
        self.table.heading("Exit Date", text="تاريخ الخروج")
        self.table.heading("Status", text="الحالة")
        self.table.heading("Days Left", text="عدد الأيام المتبقية")

        # عرض الجدول
        self.table.pack(fill=tk.BOTH, expand=True)

        # تحميل البيانات
        self.populate_table()

        # ربط حدث النقر على صف في الجدول
        self.table.bind("<ButtonRelease-1>", self.show_buttons)

    def populate_table(self, data=None):
        """تعبئة الجدول بالبيانات."""
        self.table.delete(*self.table.get_children())  # مسح الجدول الحالي
        data = data if data is not None else self.service.get_all_data()
        for index, item in enumerate(data):
            if index % 2 == 0:
                self.table.insert("", tk.END, values=item, tags=("evenrow",))  # صف زوجي
            else:
                self.table.insert("", tk.END, values=item, tags=("oddrow",))  # صف فردي

    def show_buttons(self, event=None):
        """عرض أزرار التعديل والحذف عند النقر على صف."""
        selected_item = self.table.selection()
        if selected_item:
            self.edit_button.grid(row=0, column=2, padx=10, sticky="e")  # عرض زر التعديل
            self.delete_button.grid(row=0, column=3, padx=10, sticky="e")  # عرض زر الحذف
        else:
            self.edit_button.grid_remove()  # إخفاء زر التعديل
            self.delete_button.grid_remove()  # إخفاء زر الحذف

    def edit_row(self):
        """عرض واجهة التعديل عند النقر على زر التعديل."""
        selected_item = self.table.selection()
        if selected_item:
            # جلب id الصف المحدد
            item_id = self.table.item(selected_item, "values")[0]

            # البحث في قاعدة البيانات باستخدام id
            data = self.service.get_umrah_by_id(item_id)

            if data:
                # فتح واجهة التعديل مع البيانات المستردة
                self.edit_umrah_screen = EditUmrahScreen(self, self.show_main_screen, self.service, data)
                self.edit_umrah_screen.grid(row=1, column=0, sticky="nsew")
                self.table.master.grid_remove()
                self.hide_buttons_and_search()
            else:
                messagebox.showerror("خطأ", "لم يتم العثور على البيانات!")

    def delete_row(self):
        """دالة الحذف."""
        selected_item = self.table.selection()
        if selected_item:
            item_values = self.table.item(selected_item, "values")
            item_id = item_values[0]
            person_name = item_values[1]

            # حذف البيانات من قاعدة البيانات
            confirm = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف البيانات للمعتمر: {person_name}?")
            if confirm:
                success, message = self.service.delete_umrah_data(item_id)
                if success:
                    self.table.delete(selected_item)
                    messagebox.showinfo("نجاح", "تم حذف البيانات بنجاح!")
                else:
                    messagebox.showerror("خطأ", message)

    def on_search(self, event=None):
        """البحث عند تغيير نص حقل البحث."""
        search_term = self.search_entry.get().strip()
        if search_term:
            results = self.service.search_data(search_term)
        else:
            results = self.service.get_all_data()
        self.populate_table(results)

    def show_add_screen(self):
        """عرض واجهة الإضافة."""
        self.table.master.grid_remove()
        self.add_umrah_screen.grid()
        self.hide_buttons_and_search()

    def show_main_screen(self):
        """عرض الشاشة الرئيسية."""
        if self.add_umrah_screen:
            self.add_umrah_screen.grid_remove()
        if self.edit_umrah_screen:
            self.edit_umrah_screen.grid_remove()
        self.table.master.grid()
        self.show_buttons_and_search()
        self.populate_table()

    def hide_buttons_and_search(self):
        """إخفاء الأزرار وشريط البحث."""
        self.export_excel_button.grid_remove()
        self.add_button.grid_remove()
        self.search_label.grid_remove()
        self.search_entry.grid_remove()
        self.edit_button.grid_remove()  # إخفاء زر التعديل
        self.delete_button.grid_remove()  # إخفاء زر الحذف

    def show_buttons_and_search(self):
        """إعادة عرض الأزرار وشريط البحث."""
        self.search_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.search_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.export_excel_button.grid(row=0, column=5, padx=(10, 20), sticky="e")
        self.add_button.grid(row=0, column=4, padx=(20, 10), sticky="e")

        # إعادة عرض أزرار التعديل والحذف إذا تم تحديد صف
        selected_item = self.table.selection()
        if selected_item:
            self.edit_button.grid(row=0, column=2, padx=10, sticky="e")  # عرض زر التعديل
            self.delete_button.grid(row=0, column=3, padx=10, sticky="e")  # عرض زر الحذف