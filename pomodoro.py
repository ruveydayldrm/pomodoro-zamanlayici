#!/usr/bin/env python3
"""Pomodoro Zamanlayıcı — terminalde 25/5 dakikalık çalışma döngüleri.

Kullanım:
    python pomodoro.py                       # 4 pomodoro: 25 dk çalışma, 5 dk mola
    python pomodoro.py --calisma 50 --mola 10 --dongu 2
    python pomodoro.py --istatistik
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

VARSAYILAN_DOSYA = Path.home() / ".pomodoro-gunluk.json"
CUBUK_GENISLIGI = 30


# --- Zamanlayıcı -------------------------------------------------------------

def sure_yaz(saniye: int) -> str:
    dakika, saniye = divmod(max(0, saniye), 60)
    return f"{dakika:02d}:{saniye:02d}"


def ilerleme(gecen: int, toplam: int, genislik: int = CUBUK_GENISLIGI) -> str:
    dolu = genislik if toplam <= 0 else min(genislik, round(genislik * gecen / toplam))
    return "█" * dolu + "░" * (genislik - dolu)


def geri_say(saniye: int, etiket: str, uyku=time.sleep, cikti=sys.stdout) -> None:
    """Aynı satırı güncelleyerek geri sayar."""
    for kalan in range(saniye, 0, -1):
        cikti.write(f"\r{etiket}  {ilerleme(saniye - kalan, saniye)}  {sure_yaz(kalan)} ")
        cikti.flush()
        uyku(1)
    cikti.write(f"\r{etiket}  {ilerleme(saniye, saniye)}  00:00 \n")
    cikti.flush()


def oturum_plani(dongu: int, calisma: int, mola: int, uzun_mola: int, aralik: int) -> list[tuple[str, int]]:
    """Süreler saniye cinsindendir. Her `aralik` pomodorodan sonra uzun mola verilir;
    son pomodorodan sonra mola eklenmez."""
    plan = []
    for i in range(1, dongu + 1):
        plan.append(("çalışma", calisma))
        if i < dongu:
            plan.append(("uzun mola", uzun_mola) if aralik and i % aralik == 0 else ("mola", mola))
    return plan


# --- Kayıt ve istatistik -----------------------------------------------------

def gunluk_oku(yol: Path) -> dict[str, int]:
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def pomodoro_kaydet(yol: Path, gun: date | None = None) -> int:
    """Günün sayacını bir artırır ve yeni değeri döner."""
    kayit = gunluk_oku(yol)
    anahtar = (gun or date.today()).isoformat()
    kayit[anahtar] = kayit.get(anahtar, 0) + 1
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_name(yol.name + ".tmp")
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(kayit, f, indent=2, sort_keys=True)
    os.replace(gecici, yol)
    return kayit[anahtar]


def istatistik(kayit: dict[str, int], bugun: date | None = None) -> dict[str, int]:
    bugun = bugun or date.today()
    son7 = sum(kayit.get((bugun - timedelta(days=i)).isoformat(), 0) for i in range(7))
    # Seri: bugünden (bugün henüz yapılmadıysa dünden) geriye kesintisiz gün sayısı
    gun = bugun if kayit.get(bugun.isoformat()) else bugun - timedelta(days=1)
    seri = 0
    while kayit.get(gun.isoformat(), 0) > 0:
        seri += 1
        gun -= timedelta(days=1)
    return {
        "bugun": kayit.get(bugun.isoformat(), 0),
        "son7": son7,
        "toplam": sum(kayit.values()),
        "seri": seri,
    }


def istatistik_yazdir(kayit: dict[str, int], bugun: date | None = None) -> None:
    bugun = bugun or date.today()
    ist = istatistik(kayit, bugun)
    print(f"Bugün: {ist['bugun']} 🍅   Son 7 gün: {ist['son7']}   Toplam: {ist['toplam']}   Seri: {ist['seri']} gün\n")
    gunler = [bugun - timedelta(days=i) for i in range(6, -1, -1)]
    en_cok = max([kayit.get(g.isoformat(), 0) for g in gunler] + [1])
    for g in gunler:
        sayi = kayit.get(g.isoformat(), 0)
        print(f"  {g:%d.%m}  {'█' * round(20 * sayi / en_cok):<20}  {sayi}")


# --- Komut satırı ------------------------------------------------------------

def dakika(metin: str) -> float:
    try:
        deger = float(metin.replace(",", "."))
    except ValueError:
        deger = 0
    if deger <= 0:
        raise argparse.ArgumentTypeError(f"Süre pozitif bir sayı olmalı: {metin}")
    return deger


def zil() -> None:
    sys.stdout.write("\a")
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pomodoro", description="Terminalde pomodoro zamanlayıcı.")
    p.add_argument("--calisma", type=dakika, default=25, help="Çalışma süresi, dakika (varsayılan: 25)")
    p.add_argument("--mola", type=dakika, default=5, help="Kısa mola, dakika (varsayılan: 5)")
    p.add_argument("--uzun-mola", type=dakika, default=15, help="Uzun mola, dakika (varsayılan: 15)")
    p.add_argument("--aralik", type=int, default=4, help="Kaç pomodoroda bir uzun mola (varsayılan: 4)")
    p.add_argument("--dongu", type=int, default=4, help="Kaç pomodoro yapılacak (varsayılan: 4)")
    p.add_argument("--istatistik", action="store_true", help="Geçmiş pomodoroları göster")
    p.add_argument("--dosya", help="Kayıt dosyası (varsayılan: ~/.pomodoro-gunluk.json)")
    args = p.parse_args(argv)

    yol = Path(args.dosya) if args.dosya else VARSAYILAN_DOSYA
    if args.istatistik:
        istatistik_yazdir(gunluk_oku(yol))
        return 0
    if args.dongu < 1:
        p.error("--dongu en az 1 olmalı.")

    sn = lambda dk: max(1, round(dk * 60))  # noqa: E731
    plan = oturum_plani(args.dongu, sn(args.calisma), sn(args.mola), sn(args.uzun_mola), args.aralik)

    tamamlanan = 0
    try:
        for tur, saniye in plan:
            if tur == "çalışma":
                geri_say(saniye, f"🍅 Pomodoro {tamamlanan + 1}/{args.dongu}")
                tamamlanan += 1
                bugun = pomodoro_kaydet(yol)
                zil()
                print(f"   Tebrikler! Bugün {bugun}. pomodoro tamamlandı.")
            else:
                geri_say(saniye, "☕ Uzun mola    " if tur == "uzun mola" else "☕ Mola         ")
                zil()
                print("   Mola bitti, hadi devam!")
    except KeyboardInterrupt:
        print(f"\n\nDurduruldu. Bu oturumda {tamamlanan} pomodoro tamamlandı.")
        return 0

    print(f"\nOturum bitti: {tamamlanan} pomodoro. İstatistik için: python pomodoro.py --istatistik")
    return 0


if __name__ == "__main__":
    sys.exit(main())
