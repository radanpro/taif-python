from database.database_manager import DatabaseManager
from services.validator import Validator
from database.SearchManager import SearchManager
from reports.ticket_exporter import TicketExporter 

class TicketService:
    def __init__(self, master):
        self.db_manager = DatabaseManager()
        self.search_manager = SearchManager()
        self.validator = Validator()
        self.master = master

    def add_ticket_data(self, data):
        columns = [
            "name", "passport_number", "from_place", "to_place", "booking_company",
            "amount", "currency", "agent", "net_amount", "trip_date", "office_name", "paid", "remaining_amount"
        ]
        data_dict = dict(zip(columns, data[1:]))

        rules = {
            "name": ["required", "min:3", "max:50"],
            "passport_number": ["required", "min:6", "max:20"],
            "from_place": ["required"],
            "to_place": ["required"],
            "booking_company": ["required", "string"],
            "amount": ["required", "numeric:2"],
            "currency": ["required"],
            "agent": ["required", "numeric:2"],
            "net_amount": ["required", "numeric:2"],
            "trip_date": ["required"],
            "office_name": ["required"],
            "paid": ["required", "numeric:2"]
        }

        if self.validator.validate(data_dict, rules):
            self.db_manager.insert("Trips", **data_dict)
            return True, "تمت إضافة البيانات بنجاح."
        else:
            errors = self.validator.get_errors()
            return False, "\n".join([f"{field}: {', '.join(errs)}" for field, errs in errors.items()])

    def calculate_net_amount(self, amount, agent):
        try:
            return float(amount) - float(agent)
        except ValueError:
            return 0.00

    def format_currency(self, currency_code):
        """
        تحويل رمز العملة المخزن في قاعدة البيانات إلى نص.
        """
        currency_map = {"1": "ر.ي", "2": "ر.س", "3": "دولار"}
        return currency_map.get(currency_code, "ر.ي")  # افتراضيًا ر.ي إذا لم يتم العثور على الرمز

    def merge_currency_with_amounts(self, row):
        """
        دمج نص العملة مع قيم الأعمدة "المبلغ"، "للوكيل"، و"الصافي".
        """
        currency_text = self.format_currency(row[7])  # تحويل رمز العملة إلى نص
        # print(row[7])
        row = list(row)
        row[6] = f"{row[6]} {currency_text}"  # المبلغ
        row[8] = f"{row[8]} {currency_text}"  # للوكيل
        row[9] = f"{row[9]} {currency_text}"  # الصافي
        return tuple(row)

    def get_all_data(self):
        """
        استرجاع البيانات من قاعدة البيانات وإزالة العمود رقم 6 (العملة) باستخدام مولد.
        """
        data = self.db_manager.select("Trips")
        updated_data = []
        for row in data:
            row = list(row)
            formatted_row = self.merge_currency_with_amounts(row)  # دمج العملة مع الأعمدة
            updated_data.append(formatted_row[:7] + formatted_row[8:])  # إزالة العمود رقم 6
        return updated_data

    def search_data(self, search_term: str):
        """
        البحث في قاعدة البيانات باستخدام مصطلح البحث.
        """
        if not search_term:
            return self.get_all_data()
        # the table "name", "passport_number", "from_place" and "to_place"
        results = self.search_manager.search("Trips", ["name", "passport_number", "from_place", "to_place", "booking_company", "amount"], search_term)
        formatted_data = []
        for row in results:
            row = list(row.values())
            formatted_row = self.merge_currency_with_amounts(row)
            yield formatted_row[:7] + formatted_row[8:]

    def export_to_excel(self):
        """
        فتح نافذة تصدير البيانات إلى Excel.
        """
        export_screen = TicketExporter(self.master)
        # print("Export to Excel - Functionality not implemented yet.")

    def save_ticket_data(self, data, master):
        success, message = self.add_ticket_data(data)
        if success:
            master.refresh_table()
        return success, message

    def update_ticket_data(self, data, master):
        """
        تحديث بيانات رحلات السفر في قاعدة البيانات.
        """
        try:
            update_data = {
                "name": data[1],
                "passport_number": data[2],
                "from_place": data[3],
                "to_place": data[4],
                "booking_company": data[5],
                "amount": data[6],
                "currency": data[7],
                "agent": data[8],
                "net_amount": data[9],
                "trip_date": data[10],
                "office_name": data[11],
                "paid": data[12],
                "remaining_amount": data[13]
            }

            # تحديث البيانات في قاعدة البيانات
            self.db_manager.update("Trips", data[0], **update_data)
            return True, "تم تحديث البيانات بنجاح!"
        except Exception as e:
            return False, f"حدث خطأ أثناء تحديث البيانات: {str(e)}"
        
    def get_by_id(self, ticket_id):
        query = self.db_manager.select("Trips", id=ticket_id)
        if query:
            return query[0]
        return None
        
    def delete_data(self, ticket_id):
        """
        حذف بيانات الرحلة من قاعدة البيانات باستخدام id.
        """
        try:
            self.db_manager.delete("Trips", id=ticket_id)
            return True, "تم حذف البيانات بنجاح!"
        except Exception as e:
            return False, f"حدث خطأ أثناء حذف البيانات: {str(e)}"