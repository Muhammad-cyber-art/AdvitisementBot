import sys
from collectors.aviasales import AviasalesCollector

def main():
    print("✈️ Travel Automation Platform - Data Acquisition PoC")
    print("-" * 60)
    
    # 1. Collector initsializatsiyasi
    # Haqiqiy loyihada token .env fayldan olinadi. Hozir demo maqsadida bo'sh qoldiriladi
    # yoki sinov uchun public token bo'lsa ishlatiladi.
    aviasales_collector = AviasalesCollector(token="DEMO_TOKEN") 
    
    # 2. Qidiruv parametrlari
    from_city = "TAS"  # Toshkent
    to_city = "IST"    # Istanbul
    date = "2026-07-01"
    
    print(f"🔍 Qidiruv: {from_city} -> {to_city} | Sana: {date}")
    print(f"📡 {aviasales_collector.source_name} bo'yicha ma'lumot yig'ilmoqda...\n")
    
    # 3. Ma'lumotlarni olish
    tickets = aviasales_collector.collect(from_city=from_city, to_city=to_city, date=date)
    
    # 4. Natijani konsolga chiqarish
    if not tickets:
        print("❌ Hech qanday chipta topilmadi yoki xatolik yuz berdi.")
        print("💡 Agar token xato bo'lsa, uni Travelpayouts kabinetidan oling.")
        sys.exit(1)

    print(f"✅ Jami {len(tickets)} ta chipta topildi:\n")
    
    for idx, t in enumerate(tickets, 1):
        print(f"🎟 Ticket #{idx}")
        print(f"  Source:      {t.source}")
        print(f"  Route:       {t.from_city} -> {t.to_city}")
        print(f"  Date:        {t.departure_date.strftime('%Y-%m-%d')} to {t.arrival_date.strftime('%Y-%m-%d')}")
        print(f"  Airline:     {t.airline}")
        print(f"  Price:       {t.price} {t.currency}")
        print(f"  Booking URL: {t.booking_url}")
        print("-" * 40)

if __name__ == "__main__":
    main()
