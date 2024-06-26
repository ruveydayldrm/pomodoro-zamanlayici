import io
import tempfile
import unittest
from datetime import date
from pathlib import Path

import pomodoro


class ZamanlayiciTesti(unittest.TestCase):
    def test_sure_yaz(self):
        self.assertEqual(pomodoro.sure_yaz(1500), "25:00")
        self.assertEqual(pomodoro.sure_yaz(65), "01:05")
        self.assertEqual(pomodoro.sure_yaz(-3), "00:00")

    def test_ilerleme(self):
        self.assertEqual(pomodoro.ilerleme(0, 10, 4), "░░░░")
        self.assertEqual(pomodoro.ilerleme(5, 10, 4), "██░░")
        self.assertEqual(pomodoro.ilerleme(10, 10, 4), "████")

    def test_geri_say_her_saniye_bekler(self):
        beklemeler = []
        cikti = io.StringIO()
        pomodoro.geri_say(3, "Test", uyku=beklemeler.append, cikti=cikti)
        self.assertEqual(beklemeler, [1, 1, 1])
        self.assertIn("00:03", cikti.getvalue())
        self.assertTrue(cikti.getvalue().endswith("00:00 \n"))

    def test_oturum_plani(self):
        plan = pomodoro.oturum_plani(dongu=5, calisma=25, mola=5, uzun_mola=15, aralik=2)
        self.assertEqual([t for t, _ in plan], [
            "çalışma", "mola", "çalışma", "uzun mola", "çalışma", "mola", "çalışma", "uzun mola", "çalışma",
        ])
        self.assertEqual(plan[3], ("uzun mola", 15))

    def test_tek_pomodoroda_mola_yok(self):
        self.assertEqual(pomodoro.oturum_plani(1, 25, 5, 15, 4), [("çalışma", 25)])


class KayitTesti(unittest.TestCase):
    def setUp(self):
        self._gecici = tempfile.TemporaryDirectory()
        self.yol = Path(self._gecici.name) / "gunluk.json"

    def tearDown(self):
        self._gecici.cleanup()

    def test_kaydet_ve_oku(self):
        self.assertEqual(pomodoro.pomodoro_kaydet(self.yol, date(2024, 2, 10)), 1)
        self.assertEqual(pomodoro.pomodoro_kaydet(self.yol, date(2024, 2, 10)), 2)
        self.assertEqual(pomodoro.gunluk_oku(self.yol), {"2024-02-10": 2})

    def test_bozuk_dosya_bos_sayilir(self):
        self.yol.write_text("{bozuk", encoding="utf-8")
        self.assertEqual(pomodoro.gunluk_oku(self.yol), {})

    def test_istatistik_ve_seri(self):
        kayit = {"2024-02-10": 2, "2024-02-11": 4, "2024-02-12": 1, "2024-02-01": 3}
        ist = pomodoro.istatistik(kayit, date(2024, 2, 12))
        self.assertEqual(ist, {"bugun": 1, "son7": 7, "toplam": 10, "seri": 3})

    def test_bugun_yapilmadiysa_seri_dunden_sayilir(self):
        kayit = {"2024-02-10": 1, "2024-02-11": 1}
        self.assertEqual(pomodoro.istatistik(kayit, date(2024, 2, 12))["seri"], 2)
        self.assertEqual(pomodoro.istatistik(kayit, date(2024, 2, 13))["seri"], 0)


if __name__ == "__main__":
    unittest.main()
