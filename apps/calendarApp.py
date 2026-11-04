import os
import pygame as pg
import datetime as dt
import calendar
from custom_days import CustomDaysManager

FOLDERPATH = os.path.expanduser("~/.config/hypr/calendar")

pg.init()
WIDTH, HEIGHT = 620, 420
root = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Calendar")
bgColor = (20, 20, 20)
textColor = (240, 240, 240)
dimColor = (150, 150, 150)
accentColor = (70, 130, 180)
todayColor = (50, 120, 180)
defaultEventColor = (180, 50, 50)
julianAccentColor = (180, 100, 50)

font_large = pg.font.SysFont(None, 32)
font_med = pg.font.SysFont(None, 24)
font_small = pg.font.SysFont(None, 18)

clock = pg.time.Clock()
running = True

currentDate = dt.date.today()
selectedMonth = currentDate.month
selectedYear = currentDate.year

calendar.setfirstweekday(calendar.SUNDAY)

# Initialize custom days manager using separate file
custom_days_mgr = CustomDaysManager(os.path.join(FOLDERPATH, "custom_days.json"))

def hex_to_rgb(hex_str, default=defaultEventColor):
    """Utility to convert #RRGGBB hex string to RGB tuple."""
    if not hex_str or not hex_str.startswith("#") or len(hex_str) != 7:
        return default
    try:
        return tuple(int(hex_str[i:i+2], 16) for i in (1, 3, 5))
    except ValueError:
        return default

def is_julian(year, month):
    if year < 1582:
        return True
    if year == 1582 and month < 10:
        return True
    return False

def get_julian_matrix(year, month):
    def julian_leap(y):
        return y % 4 == 0

    days_in_m = [0, 31, 29 if julian_leap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    y = year
    m = month
    if m < 3:
        m += 12
        y -= 1
    h = (1 + (13 * (m + 1)) // 5 + y + y // 4 + 5) % 7
    start_day = (h + 6) % 7

    matrix = []
    week = [0] * 7
    total_days = days_in_m[month]

    for d in range(start_day):
        week[d] = 0

    current_day_of_week = start_day
    for day in range(1, total_days + 1):
        week[current_day_of_week] = day
        current_day_of_week += 1
        if current_day_of_week > 6:
            matrix.append(week)
            week = [0] * 7
            current_day_of_week = 0

    if week != [0] * 7:
        matrix.append(week)

    return matrix

while running:
    active_event_info = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEWHEEL:
            if event.y > 0:
                selectedMonth -= 1
                if selectedMonth < 1:
                    selectedMonth = 12
                    selectedYear -= 1
            else:
                selectedMonth += 1
                if selectedMonth > 12:
                    selectedMonth = 1
                    selectedYear += 1

    root.fill(bgColor)

    use_julian = is_julian(selectedYear, selectedMonth)

    # --- Draw Top Header ---
    month_name = calendar.month_name[selectedMonth]
    header_text = f"{month_name} {selectedYear}"
    text_surface = font_large.render(header_text, True, textColor)
    root.blit(text_surface, (20, 20))

    mode_text = "(Julian Calendar)" if use_julian else ""
    mode_color = julianAccentColor if use_julian else dimColor
    mode_surface = font_small.render(mode_text, True, mode_color)
    root.blit(mode_surface, (20, 52))

    today_str = f"Today: {currentDate.strftime('%B %d, %Y')}"
    today_surface = font_med.render(today_str, True, dimColor)
    root.blit(today_surface, (WIDTH - today_surface.get_width() - 20, 25))

    # --- Draw Days of Week Header ---
    days_of_week = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    col_width = WIDTH // 7
    start_y = 90
    
    for i, day in enumerate(days_of_week):
        d_surf = font_med.render(day, True, accentColor)
        root.blit(d_surf, (i * col_width + (col_width - d_surf.get_width()) // 2, start_y))

    # --- Get Calendar Grid Dates ---
    if use_julian:
        month_matrix = get_julian_matrix(selectedYear, selectedMonth)
    else:
        month_matrix = calendar.monthcalendar(selectedYear, selectedMonth)

    row_height = 40
    start_y_grid = start_y + 35

    mouse_x, mouse_y = pg.mouse.get_pos()

    for r_idx, week in enumerate(month_matrix):
        for c_idx, day in enumerate(week):
            if day != 0:
                event_data = custom_days_mgr.get_event(selectedYear, selectedMonth, day)
                is_today = (not use_julian and 
                            selectedYear == currentDate.year and 
                            selectedMonth == currentDate.month and 
                            day == currentDate.day)
                
                cell_left = c_idx * col_width
                cell_top = start_y_grid + r_idx * row_height

                if cell_left <= mouse_x < cell_left + col_width and cell_top <= mouse_y < cell_top + row_height:
                    if event_data:
                        active_event_info = (f"{selectedYear:04d}-{selectedMonth:02d}-{day:02d}: {event_data['title']}", 
                                             hex_to_rgb(event_data.get("color")))

                color = textColor
                if event_data:
                    box_size = 28
                    box_rect = pg.Rect(cell_left + (col_width - box_size) // 2, cell_top + 4, box_size, box_size)
                    box_color = hex_to_rgb(event_data.get("color"))
                    pg.draw.rect(root, box_color, box_rect, border_radius=4)
                    color = bgColor
                elif is_today:
                    box_size = 28
                    box_rect = pg.Rect(cell_left + (col_width - box_size) // 2, cell_top + 4, box_size, box_size)
                    pg.draw.rect(root, todayColor, box_rect, border_radius=4)
                    color = bgColor

                day_surf = font_med.render(str(day), True, color)
                root.blit(day_surf, (cell_left + (col_width - day_surf.get_width()) // 2, 
                                     cell_top + 8))

    # --- Draw Footer ---
    if active_event_info:
        label_text, label_color = active_event_info
        event_surf = font_small.render(label_text, True, label_color)
        root.blit(event_surf, (20, HEIGHT - 30))
    else:
        tip_surf = font_small.render("Tip: Hover over highlighted dates to view events.", True, dimColor)
        root.blit(tip_surf, (20, HEIGHT - 30))

    pg.display.flip()
    clock.tick(30)

pg.quit()