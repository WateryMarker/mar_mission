"""MARS 2099: a small terminal mission-control game."""
import random
import sys

MISSION_DAYS = 5
COLORS = {
    "event": "1;35",
    "option": "1;36",
    "success": "1;32",
    "warning": "1;33",
    "danger": "1;31",
    "title": "1;34",
}
EVENTS = [
    ("พายุฝุ่นกำลังเข้าใกล้", "storm"),
    ("ตรวจพบน้ำแข็งใต้พื้นผิว", "ice"),
    ("มีสัญญาณเรียก Wi-Fi จากไหนไม่รู้", "signal"),
    ("เกิดแสงอาทิตย์ปะทุ", "solar"),
]


def colorize(text, color):
    if not sys.stdout.isatty():
        return text
    return f"\033[{COLORS[color]}m{text}\033[0m"


def show_banner(title, color):
    border = "=" * 52
    print("\n" + colorize(border, color))
    print(colorize(f"  {title}", color))
    print(colorize(border, color))


def show_option(number, description):
    print(f"  {colorize(f'[{number}]', 'option')} {description}")


def show_result(message, kind="success"):
    label = {
        "success": "RESULT",
        "warning": "NOTICE",
        "danger": "DANGER",
    }[kind]
    border = "-" * 52
    print("\n" + colorize(border, kind))
    print(colorize(f"  >>> {label}: {message}", kind))
    print(colorize(border, kind))


def change_resource(stats, resource, amount):
    stats[resource] = max(0, min(100, stats[resource] + amount))


def ask_choice(prompt, choices):
    while True:
        choice = input(prompt).strip()
        if choice in choices:
            return choice
        show_result(f"เลือกได้แค่ {', '.join(choices)}", "warning")


def show_status(day, stats):
    show_banner(f"MARS 2099  |  MISSION CONTROL  |  SOL {day}/{MISSION_DAYS}", "title")
    print(f"OXYGEN  [{stats['oxygen']:3}%] {'#' * (stats['oxygen'] // 10)}")
    print(f"ENERGY  [{stats['energy']:3}%] {'#' * (stats['energy'] // 10)}")
    print(f"HULL    [{stats['hull']:3}%] {'#' * (stats['hull'] // 10)}")
    print(f"ROCK SAMPLES: {stats['samples']}/3 required")
    kit = "พร้อมใช้" if stats["supply_kit"] else "ใช้ไปแล้ว"
    print(f"EMERGENCY KIT: {kit}")
    print("-" * 48)
    show_option("1", "สำรวจพื้นผิวดาว     (ใช้ O2 15, ENERGY 8)")
    show_option("2", "ซ่อมเกราะยาน        (ใช้ O2 5, ENERGY 12)")
    show_option("3", "ชาร์จแผงโซลาร์       (ใช้ O2 8, ได้ ENERGY 25)")
    show_option("4", "ใช้กล่องเสบียงฉุกเฉิน (ใช้ได้ครั้งเดียว)")


def perform_action(choice, stats):
    if choice == "1":
        if stats["oxygen"] < 15 or stats["energy"] < 8:
            show_result("ทรัพยากรไม่พอออกสำรวจ ลองเลือกแผนอื่น", "warning")
            return False
        stats["oxygen"] -= 15
        stats["energy"] -= 8
        found = random.randint(1, 2)
        stats["samples"] += found
        show_result(f"เก็บตัวอย่างหินได้ {found} ชิ้น ภารกิจวิทยาศาสตร์คืบหน้า!")
    elif choice == "2":
        if stats["oxygen"] < 5 or stats["energy"] < 12:
            show_result("ทรัพยากรไม่พอซ่อมยาน ลองเลือกแผนอื่น", "warning")
            return False
        stats["oxygen"] -= 5
        stats["energy"] -= 12
        stats["hull"] = min(100, stats["hull"] + 22)
        show_result("ซ่อมเกราะยานเรียบร้อย วิศวกรบนโลกส่งอีโมจิปรบมือมาให้")
    elif choice == "3":
        if stats["oxygen"] < 8:
            show_result("ออกซิเจนไม่พอเปิดระบบชาร์จ ลองเลือกแผนอื่น", "warning")
            return False
        stats["oxygen"] -= 8
        stats["energy"] = min(100, stats["energy"] + 25)
        show_result("ชาร์จพลังงานจากแสงอาทิตย์สำเร็จ แดดบนดาวอังคารก็มีประโยชน์")
    else:
        if not stats["supply_kit"]:
            show_result("กล่องเสบียงถูกใช้ไปแล้ว เก็บไว้ในความทรงจำแทนละกัน", "warning")
            return False
        stats["supply_kit"] = False
        change_resource(stats, "oxygen", 20)
        change_resource(stats, "energy", 20)
        show_result("เปิดกล่องเสบียงฉุกเฉิน! เจอออกซิเจนกับแบตเตอรี่ และลูกอมเก่า 1 เม็ด")

    return True


def trigger_event(stats):
    message, event = random.choice(EVENTS)
    show_banner("RANDOM EVENT DETECTED", "event")
    print(colorize(f"  !! {message}", "event"))
    if event == "storm":
        show_option("1", "หลบในหลุมอุกกาบาต (ใช้ O2 5)")
        show_option("2", "ขับฝ่าพายุ (เกราะยานลด 12 แต่ได้ตัวอย่าง 1 ชิ้น)")
        choice = ask_choice("  เลือกทางรับมือ [1/2]: ", ("1", "2"))
        if choice == "1":
            change_resource(stats, "oxygen", -5)
            show_result("หลบพ้นพายุได้ ยานยังอยู่ครบ")
        else:
            change_resource(stats, "hull", -12)
            stats["samples"] += 1
            show_result("ฝ่าพายุสำเร็จ ได้หินมา 1 ชิ้น แต่ยานมีรอยบุบ", "warning")
    elif event == "ice":
        show_option("1", "เก็บน้ำแข็งอย่างระวัง (ใช้ ENERGY 6, ได้ O2 12 และหิน 1 ชิ้น)")
        show_option("2", "เจาะเต็มกำลัง (ใช้ ENERGY 10, ได้ O2 20 แต่เกราะลด 8)")
        choice = ask_choice("  เลือกทางรับมือ [1/2]: ", ("1", "2"))
        if choice == "1":
            change_resource(stats, "energy", -6)
            change_resource(stats, "oxygen", 12)
            stats["samples"] += 1
            show_result("เก็บตัวอย่างน้ำแข็งสำเร็จ นักวิทยาศาสตร์ส่งสติกเกอร์ดาวมาให้")
        else:
            change_resource(stats, "energy", -10)
            change_resource(stats, "oxygen", 20)
            change_resource(stats, "hull", -8)
            show_result("เจาะได้น้ำแข็งเยอะ แต่เครื่องเจาะไปทักทายเกราะยาน", "warning")
    elif event == "signal":
        show_option("1", "ตอบกลับด้วยรหัส Wi-Fi: 12345678 (ได้ ENERGY 12)")
        show_option("2", "ไม่ตอบ ป้องกันข้อมูลส่วนตัว")
        choice = ask_choice("  เลือกทางรับมือ [1/2]: ", ("1", "2"))
        if choice == "1":
            change_resource(stats, "energy", 12)
            show_result("มีคนส่งแบตสำรองมาให้ พร้อมข้อความว่า 'รหัสนี้เดาง่ายมาก'")
        else:
            show_result("ปิดสัญญาณเรียบร้อย ความเป็นส่วนตัวปลอดภัย", "warning")
    else:
        show_option("1", "หันแผงโซลาร์รับแสง (ได้ ENERGY 15)")
        show_option("2", "เปิดเกราะป้องกัน (ใช้ ENERGY 8, ได้ HULL 10)")
        choice = ask_choice("  เลือกทางรับมือ [1/2]: ", ("1", "2"))
        if choice == "1":
            change_resource(stats, "energy", 15)
            show_result("แผงโซลาร์ชาร์จเต็ม แดดแรงจนคิดถึงครีมกันแดด")
        else:
            change_resource(stats, "energy", -8)
            change_resource(stats, "hull", 10)
            show_result("เกราะรับพลังงานไว้ได้ ยานปลอดภัยและดูเงางามขึ้น")


def finish_mission(stats, failed=False):
    score = stats["samples"] * 20
    score += (stats["oxygen"] + stats["energy"] + stats["hull"]) // 3

    show_banner("MISSION DEBRIEF", "title")
    if failed:
        rank = "F"
        show_result("MISSION FAILED: ระบบยานขัดข้อง ติดต่อโลกไม่ได้", "danger")
    elif stats["samples"] >= 3:
        rank = "S" if score >= 110 else "A" if score >= 85 else "B"
        show_result("MISSION COMPLETE: ภารกิจสำเร็จ!")
        print("นักวิทยาศาสตร์บนโลกดีใจมาก ส่วนคุณได้กลับบ้านไปนอน")
    else:
        rank = "C" if score >= 60 else "D"
        show_result("MISSION INCOMPLETE: กลับโลกได้ แต่ลืมเก็บตัวอย่างหิน", "warning")
        print("นักวิทยาศาสตร์ฝากถามว่า... ออกไปทำอะไรตั้ง 5 sols?")

    rank_messages = {
        "S": "ตำนานแห่งดาวอังคาร! NASA ขอจองตัวแล้ว",
        "A": "นักบินมือโปร ยานมีรอยนิดหน่อยแต่กลับบ้านได้",
        "B": "ภารกิจผ่านแบบเฉียดฉิว กรุณาอย่าบอกฝ่ายบัญชี",
        "C": "รอดกลับมาได้ แต่ฝ่ายวิทยาศาสตร์ยังงง",
        "D": "ทริปนี้ได้ประสบการณ์กลับมาแทนตัวอย่างหิน",
        "F": "ได้เป็นข่าวดังบนโลก แต่ไม่ใช่ข่าวที่อยากเป็น",
    }
    print(f"\n{colorize(f' SCORE: {score}  |  RANK: {rank} ', 'title')}")
    result_kind = "success" if rank in ("S", "A") else "danger" if rank == "F" else "warning"
    show_result(rank_messages[rank], result_kind)
    print(f"ตัวอย่างหินที่เก็บได้: {stats['samples']}")


def main():
    stats = {
        "oxygen": 80,
        "energy": 60,
        "hull": 70,
        "samples": 0,
        "supply_kit": True,
    }
    print("เชื่อมต่อศูนย์ควบคุมโลก... สำเร็จ")
    print("ภารกิจ: อยู่รอด 5 sols และเก็บตัวอย่างหินอย่างน้อย 3 ชิ้น")

    day = 1
    while day <= MISSION_DAYS:
        show_status(day, stats)
        if stats["oxygen"] < 5 and not stats["supply_kit"]:
            show_result("ออกซิเจนไม่พอสำหรับปฏิบัติการใดๆ และไม่มีกล่องเสบียงเหลือแล้ว", "danger")
            finish_mission(stats, failed=True)
            return
        choice = input("เลือกคำสั่ง 1-4: ").strip()
        if choice not in ("1", "2", "3", "4"):
            show_result("ไม่พบคำสั่งนี้ กรุณาเลือก 1, 2, 3 หรือ 4", "warning")
            continue
        if not perform_action(choice, stats):
            continue

        trigger_event(stats)
        if min(stats["oxygen"], stats["energy"], stats["hull"]) <= 0:
            finish_mission(stats, failed=True)
            return
        day += 1

    finish_mission(stats)


if __name__ == "__main__":
    main()
