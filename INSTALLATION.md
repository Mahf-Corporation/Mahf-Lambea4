# Mahf Firmware CPU Driver - Yükleme ve Derleme Kılavuzu

## 🚀 KÜ HIZLI BAŞLAMA

### Adım 1: Installer'ı Çalıştırın

**PowerShell Installer'ı Kullanarak:**

```powershell
# Yönetici olarak PowerShell'i açın (Windowsa başlayın ve "powershell" yazın, Ctrl+Shift+Enter tuşlarına basın)

# Proje dizinine gidin:
cd "C:\Users\[VerilenAdınız]\Desktop\Mahf-Lambea3-main"

# Installer'ı çalıştırın:
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Adım 2: Kurulum Tamamlansın

Installer şu işlemleri otomatik yapar:
- ✅ Uygulama dosyalarını kopyala
- ✅ Başlat Menüsü kısayolu oluştur
- ✅ Masaüstü kısayolu oluştur
- ✅ Registry girdileri ekle

### Adım 3: Uygulamayı Başlat

```
Başlat Menüsü → Mahf CPU Driver → Mahf CPU Driver
```

---

## 🔨 PROJE DERLEME (Geliştiriciler için)

### Ön Gereksinimler

Sisteminizde aşağıdakiler olması gerekir:

1. **Windows 10/11** x64
2. **.NET SDK 9.0+**
3. **Visual Studio Code** (isteğe bağlı)

### Kurulum Adımları

#### 1. .NET SDK'yı İndirin ve Kurun

Windows Terminali açın ve şu komutu çalıştırın:

```powershell
# [Windows Terminal'i Yönetici olarak açın]

# .NET SDK Installer scriptini indir ve çalıştır
powershell -Command "
    `$ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile 'dotnet-install.ps1' -UseBasicParsing
    .\dotnet-install.ps1 -Channel 9.0 -InstallDir 'C:\dotnet'
"

# PATH'e ekle
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';C:\dotnet', 'Machine')
refreshenv
```

#### 2. Projeyi Build Edin

```powershell
# Proje dizinine gidin
cd "C:\Users\[VerilenAdınız]\Desktop\Mahf-Lambea3-main"

# PowerShell build scriptini çalıştırın
powershell -ExecutionPolicy Bypass -File build.ps1 -InstallDotNet
```

Bu script otomatik olarak:
- ✅ Bağımlılıkları indir (restore)
- ✅ Kodu derle (build)
- ✅ Exe dosyasını oluştur (`Bin\MahfControlPanel.exe`)

#### 3. Installer Oluştur

Inno Setup yüklü ise:

```powershell
# Installer'ı derle
ISCC.exe setup.iss
```

Çıktı: `Output\MahfCPUSetup_3.0.2.exe`

---

## 📁 PROJE YAPıSı

```
Mahf-Lambea3-main (Ana Dizin)
│
├─ MahfControlPanel/          ← C# WPF Uygulaması
│  ├─ Properties/             ← Proje ayarları
│  ├─ Resources/              ← Görüntüler vb.
│  ├─ App.xaml                ← Uygulama tanımı
│  ├─ App.xaml.cs             ← Uygulama kodu
│  ├─ main.xaml               ← Ana pencere tanımı
│  ├─ mainwindow.xaml.cs      ← Ana pencere kodu
│  └─ MahfControlPanel.csproj ← C# Proje dosyası
│
├─ Bin/                       ← Yapılı Çıktı
│  └─ MahfControlPanel.exe    ← Ana Uygulaması
│
├─ Driver/                    ← Sürücü Dosyaları
│  ├─ mahf_cpu.inf           ← Sürücü Yapılandırması
│  └─ mahf_cpu.cat           ← Sürücü Sertifikası
│
├─ Output/                    ← Installer Çıktısı
│  └─ MahfCPUSetup_3.0.2.exe ← Koşu Kurulumu
│
├─ build.ps1                 ← Build Script
├─ build.bat                 ← Build Script (Batch)
├─ install.ps1               ← Installer Script
├─ install.bat               ← Installer Script (Batch)
├─ create-exe.ps1           ← Exe Oluşturma Script
├─ setup.iss                ← Inno Setup Yapılandırması
├─ CMakeLists.txt           ← CMake Yapılandırması (Opsiyonel)
│
├─ mahf_core.c              ← Kernel Driver Kodu
├─ mahf_core.h              ← Kernel Driver Header
├─ mahf_service.c           ← Servis Kodu
├─ mainwindow.xaml.cs       ← (Kopya - MahfControlPanel'de kullanılır)
├─ main.xaml                ← (Kopya - MahfControlPanel'de kullanılır)
│
├─ README.md                ← Ana Kılavuz
├─ INSTALLATION.md          ← Bu Dosya
├─ DEVELOPMENT.md           ← Geliştirici Notları
├─ LICENSE.txt              ← Lisans
├─ CHANGELOG.md             ← Değişiklik Geçmişi
│
└─ .gitignore, .clang-tidy, vb.
```

---

## 🛠️ SORUN GIDERME

### Hata: ".NET SDK not found"

**Çözüm:**
```powershell
# .NET SDK'yı manuel olarak indir
# https://aka.ms/dotnet/download

# Ya da PowerShell kurulum scriptini çalıştır:
powershell -ExecutionPolicy Bypass -File build.ps1 -InstallDotNet
```

### Hata: "Inno Setup not found"

**Çözüm:**
- Inno Setup olmadan PowerShell installer'ını kullanın
- Ya da Inno Setup'ı İndirin: https://jrsoftware.org/isdl.php

### Hata: "Access Denied"

**Çözüm:**
- PowerShell veya CMD'yi **Yönetici Olarak Çalıştır** ile açın
- Kullanıcı hesabının yazma izni olduğundan emin olun

### Hata: "Build failed"

**Çözüm:**
```powershell
# İlk olarak temizle
cd MahfControlPanel
dotnet clean
cd ..

# Sonra tekrar dene
powershell -File build.ps1
```

---

## 📝 ÖZEL AYARLAR

### Kurulum Dizinini Değiştir

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -InstallDir "D:\MyApp\MahfCPU"
```

### Kısayolları Oluşturmadan Kur

```powershell
powershell -ExecutionPolicy Bypass -File `
  install.ps1 `
  -CreateStartMenu:$false `
  -CreateDesktopShortcut:$false
```

### Sistemden Tamamen Kaldır

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall
```

---

## 🔧 GELIŞTIRICI NOTLARI

### C# Kodu Değiştirdim

1. `MahfControlPanel\` klasöründeki dosyaları düzenle
2. Build scriptini çalıştır: `powershell -File build.ps1`
3. `Bin\MahfControlPanel.exe` güncellenir

### Kernel Driver Kodu Değiştirdim

Kernel driversü derlemek için:
1. Windows Driver Kit (WDK) yüklü olmalı
2. Visual Studio + VS Tools for Xamarin
3. Sürücü imzalı olmalı (Code Signing)

Bu proje WDF kullanır - daha fazla: https://docs.microsoft.com/en-us/windows-hardware/drivers/wdf/

### Test Mode

Inno Setup olmadan test etmek için:
```powershell
# Sadece uygulamayı test et
.\Bin\MahfControlPanel.exe

# Installer'ı test et
powershell -ExecutionPolicy Bypass -File install.ps1
```

---

## 📚 DOSYA REFERENSLERI

| Dosya | Açıklama | Önerilen Editor |
|-------|----------|-----------------|
| `MahfControlPanel.csproj` | C# Proje Dosyası | VS Code / Visual Studio |
| `*.xaml` | UI Tanımı (WPF) | VS Code / Visual Studio |
| `*.cs` | C# Kaynak Kodu | VS Code / Visual Studio |
| `setup.iss` | Inno Setup Yapılandırması | Notepad / Inno Setup IDE |
| `CMakeLists.txt` | CMake Yapılandırması | Notepad / VS Code |
| `*.bat` | Batch Script | Notepad / VS Code |
| `*.ps1` | PowerShell Script | VS Code / PowerShell ISE |
| `*.md` | Markdown Dosyası | Notepad / VS Code / Typora |

---

## 🔐 GÜVENLİK NOTLARI

1. **Administrator Hakları**: Kurulum sırasında yönetici hakları gereklidir
2. **Kod İmzalama**: Sürücü imzasız - test amaçlı kullanın
3. **Sistem Yedeklemesi**: Yazmadan önce sistem yedeklemesi yapın
4. **UAC**: Windows Kullanıcı Hesabı Kontrolü onaylanmalı

---

## 📞 DESTEK

Sorularınız varsa:
- Issues: [GitHub Repository]
- Email: support@mahfcorp.com
- Website: https://www.mahfcorp.com/

---

## 📄 LİSANS

Copyright © 2024 Mahf Corporation
Tüm Hakları Saklıdır - LICENSE.txt dosyasına bakın
