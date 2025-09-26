# Jak vyrobit APK na Windows (bez Linuxu lokálně)

Máte 2 pohodlné možnosti:

## Varianta A: GitHub Actions (doporučeno – žádný Linux lokálně)
1. Nahrajte složku projektu `kivy_jirka_kara/` do svého GitHub repozitáře (jako root nebo do podadresáře).
2. Zkontrolujte, že je přiložen soubor `.github/workflows/android.yml` (je součástí ZIPu).
3. V GitHubu přejděte do **Actions** → workflow **Build Android APK (Kivy/Buildozer)** → **Run workflow**.
4. Po doběhnutí se v **Artifacts** objeví `JirkaKara-android-apk` – stáhněte `.apk`.

> Poznámka: Pokud je projekt v podadresáři, upravte v `android.yml` řádek `working-directory` na danou cestu.

## Varianta B: WSL2 (Ubuntu v rámci Windows)
1. Zapněte WSL2 a nainstalujte Ubuntu:
   - Otevřete PowerShell jako správce a spusťte:
     ```ps1
     wsl --install -d Ubuntu
     ```
   - Restartujte PC, vytvořte uživatele v Ubuntu.
2. Ve Windows připravte složku s projektem (včetně assetů: PNG/MPEG) – například `C:\JirkaKaraAndroid`.
3. Ve WSL přejděte do `/mnt/c/JirkaKaraAndroid`:
   ```bash
   cd /mnt/c/JirkaKaraAndroid
   ```
4. Nainstalujte Buildozer a závislosti:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv zip unzip openjdk-17-jdk
   python3 -m pip install --upgrade pip
   pip install buildozer cython
   ```
5. Build APK:
   ```bash
   buildozer android debug
   ```
6. APK najdete v `bin/` jako např. `JirkaKara-0.1-debug.apk`.

## Assety
Do stejné složky k `main.py` vložte soubory:
- `start_squat.png`, `start_bed.png`, `start_jail.png`
- `stranskej.png`, `goal_cil.png`
- `WhatsApp Audio 2025-09-26 at 15.13.18.mpeg`
- `fail1.mpeg`, `fail2.mpeg`, `fail3.mpeg`

## Časté problémy
- **Zvuk nehraje na některých telefonech:** převeďte `.mpeg` na `.mp3` nebo `.ogg`.
- **Buildozer stahuje SDK/NDK dlouho:** je to normální při prvním buildu.
- **Play Store (AAB):** pro publikaci do Play Store je vhodné přejít na `buildozer android release` a podepsat klíčem (`.keystore`). Rád doplním.

Šťastné buildění! 🎮
