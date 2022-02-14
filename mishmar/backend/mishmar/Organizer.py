import datetime
from random import Random

from deep_translator import GoogleTranslator
from django.http import FileResponse

from .Guard import Guard
import xlsxwriter
import io
from mishmar.models import Event


class Organizer:

    def __init__(self, days, guards_in_shift, organization, officer, sat_night, users, users_settings):
        self.organized = {}
        self.days = days
        self.guards = []
        self.officer = officer
        self.notes = ""
        self.sat_night = sat_night
        self.guards_in_shift = guards_in_shift
        self.score = 0
        self.users = users
        self.users_settings = users_settings
        self.num_guards = len(users)
        self.not_recieved = {}
        self.note_pad = ["אין מספיק אנשים ביום ", "איו אחמ\"ש ביום ", "מישהו נמצא ביותר מידי ליליות"]

    def initialize_dictionaries(self):
        for i in range(14):
            self.organized["M" + str(i)] = []
            self.organized["A" + str(i)] = []
            self.organized["N" + str(i)] = []
            self.not_recieved["M" + str(i)] = []
            self.not_recieved["A" + str(i)] = []
            self.not_recieved["N" + str(i)] = []

    def reset_organizer(self):
        self.organized = {}
        self.guards = []
        self.officer = ""
        self.notes = ""
        self.sat_night = []
    
    def not_recieved_shift(self):
        for key in self.days:
            for name in self.days[key]:
                if name not in self.organized[key]:
                    self.not_recieved[key].append(name)

    def WriteToExcel(self, notes, dates, user):
        # Create a workbook and add a worksheet.
        self.not_recieved_shift()
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.right_to_left()
        user_settings = self.users_settings.filter(user=user).first()
        days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
        if user_settings.language == 'english':
            days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        maxes = {"morning": 0, "after_noon": 0, "night": 0}

        for key in self.days:
            temp = 0
            if key.count("M"):
                split = self.days[key]
                for x in range(len(split)):
                    if split[x] != "(לא משיכה)":
                        temp += 1
                if temp > maxes["morning"]:
                    maxes["morning"] = temp
            elif key.count("A"):
                split = self.days[key]
                if len(split) > maxes["after_noon"]:
                    maxes["after_noon"] = len(split)
            else:
                split = self.days[key]
                if len(split) > maxes["night"]:
                    maxes["night"] = len(split)

        maxes["morning"] += 1
        maxes["after_noon"] += 2
        maxes["night"] += 2

        # Write a total using a formula.
        title_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 24,
            'fg_color': 'white'})
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        cell_format_selected = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': "#006100",
            'bg_color': "#C6EFCE"
        })
        cell_no_pull_format = workbook.add_format({
            'font_color': "#ff0000"
        })
        border_bottom_format = workbook.add_format({
            'bottom': 5,
            'bottom_color': '#000000'
        })
        border_left_format = workbook.add_format({
            'left': 5,
            'left_color': '#000000'
        })
        border_left_bottom_format = workbook.add_format({
            'left': 5,
            'left_color': '#000000',
            'bottom': 5,
            'bottom_color': '#000000',
        })
        # Building first Structure
        col = 0
        for x in range(15):
            worksheet.write(4 + maxes["morning"], col, None, border_bottom_format)
            worksheet.write(4 + maxes["after_noon"] + maxes["morning"], col, None, border_bottom_format)
            col += 1
        row = 0
        sum_maxes = maxes["morning"] + maxes["after_noon"] + maxes["night"] + 6
        for x in range(sum_maxes):
            if x == 4 + maxes["morning"] or x == 4 + maxes["morning"] + maxes["after_noon"]:
                worksheet.write(row, 8, None, border_left_bottom_format)
            else:
                worksheet.write(row, 8, None, border_left_format)
            row += 1
        # Building second Structure
        worksheet.merge_range('A1:H2', self.translate_text('הגשות', user, "hebrew"), title_format)
        worksheet.merge_range('I1:P2', self.translate_text('הגשות', user, "hebrew"), title_format)
        worksheet.merge_range('Q1:X2', dates["day0"].strftime("%d.%m") + "-" + dates["day13"].strftime("%d.%m"),
                              title_format)
        worksheet.write(2, 0, self.translate_text("תאריך", user, "hebrew"), cell_format)
        col = 1
        for d in dates:
            worksheet.write(2, col, dates[d].strftime("%d.%m"), cell_format)
            col += 1
        worksheet.write(3, 0, self.translate_text("יום", user, "hebrew"), cell_format)
        col = 1
        for d in days:
            worksheet.write(3, col, d, cell_format)
            worksheet.write(3, col + 7, d, cell_format)
            col += 1
        worksheet.merge_range(f'A5:A{5 + maxes["morning"]}', self.translate_text('בוקר', user, "hebrew"), cell_format)
        worksheet.merge_range(
            f'A{5 + maxes["morning"] + 1}:A{5 + maxes["morning"] + maxes["after_noon"]}',
            self.translate_text('צהריים', user, "hebrew"), cell_format)
        worksheet.merge_range(
            f'A{5 + maxes["morning"] + maxes["after_noon"] + 1}:A{5 + maxes["morning"] + maxes["after_noon"] + maxes["night"]}',
            self.translate_text('לילה', user, "hebrew"), cell_format)
        worksheet.merge_range('Q4:R4', 'שם', cell_format)
        worksheet.write("S4", self.translate_text('בוקר', user, "hebrew") + " 1", cell_format)
        worksheet.write("T4", self.translate_text('בוקר', user, "hebrew") + " 2", cell_format)
        worksheet.write("U4", self.translate_text('צהריים', user, "hebrew") + " 1", cell_format)
        worksheet.write("V4", self.translate_text('צהריים', user, "hebrew") + " 2", cell_format)
        worksheet.write("W4", self.translate_text('לילה', user, "hebrew"), cell_format)
        worksheet.write("X4", self.translate_text("סופ\"ש", user, "hebrew"), cell_format)

        # Adding Data
        users = []
        row = 4
        col = 1
        for key in self.not_recieved:
            if key.count("M"):
                day = int(key.replace("M", "")) + 1
                row = 4
                for x in range(len(self.not_recieved[key])):
                    if self.not_recieved[key][x] != "(לא משיכה)":
                        if x + 1 < len(self.not_recieved[key]):
                            if self.not_recieved[key][x + 1] == "(לא משיכה)":
                                worksheet.write(row, day, self.not_recieved[key][x], cell_no_pull_format)
                            else:
                                worksheet.write(row, day, self.not_recieved[key][x])
                        else:
                            worksheet.write(row, day, self.not_recieved[key][x])
                        if self.not_recieved[key][x] not in users:
                            users.append(self.not_recieved[key][x])
                        row += 1
                for x in range(len(self.organized[key])):
                    worksheet.write(row, day, self.organized[key][x], cell_format_selected)
                    if self.organized[key][x] not in users:
                        users.append(self.organized[key][x])
                    row += 1
            elif key.count("A"):
                day = int(key.replace("A", "")) + 1
                row = 4 + maxes["morning"] + 1
                for x in range(len(self.not_recieved[key])):
                    worksheet.write(row, day, self.not_recieved[key][x])
                    if self.not_recieved[key][x] not in users:
                        users.append(self.not_recieved[key][x])
                    row += 1
                for x in range(len(self.organized[key])):
                    worksheet.write(row, day, self.organized[key][x], cell_format_selected)
                    if self.organized[key][x] not in users:
                        users.append(self.organized[key][x])
                    row += 1
            else:
                day = int(key.replace("N", "")) + 1
                row = 4 + maxes["morning"] + maxes["after_noon"] + 1
                for x in range(len(self.not_recieved[key])):
                    worksheet.write(row, day, self.not_recieved[key][x])
                    if self.not_recieved[key][x] not in users:
                        users.append(self.not_recieved[key][x])
                    row += 1
                for x in range(len(self.organized[key])):
                    worksheet.write(row, day, self.organized[key][x], cell_format_selected)
                    if self.organized[key][x] not in users:
                        users.append(self.organized[key][x])
                    row += 1

        num_rows = len(users) + 1
        col = 18
        for x in range(num_rows):
            col = 18
            if x == 0:
                worksheet.merge_range(f'Q{4 + x + 1}:R{4 + x + 1}', '', cell_format)
            else:
                worksheet.merge_range(f'Q{4 + x + 1}:R{4 + x + 1}', users[x - 1], cell_format)
            for c in range(6):
                worksheet.write(4 + x, col, "", cell_format)
                col += 1
        worksheet.merge_range(f'Q{4 + num_rows + 1}:R{4 + num_rows + 1}', self.translate_text('סה\"כ', user, "hebrew"),
                              cell_format)
        worksheet.write(f'S{4 + num_rows + 1}', f'=SUM(S5:S{4 + num_rows})', cell_format)
        worksheet.write(f'T{4 + num_rows + 1}', f'=SUM(T5:T{4 + num_rows})', cell_format)
        worksheet.write(f'U{4 + num_rows + 1}', f'=SUM(U5:U{4 + num_rows})', cell_format)
        worksheet.write(f'V{4 + num_rows + 1}', f'=SUM(V5:V{4 + num_rows})', cell_format)
        worksheet.write(f'W{4 + num_rows + 1}', f'=SUM(W5:W{4 + num_rows})', cell_format)
        worksheet.write(f'X{4 + num_rows + 1}', f'=SUM(X5:X{4 + num_rows})', cell_format)

        row = 4 + num_rows + 4

        worksheet.merge_range(f'Q{row}:X{row + 3}', self.translate_text('משמרות לאיכות', user, "hebrew"), title_format)
        worksheet.merge_range(f'Q{row + 4}:X{row + 5}', self.translate_text('שבוע ראשון', user, "hebrew"), title_format)
        worksheet.merge_range(f'Q{row + 6}:X{row + 6}', '', cell_format)
        worksheet.merge_range(f'Q{row + 7}:X{row + 7}', '', cell_format)
        worksheet.merge_range(f'Q{row + 8}:X{row + 9}', self.translate_text('שבוע שני', user, "hebrew"), title_format)
        worksheet.merge_range(f'Q{row + 10}:X{row + 10}', '', cell_format)
        worksheet.merge_range(f'Q{row + 11}:X{row + 11}', '', cell_format)

        row = row + 13
        count = 0
        for n in notes:
            if n == "general":
                worksheet.merge_range(f'Q{row + count}:X{row + count + 1}', self.translate_text('הערות', user, "hebrew"),
                                      title_format)
                count += 2
            elif n == "week1":
                worksheet.merge_range(f'Q{row + count}:X{row + count}', self.translate_text('שבוע ראשון', user, "hebrew"),
                                      title_format)
                count += 1
            else:
                worksheet.merge_range(f'Q{row + count}:X{row + count}', self.translate_text('שבוע שני', user, "hebrew"),
                                      title_format)
                count += 1
            split = notes[n].split("\n")
            if len(split) > 0:
                for s in split:
                    worksheet.merge_range(f'Q{row + count}:X{row + count}', s, cell_format)
                    count += 1

        worksheet.merge_range(f'Z4:AE5', self.translate_text('אירועים', user, "hebrew"), title_format)
        events = Event.objects.all()
        events_notes = []
        temp = ""
        for x in range(14):
            if len(events.filter(date2=dates["day" + str(x)])) > 0:
                for ev in events.filter(date2=dates["day" + str(x)]):
                    if ev.nickname != "כולם":
                        events_notes.append(
                            self.translate_text(f'בתאריך {ev.date2} יש {ev.description} ל{ev.nickname}', user, "hebrew"))
                    else:
                        events_notes.append(self.translate_text(f'בתאריך {ev.date2} יש {ev.description}', user, "hebrew"))
        row = 6
        count = 0
        for s in events_notes:
            worksheet.merge_range(f'Z{row + count}:AE{row + count}', s, cell_format)
            count += 1

        workbook.close()
        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        file_name = "suggestion" + dates["day0"].strftime("%d.%m")
        return FileResponse(buffer, as_attachment=True, filename=f'{file_name}.xlsx')
        

    def build_guards(self):
        index = 0
        for user in self.users:
            user_profile = self.users_settings.filter(user=user).first()
            self.guards[index].name = user_profile.nickname
            self.guards[index].qualityNight = user_profile.night
            self.guards[index].qualitySatNight = user_profile.sat_night
            self.guards[index].qualitySatMorning = user_profile.sat_morning
            if len(user.groups.filter(name="manager")) > 0:
                self.guards[index].authority = True
            index = index + 1

    def day_to_week(self, day):
        if day < 7:
            return 0
        else:
            return 1

    # returns who's available in each morning
    def available_morning(self, day):
        available = []
        if day == 0:
            for guard in self.guards:
                if guard.name in self.days["M" + str(day)] and \
                        guard.name not in self.sat_night and guard.name not in self.organized["M" + str(day)]\
                        and guard.name not in self.organized["A" + str(day)]:
                    if guard.weeks[self.day_to_week(day)].resMorning == -1:
                        available.append(guard)
                    elif guard.weeks[self.day_to_week(day)].resMorning != guard.weeks[self.day_to_week(day)].morning:
                        available.append(guard)
        else:
            for guard in self.guards:
                if guard.name in self.days["M" + str(day)] \
                        and guard.name not in self.organized["N" + str(day - 1)] and \
                        guard.name not in self.organized["M" + str(day)] and \
                        guard.name not in self.organized["A" + str(day)]:
                    if day == 6 or day == 13:
                        if guard.name not in self.organized["N" + str(day)]:
                            available.append(guard)
                    else:
                        if guard.weeks[self.day_to_week(day)].resMorning == -1:
                            available.append(guard)
                        elif guard.weeks[self.day_to_week(day)].resMorning != \
                                guard.weeks[self.day_to_week(day)].morning:
                            available.append(guard)
        return available

    # Chooses guard minimum shifts first if everyone is equal then random without quality
    def choose_guard_regular(self, available, day: int, shift: int):
        num_shifts = []
        r = Random()
        if shift == 0:
            for guard in available:
                num_shifts.append(int(guard.weeks[self.day_to_week(day)].morning))
        else:
            for guard in available:
                num_shifts.append(int(guard.weeks[self.day_to_week(day)].afterNoon))
        if self.array_equal(num_shifts):
            num = r.randrange(len(num_shifts))
        else:
            if not self.multiple_index(num_shifts, min(num_shifts)):
                num = num_shifts.index(min(num_shifts))
            else:
                for item in num_shifts:
                    if item != min(num_shifts):
                        num_index = num_shifts.index(item)
                        num_shifts.remove(item)
                        available.pop(num_index)
                num = r.randrange(len(num_shifts))
        return available[num]

    def multiple_index(self, array, minimum):
        num = 0
        for item in array:
            if item == minimum:
                num = num + 1
        if num > 1:
            return True
        return False

    def array_equal(self, array):
        num = array[0]
        for i in range(len(array)):
            if array[i] != num:
                return False
        return True

    def is_empty(self, array):
        for item in array:
            if item != "":
                return False
        return True

    def is_authority_in_available(self, available):
        for guard in available:
            if guard.authority:
                return True
            if guard.name == self.officer:
                return True
        return False

    def saturday(self, day):
        if day == 5 or day == 6 or day == 12 or day == 13:
            return True
        return False

    # Adds one Guard to morning shift
    def add_to_morning_shift(self, day):
        available = self.available_morning(day)
        if len(self.organized["M" + str(day)]) != 0 or not self.is_authority_in_available(available) or self.saturday(day):
            if not self.is_authority_in_available(available) and len(self.organized["M" + str(day)]) == 0 \
                    and not self.saturday(day):
                self.notes = self.notes + "אין אחמש ביום " + self.number_to_day(day) \
                             + " במשמרת בוקר " + "\n"
            if not self.is_empty(available):
                if not self.saturday(day):
                    guard = self.choose_guard_regular(available, day, 0)
                    guard.weeks[self.day_to_week(day)].morning = guard.weeks[self.day_to_week(day)].morning + 1
                else:
                    guard = self.choose_guard_quality(available, day, 1)
                    guard.qualitySatMorning = int(guard.qualitySatMorning) + 1
                    guard.weeks[self.day_to_week(day)].satMorning = guard.weeks[self.day_to_week(day)].satMorning + 1
                self.organized["M" + str(day)].append(guard.name)
            else:
                if not self.saturday(day):
                    self.notes = self.notes + "אין מספיק אנשים ביום " + \
                                 self.number_to_day(day) + "   במשמרת בוקר" + "\n"
                else:
                    self.notes = self.notes + "אין מספיק אנשים ביום " + \
                                 self.number_to_day(day) + "   במשמרת בוקר סופ\"ש" + "\n"
        else:
            if not self.is_empty(available):
                available_authority = []
                for guard in available:
                    if guard.authority:
                        available_authority.append(guard)
                if self.is_empty(available_authority):
                    for guard in available:
                        if guard.name == self.officer:
                            available_authority.append(guard)
                if self.is_empty(available_authority):
                    self.notes = self.notes + "אין אחמ\"ש ביום " + \
                                 self.number_to_day(day) + "   במשמרת בוקר" + "\n"
                    guard = self.choose_guard_regular(available, day, 0)
                else:
                    guard = self.choose_guard_regular(available_authority, day, 0)
                    if guard.name == self.officer:
                        self.notes = self.notes + self.officer + " הוא האחמ\"ש ביום " + \
                                     self.number_to_day(day) + " במשמרת בוקר" + "\n"
                guard.weeks[self.day_to_week(day)].morning = guard.weeks[self.day_to_week(day)].morning + 1
                self.organized["M" + str(day)].append(guard.name)
            else:
                self.notes = self.notes + "אין מספיק אנשים ביום " + \
                             self.number_to_day(day) + "   במשמרת בוקר" + "\n"

    def available_after_noon(self, day):
        available = []
        for guard in self.guards:
            if guard.name in self.days["A" + str(day)] and not \
                    guard.name in self.organized["A" + str(day)] and not \
                    guard.name in self.organized["M" + str(day)] and not \
                    guard.name in self.organized["N" + str(day)]:
                if guard.weeks[self.day_to_week(day)].resAfterNoon == -1:
                    available.append(guard)
                elif guard.weeks[self.day_to_week(day)].resAfterNoon != guard.weeks[self.day_to_week(day)].afterNoon:
                    available.append(guard)
        return available

    def add_to_after_noon_shift(self, day):
        available = self.available_after_noon(day)
        if not self.is_empty(available):
            guard = self.choose_guard_regular(available, day, 1)
            guard.weeks[self.day_to_week(day)].afterNoon = guard.weeks[self.day_to_week(day)].afterNoon + 1
            self.organized["A" + str(day)].append(guard.name)
        else:
            self.notes = self.notes + "אין מספיק אנשים ביום " + \
                         self.number_to_day(day) + "   במשמרת צהריים" + "\n"

    def available_night(self, day):
        available = []
        for guard in self.guards:
            if guard.name in self.days["N" + str(day)] and not \
                    guard.name in self.organized["N" + str(day)] and not guard.name in self.organized["A" + str(day)]:
                if self.saturday(day):
                    if day == 5 or day == 12:
                        if not guard.name in self.organized["N" + str(day + 1)] and not \
                                guard.name in self.organized["M" + str(day + 1)]:
                            available.append(guard)
                    else:
                        if not guard.name in self.organized["M" + str(day)]:
                            if day == 6:
                                if not guard.name in self.organized["M" + str(day + 1)]:
                                    available.append(guard)
                            else:
                                available.append(guard)
                else:
                    if not guard.name in self.organized["M" + str(day + 1)]:
                        available.append(guard)
        return available

    def array_equal_zero(self, array):
        for item in array:
            if item != 0:
                return False
        return True

    # Chooses guard based on quality and random
    def choose_guard_quality(self, available, day: int, shift: int):
        quality_shifts = []
        r = Random()
        temp_available = []
        for guard in available:
            temp_available.append(guard)
        for guard in available:
            if guard.weeks[0].get_quality(shift) > 0 or guard.weeks[1].get_quality(shift) > 0:
                available.remove(guard)
        if len(available) == 0:
            available = temp_available
        if shift == 0:
            for guard in available:
                quality_shifts.append(int(guard.qualityNight))
        elif shift == 2:
            for guard in available:
                quality_shifts.append(int(guard.qualitySatNight))
        else:
            for guard in available:
                quality_shifts.append(int(guard.qualitySatMorning))
        if self.array_equal_zero(quality_shifts):
            num = r.randrange(len(quality_shifts))
        else:
            if not self.multiple_index(quality_shifts, min(quality_shifts)):
                num = quality_shifts.index(min(quality_shifts))
            else:
                for item in quality_shifts:
                    if item != min(quality_shifts):
                        num_index = quality_shifts.index(item)
                        quality_shifts.remove(item)
                        available.pop(num_index)
                num = r.randrange(len(quality_shifts))
        return available[num]

    # Adds one Guard to night shift
    def add_to_night_shift(self, day, shift: int):
        available = self.available_night(day)
        if not self.is_empty(available):
            guard = self.choose_guard_quality(available, day, shift)
            shift_quality = int(guard.weeks[self.day_to_week(day)].get_quality(shift))
            guard.weeks[self.day_to_week(day)].set_quality(shift, shift_quality + 1)
            shift_quality = int(guard.get_quality(shift))
            guard.set_quality(shift, int(shift_quality + 1))
            self.organized["N" + str(day)].append(guard.name)
        else:
            if not self.saturday(day):
                self.notes = self.notes + "אין מספיק אנשים ביום " + \
                             self.number_to_day(day) + "   במשמרת לילה" + "\n"
            else:
                self.notes = self.notes + "אין מספיק אנשים ביום " + \
                             self.number_to_day(day) + "   במשמרת לילה סופ\"ש" + "\n"

    def number_to_day(self, day):
        st = ""
        if day == 0 or day == 7:
            st = "ראשון"
        elif day == 1 or day == 8:
            st = "שני"
        elif day == 2 or day == 9:
            st = "שלישי"
        elif day == 3 or day == 10:
            st = "רביעי"
        elif day == 4 or day == 11:
            st = "חמישי"
        elif day == 5 or day == 12:
            st = "שישי"
        elif day == 6 or day == 13:
            st = "שבת"
        if day < 7:
            st = st + " בשבוע הראשון "
        else:
            st = st + " בשבוע השני "
        return st

    def remove_from_organized(self, day: int, shift: str, name: str):
        self.organized[shift + str(day)].remove(name)

    def name_to_guard(self, name: str):
        for guard in self.guards:
            if name == guard.name:
                return guard

    def re_organize_weekend(self):
        pass

    def re_organized_night(self):
        too_much_nights = []
        min_guards = self.num_guards_in_nights()
        for guard in self.guards:
            if guard.weeks[0].night + guard.weeks[1].night > min_guards:
                too_much_nights.append(guard)
        if len(too_much_nights) == 0:
            return
        for_index = 0
        while_index = 0
        for guard in too_much_nights:
            for i in range(12):
                if guard.name in self.organized["N" + str(i)]:
                    if len(self.available_night(i)) > 0:
                        self.add_to_night_shift(i, 0)
                        self.remove_from_organized(i, "N", guard.name)
                        guard.qualityNight = guard.qualityNight - 1
                        guard.weeks[self.day_to_week(i)].night = guard.weeks[self.day_to_week(i)].night - 1
                        too_much_nights.remove(guard)
                        break
                    elif (i < 4 or i > 6) and i < 11:
                        available_switch = []
                        for guard_morning in self.organized["M" + str(i + 1)]:
                            if guard_morning in self.days["N" + str(i)]:
                                available_switch.append(self.name_to_guard(guard_morning))
                        if len(available_switch) > 0 and \
                                guard.name in self.organized["M" + str(i + 1)]:
                            switched_guard = self.choose_guard_quality(available_switch, i, 0)
                            self.remove_from_organized(i + 1, "M", switched_guard.name)
                            switched_guard.weeks[self.day_to_week(i + 1)].morning = \
                                switched_guard.weeks[self.day_to_week(i + 1)].morning - 1
                            switched_guard.qualityNight = switched_guard.qualityNight + 1
                            switched_guard.weeks[self.day_to_week(i + 1)].night = \
                                switched_guard.weeks[self.day_to_week(i + 1)].night + 1
                            self.organized["N" + str(i)].append(switched_guard.name)
                            self.remove_from_organized(i, "N", guard.name)
                            guard.qualityNight = guard.qualityNight - 1
                            guard.weeks[self.day_to_week(i)].night = guard.weeks[self.day_to_week(i)].night - 1
                            self.add_to_morning_shift(i + 1)
                            too_much_nights.remove(guard)
                            break

    def night_shift_sum(self):
        sum_shift = 0
        for i in range(12):
            if i != 5 and i != 6:
                sum_shift = sum_shift + self.guards_in_shift["N" + str(i)]
        return sum_shift

    def num_guards_in_nights(self):
        sum_shift = self.night_shift_sum()
        if sum_shift % len(self.guards) == 0:
            return sum_shift / len(self.guards)
        else:
            return sum_shift / len(self.guards) + 1

    def check_empty_shift(self):
        for i in range(14):
            if self.guards_in_shift["M" + str(i)] > 0:
                if len(self.organized["M" + str(i)]) == 0:
                    self.notes = self.notes + "אין אף אחד במשמרת בוקר ביום " + str(i + 1) + "\n"
            if self.guards_in_shift["A" + str(i)] > 0:
                if len(self.organized["A" + str(i)]) == 0:
                    self.notes = self.notes + "אין אף אחד במשמרת צהריים ביום " + str(i + 1) + "\n"
            if self.guards_in_shift["N" + str(i)] > 0:
                if len(self.organized["N" + str(i)]) == 0:
                    self.notes = self.notes + "אין אף אחד במשמרת לילה ביום " + str(i + 1) + "\n"

    def check_min_got(self):
        for guard in self.guards:
            if guard.weeks[0].served > 2 and guard.weeks[0].got < 3:
                self.notes = self.notes + guard.name + "לא קיבל מינימום בשבוע ראשון" + "\n"
            if guard.weeks[1].served > 2 and guard.weeks[1].got < 3:
                self.notes = self.notes + guard.name + "לא קיבל מינימום בשבוע שני" + "\n"

    def get_score(self):
        split_notes = self.notes.split("\n")
        for note in split_notes:
            self.score = self.score + self.score_note(note)

    def score_note(self, line):
        if line.count("  הוא האחמ\"ש ביום  ") > 0:
            return 1
        if line.count("אין מספיק אנשים ביום"):
            return 2
        if line.count("אין אחמש ביום "):
            return 4
        if line.count("חסר במשמרת לילה ביום  "):
            return 11
        if line.count("יש פחות אנשים ביום "):
            return 3
        if line.count("לא קיבל מינימום"):
            return 9
        if line.count("מישהו נמצא ביותר מידי ליליות"):
            return 12
        if line.count("חסר במשמרת בוקר"):
            return 10
        if line.count("חסר מישהו במשמרת לילה סופ\"ש "):
            return 11
        if line.count("חסר מישהו במשמרת בוקר סופ\"ש "):
            return 11
        if line.count("אין אף אחד במשמרת"):
            return 99999
        return 0

    def organize(self):
        self.initialize_dictionaries()
        for i in range(self.num_guards):
            self.guards.append(Guard())
        self.build_guards()
        startDate = datetime.date(2020, 8, 20)
        dates = []
        for i in range(14):
            dates.append(startDate + datetime.timedelta(i))
        for i in range(self.guards_in_shift["M0"]):
            self.add_to_morning_shift(0)
        for i in range(1, 14):
            for j in range(self.guards_in_shift["M" + str(i)]):
                self.add_to_morning_shift(i)
            if self.saturday(i - 1):
                for j in range(self.guards_in_shift["N" + str(i - 1)]):
                    self.add_to_night_shift(i - 1, 2)
            else:
                for j in range(self.guards_in_shift["N" + str(i - 1)]):
                    self.add_to_night_shift(i - 1, 0)
        for i in range(self.guards_in_shift["N13"]):
            self.add_to_night_shift(13, 2)
        for i in range(14):
            for j in range(self.guards_in_shift["A" + str(i)]):
                self.add_to_after_noon_shift(i)
        self.re_organized_night()
        min_guards = self.num_guards_in_nights()
        for guard in self.guards:
            if guard.weeks[0].night + guard.weeks[1].night > min_guards:
                for i in range(guard.weeks[0].night + guard.weeks[1].night):
                    self.notes = self.notes + "מישהו נמצא ביותר מידי ליליות" + "\n"
            guard.weeks[0].count_served(self.days, guard.name, 0)
            guard.weeks[0].count_got(self.organized, guard.name, 0)
            guard.weeks[1].count_served(self.days, guard.name, 1)
            guard.weeks[1].count_got(self.organized, guard.name, 1)
        self.check_min_got()
        self.check_empty_shift()
        self.get_score()

    def translate_text(self, text, user, from_language="hebrew"):
        if user.is_authenticated:
            user_settings = self.users_settings.filter(user=user).first()
            if from_language != user_settings.language:
                langs_dict = GoogleTranslator.get_supported_languages(as_dict=True)
                translator = GoogleTranslator(source='auto', target=langs_dict[user_settings.language])
                return translator.translate(text).capitalize()
        return text