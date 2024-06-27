# Pomodoro Zamanlayıcı 🍅

Terminalde çalışan, günlük pomodoro sayınızı kaydeden sade bir Pomodoro zamanlayıcısı.

```
🍅 Pomodoro 2/4  ███████████████░░░░░░░░░░░░░░░  12:31
```

## Özellikler

- Varsayılan 25 dk çalışma / 5 dk mola, her 4 pomodoroda bir 15 dk uzun mola
- Tüm süreler ve döngü sayısı ayarlanabilir
- Her bitişte terminal zili çalar
- Tamamlanan pomodorolar günlük olarak `~/.pomodoro-gunluk.json` dosyasına kaydedilir
- `--istatistik`: bugün, son 7 gün, toplam ve kaç gündür ara vermeden devam ettiğiniz (seri)
- `Ctrl+C` ile istediğiniz an durdurabilirsiniz; bitmiş pomodorolar kaybolmaz
- Ek kütüphane gerektirmez; yalnızca Python 3.9+

## Kullanım

```bash
python pomodoro.py                                   # 4 × (25 dk + 5 dk mola)
python pomodoro.py --calisma 50 --mola 10 --dongu 3
python pomodoro.py --dongu 8 --aralik 4 --uzun-mola 20
python pomodoro.py --istatistik
```

Örnek istatistik:

```
Bugün: 3 🍅   Son 7 gün: 17   Toplam: 42   Seri: 5 gün

  10.02  ████████████          3
  11.02  ████████████████████  5
  ...
```

## Testler

```bash
python -m unittest -v
```
